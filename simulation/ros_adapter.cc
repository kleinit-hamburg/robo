#include <gz/sim/System.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/Joint.hh>
#include <gz/sim/Link.hh>
#include <geometry_msgs/msg/wrench_stamped.hpp>
#include <mutex>
#include <cmath>
#include <gz/sim/Util.hh>
#include <gz/sim/components/Name.hh>
#include <gz/sim/components/Collision.hh>
#include <gz/plugin/Register.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/twist.pb.h>
#include <gz/msgs/joint_trajectory.pb.h>
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <trajectory_msgs/msg/joint_trajectory.hpp>
#include <sensor_msgs/msg/imu.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <rosgraph_msgs/msg/clock.hpp>
#include <tf2_msgs/msg/tf_message.hpp>
#include <thread>
#include <std_msgs/msg/string.hpp>
#include "plant_fixture.hh"

namespace garden {
class RosAdapter: public gz::sim::System,
                  public gz::sim::ISystemConfigure,
                  public gz::sim::ISystemPostUpdate,
                  public gz::sim::ISystemPreUpdate {
  PlantFixture plant;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr plantState;
  gz::sim::Model model;
  gz::sim::Entity tool{gz::sim::kNullEntity};
  std::mutex loadMutex;
  gz::math::Vector3d requestedLoad{0,0,0}, appliedLoad{0,0,0};
  std::chrono::steady_clock::time_point loadAt{};
  rclcpp::Subscription<geometry_msgs::msg::WrenchStamped>::SharedPtr loadCommand;
  rclcpp::Publisher<geometry_msgs::msg::WrenchStamped>::SharedPtr loadState;
  std::vector<gz::sim::Entity> joints, links;
  gz::transport::Node transport;
  gz::transport::Node::Publisher velocity, trajectory;
  rclcpp::Node::SharedPtr node;
  std::unique_ptr<rclcpp::executors::SingleThreadedExecutor> executor;
  std::thread thread;
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr command;
  rclcpp::Subscription<trajectory_msgs::msg::JointTrajectory>::SharedPtr arm;
  rclcpp::Publisher<rosgraph_msgs::msg::Clock>::SharedPtr clock;
  rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr state;
  rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr imu;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odometry;
  double odomX=0,odomY=0,odomYaw=0;
  rclcpp::Publisher<tf2_msgs::msg::TFMessage>::SharedPtr poses;
  std::chrono::steady_clock::duration last{};
 public:
  ~RosAdapter() override {
    if(executor) executor->cancel();
    if(thread.joinable()) thread.join();
    if(node) executor->remove_node(node);
    if(rclcpp::ok()) rclcpp::shutdown();
  }
  void Configure(const gz::sim::Entity &entity,
      const std::shared_ptr<const sdf::Element> &,
      gz::sim::EntityComponentManager &ecm,gz::sim::EventManager &) override {
    model=gz::sim::Model(entity);
    joints=model.Joints(ecm);links=model.Links(ecm);tool=model.LinkByName(ecm,"arm_wrist_link");
    for(auto id:joints){gz::sim::Joint(id).EnablePositionCheck(ecm);gz::sim::Joint(id).EnableVelocityCheck(ecm);}
    rclcpp::init(0,nullptr);
    node=std::make_shared<rclcpp::Node>("garden_sim_adapter");
    velocity=transport.Advertise<gz::msgs::Twist>("/garden/cmd_vel");
    trajectory=transport.Advertise<gz::msgs::JointTrajectory>("/garden/arm/trajectory");
    command=node->create_subscription<geometry_msgs::msg::Twist>("/garden/cmd_vel",10,[this](geometry_msgs::msg::Twist::ConstSharedPtr msg){
      gz::msgs::Twist out;out.mutable_linear()->set_x(msg->linear.x);out.mutable_angular()->set_z(msg->angular.z);velocity.Publish(out);
    });
    arm=node->create_subscription<trajectory_msgs::msg::JointTrajectory>("/garden/arm/trajectory",10,[this](trajectory_msgs::msg::JointTrajectory::ConstSharedPtr msg){
      gz::msgs::JointTrajectory out;
      for(const auto &name:msg->joint_names)out.add_joint_names(name);
      for(const auto &pt:msg->points){auto p=out.add_points();for(auto v:pt.positions)p->add_positions(v);p->mutable_time_from_start()->set_sec(pt.time_from_start.sec);p->mutable_time_from_start()->set_nsec(pt.time_from_start.nanosec);}
      trajectory.Publish(out);
    });
    loadCommand=node->create_subscription<geometry_msgs::msg::WrenchStamped>("/garden/tool/wrench",10,[this](geometry_msgs::msg::WrenchStamped::ConstSharedPtr msg){
      auto f=msg->wrench.force;auto t=msg->wrench.torque;
      if(msg->header.frame_id!="world"||!std::isfinite(f.x)||!std::isfinite(f.y)||!std::isfinite(f.z)||std::hypot(f.x,f.y,f.z)>1000.001||t.x!=0||t.y!=0||t.z!=0)return;
      std::lock_guard<std::mutex> lock(loadMutex);requestedLoad.Set(f.x,f.y,f.z);loadAt=std::chrono::steady_clock::now();
    });
    auto qos=rclcpp::SensorDataQoS();
    plantState=node->create_publisher<std_msgs::msg::String>("/garden/plant/state",qos);
    loadState=node->create_publisher<geometry_msgs::msg::WrenchStamped>("/garden/tool/applied_wrench",qos);
    clock=node->create_publisher<rosgraph_msgs::msg::Clock>("/clock",qos);
    state=node->create_publisher<sensor_msgs::msg::JointState>("/garden/joint_states",qos);
    odometry=node->create_publisher<nav_msgs::msg::Odometry>("/garden/odom",qos);
    imu=node->create_publisher<sensor_msgs::msg::Imu>("/garden/imu",qos);
    poses=node->create_publisher<tf2_msgs::msg::TFMessage>("/model/robot/pose",qos);
    executor=std::make_unique<rclcpp::executors::SingleThreadedExecutor>();
    executor->add_node(node);thread=std::thread([this]{executor->spin();});
  }
  void PreUpdate(const gz::sim::UpdateInfo &info,gz::sim::EntityComponentManager &ecm) override {
    appliedLoad.Set(0,0,0);
    if(info.paused)return;
    plant.Update(ecm);
    if(tool==gz::sim::kNullEntity)return;
    {std::lock_guard<std::mutex> lock(loadMutex);if(std::chrono::steady_clock::now()-loadAt<std::chrono::milliseconds(250))appliedLoad=requestedLoad;}
    gz::sim::Link(tool).AddWorldWrench(ecm,appliedLoad,gz::math::Vector3d::Zero,gz::math::Vector3d(0,0,.08));
  }
  void PostUpdate(const gz::sim::UpdateInfo &info,const gz::sim::EntityComponentManager &ecm) override {
    if(info.paused||info.simTime-last<std::chrono::milliseconds(20))return;
    double dt=std::chrono::duration<double>(info.simTime-last).count();
    last=info.simTime;
    auto ns=std::chrono::duration_cast<std::chrono::nanoseconds>(info.simTime).count();
    builtin_interfaces::msg::Time stamp;stamp.sec=ns/1000000000;stamp.nanosec=ns%1000000000;
    geometry_msgs::msg::WrenchStamped w;w.header.stamp=stamp;w.header.frame_id="world";w.wrench.force.x=appliedLoad.X();w.wrench.force.y=appliedLoad.Y();w.wrench.force.z=appliedLoad.Z();loadState->publish(w);
    rosgraph_msgs::msg::Clock c;c.clock=stamp;clock->publish(c);
    std::optional<double> leftSpeed,rightSpeed;
    sensor_msgs::msg::JointState j;j.header.stamp=stamp;
    for(auto id:joints){gz::sim::Joint joint(id);auto p=joint.Position(ecm),v=joint.Velocity(ecm);if(!p||!v||p->empty()||v->empty())continue;j.name.push_back(joint.Name(ecm).value_or(""));j.position.push_back(p->front());j.velocity.push_back(v->front());if(j.name.back()=="left_joint")leftSpeed=v->front();if(j.name.back()=="right_joint")rightSpeed=v->front();}
    state->publish(j);
    if(leftSpeed&&rightSpeed){
      const double speed=(*leftSpeed+*rightSpeed)*.12/2,omega=(*rightSpeed-*leftSpeed)*.12/.52;
      odomX+=speed*std::cos(odomYaw+omega*dt/2)*dt;odomY+=speed*std::sin(odomYaw+omega*dt/2)*dt;odomYaw+=omega*dt;
      nav_msgs::msg::Odometry o;o.header.stamp=stamp;o.header.frame_id="odom";o.child_frame_id="robot/base_link";
      o.pose.pose.position.x=odomX;o.pose.pose.position.y=odomY;o.pose.pose.orientation.z=std::sin(odomYaw/2);o.pose.pose.orientation.w=std::cos(odomYaw/2);
      o.twist.twist.linear.x=speed;o.twist.twist.angular.z=omega;odometry->publish(o);
    }
    bool groundContact=false;
    auto ground=ecm.EntityByComponents(gz::sim::components::Model(),gz::sim::components::Name("ground"));
    auto groundLink=gz::sim::Model(ground).LinkByName(ecm,"link");
    auto groundCollision=ecm.EntityByComponents(gz::sim::components::ParentEntity(groundLink),gz::sim::components::Collision());
    for(auto id:links){
      auto name=ecm.Component<gz::sim::components::Name>(id);if(!name||(name->Data().rfind("arm_",0)!=0&&name->Data().rfind("gripper_",0)!=0))continue;
      for(auto c:ecm.ChildrenByComponents(id,gz::sim::components::Collision())){
        auto contacts=ecm.Component<gz::sim::components::ContactSensorData>(c);if(!contacts)continue;
        for(const auto &contact:contacts->Data().contact())if(contact.collision1().id()==groundCollision||contact.collision2().id()==groundCollision)groundContact=true;
      }
    }
    plant.Contacts(model,ecm);std_msgs::msg::String plantMsg;plantMsg.data=plant.Json();plantMsg.data.pop_back();plantMsg.data+=",\"tool_ground_contact\":"+std::string(groundContact?"true":"false")+"}";plantState->publish(plantMsg);
    auto pose=gz::sim::worldPose(model.Entity(),ecm);auto q=pose.Rot();
    // Explicit ideal orientation sensor; angular velocity and acceleration unavailable.
    sensor_msgs::msg::Imu i;i.header.stamp=stamp;i.header.frame_id="robot/base_link";
    i.orientation.x=q.X();i.orientation.y=q.Y();i.orientation.z=q.Z();i.orientation.w=q.W();
    i.angular_velocity_covariance[0]=-1.;i.linear_acceleration_covariance[0]=-1.;imu->publish(i);
    tf2_msgs::msg::TFMessage t;
    auto add=[&](const std::string &name,const gz::math::Pose3d &p){geometry_msgs::msg::TransformStamped tf;tf.header.stamp=stamp;tf.header.frame_id=(name=="robot"||name=="weed")?"world":"robot";tf.child_frame_id=name;tf.transform.translation.x=p.Pos().X();tf.transform.translation.y=p.Pos().Y();tf.transform.translation.z=p.Pos().Z();tf.transform.rotation.x=p.Rot().X();tf.transform.rotation.y=p.Rot().Y();tf.transform.rotation.z=p.Rot().Z();tf.transform.rotation.w=p.Rot().W();t.transforms.push_back(tf);};
    add("robot",pose);
    if(plant.Available())add("weed",plant.pose);
    for(auto id:links){auto name=ecm.Component<gz::sim::components::Name>(id);if(name)add("robot/"+name->Data(),pose.Inverse()*gz::sim::worldPose(id,ecm));}
    poses->publish(t);
  }
};
}
GZ_ADD_PLUGIN(garden::RosAdapter,gz::sim::System,garden::RosAdapter::ISystemConfigure,garden::RosAdapter::ISystemPostUpdate,garden::RosAdapter::ISystemPreUpdate)

// Observer of Gazebo physics. Only input: a timed Twist to the original DiffDrive.
// No pose resets, direct velocity resets, mass changes or stabilizing forces.
#include <gz/sim/System.hh>
#include <gz/sim/Joint.hh>
#include <gz/sim/Link.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/Util.hh>
#include <gz/sim/components/Collision.hh>
#include <gz/sim/components/ContactSensorData.hh>
#include <gz/sim/components/JointVelocityCmd.hh>
#include <gz/sim/components/JointForceCmd.hh>
#include <gz/sim/components/Inertial.hh>
#include <gz/plugin/Register.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/twist.pb.h>
#include <google/protobuf/util/json_util.h>
#include <fstream>
#include <iomanip>
#include <array>
#include <cmath>

namespace garden {
class TerrainAudit:public gz::sim::System,public gz::sim::ISystemConfigure,
 public gz::sim::ISystemPreUpdate,public gz::sim::ISystemPostUpdate,
 public gz::sim::ISystemConfigurePriority {
  gz::sim::Model model;
  gz::sim::Entity base;
  std::array<gz::sim::Entity,2> wheels,joints;
  std::vector<gz::sim::Entity> links,collisions;
  gz::transport::Node node;
  gz::transport::Node::Publisher publisher;
  std::ofstream csv,contacts;
  double requested=0,nextPublish=0,nextLog=0,stopAt=22,startAt=2,speed=.15,publishPeriod=.05,logPeriod=.01,wheelRadius=.12;
  std::array<double,2> jointCmd{0,0},forceCmd{NAN,NAN};
 public:
  gz::sim::System::PriorityType ConfigurePriority() override {return 100;}
  void Configure(const gz::sim::Entity &entity,const std::shared_ptr<const sdf::Element> &sdf,
    gz::sim::EntityComponentManager &ecm,gz::sim::EventManager &) override {
    model=gz::sim::Model(entity);base=model.LinkByName(ecm,"base_link");links=model.Links(ecm);
    stopAt=sdf->Get<double>("stop_at");startAt=sdf->Get<double>("start_at");speed=sdf->Get<double>("speed");publishPeriod=sdf->Get<double>("command_period");logPeriod=sdf->Get<double>("sample_period");if(sdf->HasElement("wheel_radius"))wheelRadius=sdf->Get<double>("wheel_radius");
    csv.open(sdf->Get<std::string>("csv"));contacts.open(sdf->Get<std::string>("contacts"));
    if(!csv||!contacts)throw std::runtime_error("Cannot open audit logs");
    csv<<std::setprecision(12);contacts<<std::setprecision(12);
    csv<<"sim_s,cmd_v_mps,cmd_w_radps,transport_connected,x_m,y_m,z_m,v_body_x_mps,v_body_y_mps,v_world_x_mps,v_world_z_mps,pitch_deg,roll_deg,yaw_deg,com_x_m,com_y_m,com_z_m";
    for(int i=0;i<2;i++) {
      const std::string side=i==0?"left":"right";
      wheels[i]=model.LinkByName(ecm,side+"_wheel");joints[i]=model.JointByName(ecm,side+"_joint");
      gz::sim::Joint j(joints[i]);j.EnableVelocityCheck(ecm);j.EnablePositionCheck(ecm);j.EnableTransmittedWrenchCheck(ecm);
      csv<<","<<side<<"_omega_cmd_radps,"<<side<<"_omega_radps,"<<side<<"_force_cmd_Nm,"<<side<<"_axis_torque_Nm,"<<side<<"_rim_speed_mps,"<<side<<"_hub_forward_mps,"<<side<<"_slip_mps,"<<side<<"_slip_ratio";
    }
    for(auto link:links) {
      gz::sim::Link(link).EnableVelocityChecks(ecm);
      for(auto c:ecm.ChildrenByComponents(link,gz::sim::components::Collision()))collisions.push_back(c);
      csv<<","<<gz::sim::Link(link).Name(ecm).value()<<"_contacts,"<<gz::sim::Link(link).Name(ecm).value()<<"_normal_N";
    }
    csv<<'\n';
    publisher=node.Advertise<gz::msgs::Twist>("/garden/cmd_vel");
  }
  void PreUpdate(const gz::sim::UpdateInfo &info,gz::sim::EntityComponentManager &ecm) override {
    if(info.paused)return;
    const double t=std::chrono::duration<double>(info.simTime).count();
    requested=t>=startAt&&t<stopAt?speed:0;
    if(t+1e-9>=nextPublish) {
      gz::msgs::Twist msg;msg.mutable_linear()->set_x(requested);publisher.Publish(msg);nextPublish=t+publishPeriod;
    }
    // DiffDrive runs at priority 0. Physics clears commands after Update, so
    // capture the actual per-step request here, before the physical integration.
    for(int i=0;i<2;i++) {
      auto v=ecm.Component<gz::sim::components::JointVelocityCmd>(joints[i]);
      jointCmd[i]=v&&!v->Data().empty()?v->Data()[0]:NAN;
      auto f=ecm.Component<gz::sim::components::JointForceCmd>(joints[i]);
      forceCmd[i]=f&&!f->Data().empty()?f->Data()[0]:NAN;
    }
  }
  void PostUpdate(const gz::sim::UpdateInfo &info,const gz::sim::EntityComponentManager &ecm) override {
    const double t=std::chrono::duration<double>(info.simTime).count();
    if(info.paused||t+1e-9<nextLog)return;nextLog=t+logPeriod;
    auto p=gz::sim::worldPose(base,ecm);auto vel=gz::sim::Link(base).WorldLinearVelocity(ecm).value_or(gz::math::Vector3d::Zero);
    auto local=p.Rot().Inverse().RotateVector(vel);auto forward=p.Rot().RotateVector(gz::math::Vector3d::UnitX);
    gz::math::Vector3d com;double mass=0;
    for(auto link:links)if(auto in=ecm.Component<gz::sim::components::Inertial>(link)) {
      const double m=in->Data().MassMatrix().Mass();mass+=m;com+=m*(gz::sim::worldPose(link,ecm)*in->Data().Pose()).Pos();
    }
    com/=mass;
    const double deg=180/std::acos(-1.);
    csv<<t<<','<<requested<<",0,"<<publisher.HasConnections()<<','<<p.Pos().X()<<','<<p.Pos().Y()<<','<<p.Pos().Z()<<','<<local.X()<<','<<local.Y()<<','<<vel.X()<<','<<vel.Z()<<','<<p.Rot().Pitch()*deg<<','<<p.Rot().Roll()*deg<<','<<p.Rot().Yaw()*deg<<','<<com.X()<<','<<com.Y()<<','<<com.Z();
    for(int i=0;i<2;i++) {
      gz::sim::Joint j(joints[i]);auto v=j.Velocity(ecm);auto w=j.TransmittedWrench(ecm);
      const double omega=v&&!v->empty()?(*v)[0]:NAN;
      // Joint axis is (0,0,-1), in the joint frame. No joint damping/friction.
      // This is the simulated transmitted wrench projection, NOT a force command.
      const double torque=w&&!w->empty()?-(*w)[0].torque().z():NAN;
      const double rim=wheelRadius*omega;
      const double hub=gz::sim::Link(wheels[i]).WorldLinearVelocity(ecm).value_or(gz::math::Vector3d::Zero).Dot(forward);
      const double slip=rim-hub;const double ratio=slip/std::max({std::abs(rim),std::abs(hub),.01});
      csv<<','<<jointCmd[i]<<','<<omega<<','<<forceCmd[i]<<','<<torque<<','<<rim<<','<<hub<<','<<slip<<','<<ratio;
    }
    contacts<<"{\"sim_s\":"<<t<<",\"collisions\":[";bool first=true;
    for(auto link:links) {
      int count=0;double normal=0;
      for(auto c:ecm.ChildrenByComponents(link,gz::sim::components::Collision())) {
        auto data=ecm.Component<gz::sim::components::ContactSensorData>(c);if(!data)continue;
        if(!first)contacts<<',';first=false;
        std::string json;google::protobuf::util::MessageToJsonString(data->Data(),&json);
        contacts<<"{\"link\":\""<<gz::sim::Link(link).Name(ecm).value()<<"\",\"entity\":"<<c<<",\"data\":"<<json<<'}';
        for(const auto &contact:data->Data().contact()) {
          count+=contact.position_size();
          for(int k=0;k<std::min(contact.normal_size(),contact.wrench_size());k++) {
            const auto &n=contact.normal(k);const auto &f=contact.wrench(k).body_1_wrench().force();
            normal+=std::abs(n.x()*f.x()+n.y()*f.y()+n.z()*f.z());
          }
        }
      }
      csv<<','<<count<<','<<normal;
    }
    contacts<<"]}\n";csv<<'\n';
  }
};
}
GZ_ADD_PLUGIN(garden::TerrainAudit,gz::sim::System,garden::TerrainAudit::ISystemConfigure,
 garden::TerrainAudit::ISystemPreUpdate,garden::TerrainAudit::ISystemPostUpdate,garden::TerrainAudit::ISystemConfigurePriority)

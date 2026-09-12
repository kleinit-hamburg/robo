#include <gz/sim/System.hh>
#include <gz/sim/Joint.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/components/JointForceCmd.hh>
#include <gz/sim/components/JointPosition.hh>
#include <gz/sim/components/JointVelocity.hh>
#include <gz/plugin/Register.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/twist.pb.h>
#include <array>
#include <cmath>
#include <string>
#include <vector>
#include <functional>

namespace garden {
class QuadrupedTrot:public gz::sim::System,public gz::sim::ISystemConfigure,public gz::sim::ISystemPreUpdate {
  struct Leg {std::string name; gz::sim::Entity hip{gz::sim::kNullEntity}; gz::sim::Entity knee{gz::sim::kNullEntity}; double phase{0}; double side{1};};
  gz::sim::Model model;
  std::array<Leg,4> legs;
  gz::transport::Node node;
  double cmdV{0},cmdW{0},lastT{0},kp{85},kd{4.5},effort{55},freq{1.45},stride{0.38},lift{0.45};
 public:
  void Configure(const gz::sim::Entity &entity,const std::shared_ptr<const sdf::Element> &sdf,gz::sim::EntityComponentManager &ecm,gz::sim::EventManager &) override {
    model=gz::sim::Model(entity);
    legs={Leg{"front_left",gz::sim::kNullEntity,gz::sim::kNullEntity,0,1},Leg{"front_right",gz::sim::kNullEntity,gz::sim::kNullEntity,0.5,-1},Leg{"rear_left",gz::sim::kNullEntity,gz::sim::kNullEntity,0.5,1},Leg{"rear_right",gz::sim::kNullEntity,gz::sim::kNullEntity,0,-1}};
    if(sdf->HasElement("kp"))kp=sdf->Get<double>("kp"); if(sdf->HasElement("kd"))kd=sdf->Get<double>("kd");
    if(sdf->HasElement("effort"))effort=sdf->Get<double>("effort"); if(sdf->HasElement("frequency"))freq=sdf->Get<double>("frequency");
    if(sdf->HasElement("stride"))stride=sdf->Get<double>("stride"); if(sdf->HasElement("lift"))lift=sdf->Get<double>("lift");
    for(auto &leg:legs){
      leg.hip=model.JointByName(ecm,leg.name+"_hip_joint");leg.knee=model.JointByName(ecm,leg.name+"_knee_joint");
      gz::sim::Joint(leg.hip).EnablePositionCheck(ecm);gz::sim::Joint(leg.hip).EnableVelocityCheck(ecm);
      gz::sim::Joint(leg.knee).EnablePositionCheck(ecm);gz::sim::Joint(leg.knee).EnableVelocityCheck(ecm);
    }
    node.Subscribe<gz::msgs::Twist>("/garden/cmd_vel",std::function<void(const gz::msgs::Twist &)>([this](const gz::msgs::Twist &msg){cmdV=msg.linear().x();cmdW=msg.angular().z();}));
  }
  static double first(const std::optional<std::vector<double>> &v){return v&& !v->empty()?(*v)[0]:0.0;}
  void driveJoint(gz::sim::Entity e,double target,gz::sim::EntityComponentManager &ecm){
    gz::sim::Joint j(e);double q=first(j.Position(ecm));double dq=first(j.Velocity(ecm));double tau=kp*(target-q)-kd*dq;
    tau=std::max(-effort,std::min(effort,tau));
    auto c=ecm.Component<gz::sim::components::JointForceCmd>(e);
    if(c)c->Data()={tau};else ecm.CreateComponent(e,gz::sim::components::JointForceCmd({tau}));
  }
  void PreUpdate(const gz::sim::UpdateInfo &info,gz::sim::EntityComponentManager &ecm) override {
    if(info.paused)return;double t=std::chrono::duration<double>(info.simTime).count();double dt=lastT>0?t-lastT:0.001;lastT=t;
    double speed=std::max(-0.18,std::min(0.18,cmdV));double turn=std::max(-0.35,std::min(0.35,cmdW));
    double amp=std::min(1.0,std::abs(speed)/0.15+std::abs(turn)/0.35); if(amp<0.03)amp=0;
    double dir=speed>=0?1:-1;
    for(auto &leg:legs){
      leg.phase+=dt*freq*amp;leg.phase-=std::floor(leg.phase);
      double p=leg.phase;double swing=p<0.38?1.0:0.0;
      double cycle=std::sin(2*M_PI*p);double liftTerm=swing*std::sin(M_PI*p/0.38);
      double turnBias=turn*leg.side*0.25;
      double hipTarget=-0.05 + dir*stride*cycle*amp + turnBias;
      double kneeTarget=0.78 + lift*liftTerm*amp - 0.10*std::cos(2*M_PI*p)*amp;
      driveJoint(leg.hip,hipTarget,ecm);driveJoint(leg.knee,kneeTarget,ecm);
    }
  }
};
}
GZ_ADD_PLUGIN(garden::QuadrupedTrot,gz::sim::System,garden::QuadrupedTrot::ISystemConfigure,garden::QuadrupedTrot::ISystemPreUpdate)

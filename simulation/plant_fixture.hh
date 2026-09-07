#pragma once
#include <gz/sim/Link.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/Util.hh>
#include <gz/sim/components/Model.hh>
#include <gz/sim/components/ParentEntity.hh>
#include <gz/sim/components/Name.hh>
#include <gz/sim/components/ContactSensorData.hh>
#include <algorithm>
#include <sstream>

// Synthetic root force fixture, not botanical or soil calibration.
class PlantFixture {
  gz::sim::Entity stem{gz::sim::kNullEntity}, collision{gz::sim::kNullEntity};
  gz::math::Vector3d anchor{.96,-.8,.11};
 public:
  bool Available() const {return stem!=gz::sim::kNullEntity;}
  double resistance=0,peak=25;bool released=false,left=false,right=false;
  gz::math::Pose3d pose;
  void Update(gz::sim::EntityComponentManager &ecm) {
    if(stem==gz::sim::kNullEntity){
      auto weed=ecm.EntityByComponents(gz::sim::components::Model(),gz::sim::components::Name("weed"));
      if(!weed)return;stem=gz::sim::Model(weed).LinkByName(ecm,"stem");if(!stem)return;
      collision=ecm.EntityByComponents(gz::sim::components::ParentEntity(stem),gz::sim::components::Name("stem_collision"));
      gz::sim::Link(stem).EnableVelocityChecks(ecm);
    }
    gz::sim::Link link(stem);pose=gz::sim::worldPose(stem,ecm);
    auto displacement=pose.Pos()-anchor;auto velocity=link.WorldLinearVelocity(ecm).value_or(gz::math::Vector3d::Zero);
    double d=std::max(0.,displacement.Z());
    if(displacement.Length()>=.08)released=true;
    resistance=released?0.:peak*(d<.06?d/.06:std::max(0.,(.08-d)/.02));
    if(!released){
      gz::math::Vector3d f(std::clamp(-200*displacement.X()-5*velocity.X(),-40.,40.),std::clamp(-200*displacement.Y()-5*velocity.Y(),-40.,40.),std::clamp(-resistance-2*velocity.Z(),-40.,40.));
      auto rates=link.WorldAngularVelocity(ecm).value_or(gz::math::Vector3d::Zero);
      gz::math::Vector3d torque(std::clamp(-.1*pose.Rot().Roll()-.01*rates.X(),-.05,.05),std::clamp(-.1*pose.Rot().Pitch()-.01*rates.Y(),-.05,.05),0);
      link.AddWorldWrench(ecm,f,torque);
    }
  }
  void Contacts(const gz::sim::Model &robot,const gz::sim::EntityComponentManager &ecm){
    auto touching=[&](const char *linkName){
      auto link=robot.LinkByName(ecm,linkName);if(!link)return false;
      std::string collisionName(linkName);collisionName.resize(collisionName.size()-5);collisionName+="_collision";
      auto sensor=ecm.EntityByComponents(gz::sim::components::ParentEntity(link),gz::sim::components::Name(collisionName));
      auto contacts=ecm.Component<gz::sim::components::ContactSensorData>(sensor);if(!contacts)return false;
      for(const auto &contact:contacts->Data().contact())if(contact.collision1().id()==collision||contact.collision2().id()==collision)return true;
      return false;
    };
    left=touching("gripper_left_link");right=touching("gripper_right_link");
  }
  std::string Json() const {
    std::ostringstream s;s<<"{\"available\":"<<(stem?"true":"false")<<",\"left_contact\":"<<(left?"true":"false")<<",\"right_contact\":"<<(right?"true":"false")<<",\"released\":"<<(released?"true":"false")<<",\"root_resistance_N\":"<<resistance<<",\"root_peak_N\":"<<peak<<",\"position\":["<<pose.Pos().X()<<","<<pose.Pos().Y()<<","<<pose.Pos().Z()<<"]}";return s.str();
  }
};

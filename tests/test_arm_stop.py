"""Regression for ROS array positions leaking into the browser status after stop."""
import array,json,sys,threading,unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from browser_server import Application,JOINTS
class Point:
    @property
    def positions(self):return self._positions
    @positions.setter
    def positions(self,value):self._positions=array.array('d',value)
class ArmStopTests(unittest.TestCase):
    def test_ros_array_is_converted_in_stop_status(self):
        app=Application.__new__(Application);app.lock=threading.RLock();app.weed_cycle=None;app.tool_task=None
        app.motion=SimpleNamespace(stop=lambda reason:None);app.profile='plant';app.joint_positions={name:0. for name in JOINTS}
        messages=[];publisher=SimpleNamespace(publish=messages.append)
        app.publisher=publisher;app.tool_publisher=publisher;app.arm_publisher=publisher
        app.Twist=SimpleNamespace;app.WrenchStamped=lambda:SimpleNamespace(header=SimpleNamespace())
        app.JointTrajectory=SimpleNamespace;app.JointTrajectoryPoint=Point
        app.halt()
        decoded=json.loads(json.dumps(app.arm_target))
        self.assertEqual(decoded['command'],'hold');self.assertEqual(decoded['positions'],[0.]*8)
        self.assertIsInstance(messages[-1].points[0].positions,array.array)

import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from motion_core import Motion, heading_from_sample, readiness_issues

class MotionTests(unittest.TestCase):
    def test_timeout_stops_without_browser(self):
        m=Motion();m.heading(0,0);m.request('forward',0)
        self.assertEqual(m.output(.1),(.15,0))
        m.heading(0,.7)
        self.assertEqual(m.output(.7),(0.,0.));self.assertEqual(m.reason,'command_timeout')
    def test_heartbeat_does_not_hide_missing_heading(self):
        m=Motion();m.heading(0,0);m.request('left',0);m.heartbeat(.6)
        self.assertEqual(m.output(.6),(0.,0.));self.assertEqual(m.reason,'heading_timeout')
    def test_turn_crosses_angle_wrap_and_stops(self):
        m=Motion();m.heading(3,0);m.request('turn_around',0)
        for i in range(1,33):
            now=i*.1;m.heartbeat(now);m.heading(math.atan2(math.sin(3+i*.1),math.cos(3+i*.1)),now);m.output(now)
        self.assertEqual(m.command,'stop');self.assertEqual(m.reason,'turn_complete')
    def test_turn_deadline_prevents_unbounded_spin(self):
        m=Motion();m.heading(0,0);m.request('turn_around',0);m.heartbeat(21);m.heading(0,21)
        self.assertEqual(m.output(21),(0.,0.));self.assertEqual(m.reason,'turn_timeout')
    def test_stop_cancels_turn(self):
        m=Motion();m.heading(0,0);m.request('turn_around',0);m.request('stop',.1);m.heartbeat(.2)
        self.assertEqual(m.output(.3),(0.,0.))
    def test_outputs_are_ros_float_fields(self):
        for command in ('forward','backward','left','right','stop','turn_around'):
            m=Motion();m.heading(0,0);m.request(command,0)
            self.assertTrue(all(type(v) is float for v in m.output(.1)))
    def test_stale_and_invalid_heading_samples(self):
        self.assertIsNone(heading_from_sample((0,0,0,1),8,10))
        self.assertIsNone(heading_from_sample((0,0,0,1),11,10))
        self.assertIsNone(heading_from_sample((0,0,0,0),10,10))
        self.assertIsNone(heading_from_sample((0,0,0,1),10,10,False))
        self.assertEqual(heading_from_sample((0,0,0,1),9.95,10),0.)
    def test_command_requires_heading(self):
        with self.assertRaises(ValueError):Motion().request('forward',0)

if __name__=='__main__':unittest.main()


class ReadinessTests(unittest.TestCase):
    def test_clock_alone_does_not_enable_driving(self):
        self.assertEqual(readiness_issues(True,False,False,True,.01,None,None),['imu_missing','joints_missing'])
    def test_fresh_complete_state_and_expiry(self):
        self.assertEqual(readiness_issues(True,False,False,True,.01,.02,.03),[])
        self.assertEqual(readiness_issues(True,False,False,True,.01,.51,1.01),['imu_stale','joints_stale'])
    def test_process_pause_and_controller_gates(self):
        self.assertEqual(readiness_issues(False,True,True,False,.01,.01,.01),['controller_missing','world_switching','simulation_paused','process_unavailable'])

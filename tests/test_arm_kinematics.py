import math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from arm_model import fixture_pose,fixture_waypoints,LIMITS
class FixtureKinematicsTests(unittest.TestCase):
    def test_cartesian_targets_and_limits(self):
        for z in (.1,.17,.24,.4):
            q=fixture_pose(z);a,b,c=q[1],q[2],q[4]
            x=.38+.25*math.sin(a)+.31*math.sin(a+b)+.185*math.sin(a+b+c)
            height=.48+.25*math.cos(a)+.31*math.cos(a+b)+.185*math.cos(a+b+c)
            self.assertAlmostEqual(x,.96);self.assertAlmostEqual(height,z)
            self.assertTrue(all(lo<=v<=hi for v,(lo,hi) in zip(q,LIMITS)))
    def test_approach_and_extract_keep_orientation(self):
        for cmd in ('work','extract'):
            for q in fixture_waypoints(cmd):self.assertAlmostEqual(q[1]+q[2]+q[4],1.7)
    def test_unreachable_target_rejected(self):
        with self.assertRaises(ValueError):fixture_pose(2.)

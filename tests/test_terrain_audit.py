"""Physics fixture invariants, not success-by-parameter-tuning checks."""
import math,sys,tempfile,unittest
from pathlib import Path
import xml.etree.ElementTree as E
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from terrain_audit import ROOT,CFG,make_world
from terrain_model import terrain
from inspect_tracked_physics import transform,inspect
class TerrainAuditTests(unittest.TestCase):
    def test_robot_inertias_collisions_joints_and_diffdrive_unchanged(self):
        original=E.parse(ROOT/'models/tracked/model.sdf').getroot().find('model')
        def canonical(e):return (e.tag,sorted(e.attrib.items()),(e.text or '').strip(),[canonical(c) for c in e])
        with tempfile.TemporaryDirectory() as d:
            robot=E.parse(make_world('grade_5',Path(d))).getroot().find('world/model[@name="robot"]')
            for link in original.findall('link'):
                other=robot.find(f"link[@name='{link.get('name')}']")
                for child in [link.find('inertial'),*link.findall('collision')]:
                    candidate=other.find(child.tag if child.tag=='inertial' else f"collision[@name='{child.get('name')}']")
                    self.assertEqual(canonical(child),canonical(candidate))
            self.assertEqual([canonical(j) for j in original.findall('joint')],[canonical(j) for j in robot.findall('joint')])
            self.assertEqual(canonical(original.find("plugin[@name='gz::sim::systems::DiffDrive']")),canonical(robot.find("plugin[@name='gz::sim::systems::DiffDrive']")))
    def test_ramp_top_has_exact_flat_entry_and_flush_landing(self):
        with tempfile.TemporaryDirectory() as d:
            for angle in (5,10,15):
                world=E.parse(make_world(f'grade_{angle}',Path(d))).getroot().find('world');ramp=world.find(f"model[@name='grade_{angle}']")
                xyz,R=transform(ramp.findtext('pose'));L=CFG['ramp']['length_m'];thick=CFG['ramp']['thickness_m']
                start=xyz+R@[-L/2,0,thick/2];end=xyz+R@[L/2,0,thick/2]
                self.assertAlmostEqual(start[0],.5);self.assertAlmostEqual(start[2],0)
                landing=world.find("model[@name='landing']");center=list(map(float,landing.findtext('pose').split()));size=list(map(float,landing.findtext('link/collision/geometry/box/size').split()))
                self.assertAlmostEqual(end[0],center[0]-size[0]/2);self.assertAlmostEqual(end[2],center[2]+size[2]/2)
    def test_uneven_matches_existing_profile_and_documented_heights(self):
        old=E.Element('world');terrain(old,'uneven')
        with tempfile.TemporaryDirectory() as d:
            world=E.parse(make_world('uneven',Path(d))).getroot().find('world')
            for n,old_model in enumerate(old.findall('model')):
                model=world.find(f"model[@name='undulation_{n}']")
                self.assertEqual(model.findtext('pose'),old_model.findtext('pose'))
                z=float(model.findtext('pose').split()[2]);self.assertAlmostEqual(z+.025,.01+.01*math.sin(n*math.pi/4))
    def test_mass_properties_are_physically_admissible(self):
        data=inspect();self.assertAlmostEqual(data['mass_kg'],65);self.assertAlmostEqual(data['com_model_m'][2],.287476923076923)
        self.assertTrue(all(l['positive_definite'] and l['triangle_inequality'] for l in data['links']))

from verify_terrain_logs import friction_check
class ContactConsistencyTests(unittest.TestCase):
    def test_zero_normal_cannot_sustain_friction(self):
        N,T,excess,bad=friction_check({'z':1},{'x':100},.6)
        self.assertEqual(N,0);self.assertEqual(T,100);self.assertTrue(bad)
    def test_square_friction_pyramid_is_not_confused_with_circle(self):
        self.assertFalse(friction_check({'z':1},{'x':60,'y':60,'z':100},.6)[3])
    def test_world_orientation_and_force_sign_do_not_change_bound(self):
        a=friction_check({'z':1},{'x':30,'z':100},.6)
        b=friction_check({'x':1},{'z':-30,'x':-100},.6)
        self.assertEqual(a,b)

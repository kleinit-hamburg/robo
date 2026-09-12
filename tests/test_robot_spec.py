import json,sys,unittest,xml.etree.ElementTree as E
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from robot_spec import load_spec

class RobotSpecTests(unittest.TestCase):
    def test_dynamic_variants_have_generated_sdf_xacro_and_catalog_entry(self):
        spec=load_spec();catalog=json.loads((ROOT/'config/preview-concepts.json').read_text())
        for name,data in spec['variants'].items():
            self.assertIn(name,catalog)
            self.assertTrue((ROOT/data['cad_references']['sdf']).exists())
            self.assertTrue((ROOT/data['cad_references']['xacro']).exists())
            model=E.parse(ROOT/data['cad_references']['sdf']).getroot().find('model')
            self.assertIsNotNone(model.find("plugin[@name='gz::sim::systems::DiffDrive']"))
            self.assertEqual(model.findtext("plugin[@name='gz::sim::systems::DiffDrive']/wheel_radius"),str(data['drive']['wheel_radius_m']))
    def test_structural_part_ids_are_unique_and_referenced(self):
        spec=load_spec();ids=[p['part_id'] for p in spec['structural_parts']]
        self.assertEqual(len(ids),len(set(ids)))
        text=json.dumps(spec['variants'])
        for part_id in ids:self.assertIn(part_id,text)

    def test_bogie_variant_has_sprung_roller_spec(self):
        spec=load_spec();bogie=spec['variants']['tracked_bogie']
        self.assertEqual(bogie['supports']['type'],'spring_bogie_rollers')
        self.assertEqual(len(bogie['supports']['positions_x_m']),6)
        self.assertGreater(bogie['supports']['travel_m'],0.05)
        self.assertGreater(bogie['supports']['spring_stiffness_N_m'],1000)
        model=E.parse(ROOT/bogie['cad_references']['sdf']).getroot().find('model')
        left_joints=model.findall("plugin[@name='gz::sim::systems::DiffDrive']/left_joint")
        right_joints=model.findall("plugin[@name='gz::sim::systems::DiffDrive']/right_joint")
        self.assertEqual(len(left_joints),6)
        self.assertEqual(len(right_joints),6)
        self.assertEqual(len(model.findall("joint[@type='prismatic']")),12)


    def test_guided_variant_targets_120mm_obstacle_study(self):
        spec=load_spec();guided=spec['variants']['tracked_guided']
        self.assertEqual(guided['supports']['type'],'spring_bogie_rollers')
        self.assertGreaterEqual(guided['drive']['wheel_radius_m'],0.12)
        self.assertGreaterEqual(guided['track']['approach_angle_deg'],55)
        self.assertEqual(guided['drive']['effort_limit_Nm'],spec['variants']['tracked_bogie']['drive']['effort_limit_Nm'])
        self.assertIn('light45',spec['weight_classes'])
        self.assertIn('medium65',spec['weight_classes'])
        self.assertIn('heavy85',spec['weight_classes'])

    def test_improved_variant_changes_mechanical_geometry(self):
        spec=load_spec();old=spec['variants']['tracked'];new=spec['variants']['tracked_improved']
        self.assertGreater(new['drive']['wheel_radius_m'],old['drive']['wheel_radius_m'])
        self.assertGreater(new['clearance']['nominal_body_bottom_m'],old['clearance']['nominal_body_bottom_m'])
        self.assertGreater(new['track']['gauge_m'],old['track']['gauge_m'])

class ChassisBenchmarkArtifactTests(unittest.TestCase):
    def test_recorded_benchmark_contains_required_cases_and_limit(self):
        rows=json.loads((ROOT/'docs/validation/chassis-benchmark-summary.json').read_text())
        by={(r['variant'],r['case']):r for r in rows}
        for variant in ('tracked','tracked_improved'):
            for case in ('step_30','step_50','step_80','ramp_10','ramp_20','ramp_30','diagonal_wave','side_slope','narrow_gate'):
                self.assertIn((variant,case),by)
        self.assertFalse(by[('tracked','step_30')]['succeeded'])
        self.assertTrue(by[('tracked_improved','step_30')]['succeeded'])
        self.assertTrue(by[('tracked_improved','step_50')]['succeeded'])
        self.assertFalse(by[('tracked_improved','step_80')]['succeeded'])
        self.assertTrue(by[('tracked_bogie','step_80')]['succeeded'])
        self.assertFalse(by[('tracked_bogie','step_100')]['succeeded'])
        self.assertTrue(by[('tracked_bogie','ramp_30')]['succeeded'])
        self.assertFalse(by[('tracked_bogie','ramp_40')]['succeeded'])
        self.assertTrue(by[('tracked_bogie','diagonal_wave')]['succeeded'])


class WeightClassBenchmarkArtifactTests(unittest.TestCase):
    def test_weight_class_results_capture_current_limit(self):
        rows=json.loads((ROOT/'docs/validation/weight-class-chassis-summary.json').read_text())
        by={(r['variant'],r['mass_class'],r['case']):r for r in rows}
        for variant in ('tracked_bogie','tracked_guided'):
            for mass_class in ('light45','medium65','heavy85'):
                self.assertTrue(by[(variant,mass_class,'step_80')]['succeeded'])
                self.assertFalse(by[(variant,mass_class,'step_120')]['succeeded'])
        for mass_class in ('light45','medium65','heavy85'):
            self.assertTrue(by[('tracked_guided',mass_class,'step_100')]['succeeded'])
            self.assertFalse(by[('tracked_bogie',mass_class,'step_100')]['succeeded'])
            self.assertIsNotNone(by[('tracked_guided',mass_class,'ramp_30')]['mechanical_drive_energy_per_m_Wh_m'])

    def test_mechanical_comparison_marks_legged_locomotion_unready(self):
        report=json.loads((ROOT/'docs/validation/mechanical-comparison-summary.json').read_text())
        static=report['static_tool_pull_limits']
        for platform in ('quadruped','humanoid'):
            rows=[r for r in static if r['platform']==platform]
            self.assertEqual(len(rows),3)
            self.assertFalse(any(r['locomotion_ready_in_gazebo'] for r in rows))

if __name__=='__main__':unittest.main()

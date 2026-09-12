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
            if 'track' in data:
                self.assertIsNotNone(model.find("plugin[@name='gz::sim::systems::DiffDrive']"))
                self.assertEqual(model.findtext("plugin[@name='gz::sim::systems::DiffDrive']/wheel_radius"),str(data['drive']['wheel_radius_m']))
            elif 'legs' in data:
                self.assertIsNotNone(model.find("plugin[@name='garden::QuadrupedTrot']"))
                actuated=[j for j in model.findall("joint[@type='revolute']") if j.get('name','').endswith(('_hip_joint','_knee_joint'))]
                self.assertEqual(len(actuated),8)
                self.assertEqual(len(model.findall("link")),13)
            else:
                self.fail(f"unknown dynamic variant schema for {name}")
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

    def test_potato_row_variants_separate_overrow_and_inrow_geometry(self):
        spec=load_spec();over=spec['variants']['tracked_overrow_high_clearance'];narrow=spec['variants']['tracked_inrow_narrow']
        self.assertGreaterEqual(over['clearance']['nominal_body_bottom_m'],0.45)
        self.assertGreaterEqual(over['track']['gauge_m'],0.62)
        self.assertLessEqual(over['track']['belt_width_m'],0.13)
        self.assertLessEqual(narrow['track']['gauge_m']+narrow['track']['belt_width_m'],0.45)
        self.assertLess(narrow['body']['collision_width_m'],0.30)
        self.assertGreater(narrow['clearance']['nominal_body_bottom_m'],0.18)
        belt8=spec['variants']['tracked_overrow_belt08'];belt6=spec['variants']['tracked_overrow_belt06']
        self.assertEqual(round(belt8['track']['belt_width_m'],2),0.08)
        self.assertEqual(round(belt6['track']['belt_width_m'],2),0.06)
        self.assertLess(belt8['track']['gauge_m']+belt8['track']['belt_width_m'],over['track']['gauge_m']+over['track']['belt_width_m'])
        self.assertLess(belt6['drive']['effort_limit_Nm'],belt8['drive']['effort_limit_Nm'])

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
        cfg=json.loads((ROOT/'config/chassis-benchmark.json').read_text())
        by={(r['variant'],r['mass_class'],r['case']):r for r in rows}
        for variant in ('tracked_bogie','tracked_guided'):
            for mass_class in ('light45','medium65','heavy85'):
                self.assertTrue(by[(variant,mass_class,'step_80')]['succeeded'])
                self.assertFalse(by[(variant,mass_class,'step_120')]['succeeded'])
        for mass_class in ('light45','medium65','heavy85'):
            self.assertTrue(by[('tracked_guided',mass_class,'step_100')]['succeeded'])
            self.assertFalse(by[('tracked_bogie',mass_class,'step_100')]['succeeded'])
            self.assertIsNotNone(by[('tracked_guided',mass_class,'ramp_30')]['mechanical_drive_energy_per_m_Wh_m'])
            for case in cfg['cases']:
                self.assertIn(('quadruped_trot',mass_class,case),by)
                self.assertFalse(by[('quadruped_trot',mass_class,case)]['succeeded'])
            smoke=by[('quadruped_trot',mass_class,'step_30')]
            self.assertGreater(smoke['body_contact_samples'],0)
            self.assertGreater(smoke['max_tilt_deg'],30)
            self.assertGreater(smoke['mechanical_drive_energy_Wh'],0)

    def test_mechanical_comparison_distinguishes_tested_and_static_legged_models(self):
        report=json.loads((ROOT/'docs/validation/mechanical-comparison-summary.json').read_text())
        rollup={(r['variant'],r['mass_class']):r for r in report['gazebo_rollup']}
        static=report['static_tool_pull_limits']
        for mass_class in ('light45','medium65','heavy85'):
            self.assertIsNone(rollup[('quadruped_trot',mass_class)]['max_passed_step_mm'])
            self.assertEqual(rollup[('quadruped_trot',mass_class)]['runs'],14)
        for platform,ready in (('quadruped_trot',True),('quadruped',False),('humanoid',False)):
            rows=[r for r in static if r['platform']==platform]
            self.assertEqual(len(rows),3)
            self.assertEqual({r['locomotion_ready_in_gazebo'] for r in rows},{ready})

class VisualAssetPipelineTests(unittest.TestCase):
    def test_potato_ridge_uses_generated_mesh_visuals_and_keeps_collision_primitives(self):
        import sys
        sys.path.insert(0,str(ROOT/'scripts'))
        from browser_server import build_world
        world=ROOT/'build/test-potato-ridge-visual.sdf'
        objects=build_world('tracked_overrow_high_clearance',world,'potato_ridge')
        mesh_visuals=[v for o in objects for l in o['links'] for v in l['visuals'] if v['shape']=='mesh']
        self.assertGreaterEqual(len(mesh_visuals),55)
        self.assertTrue(any('potato_ridge_340cm.glb' in v['uri'] for v in mesh_visuals))
        self.assertTrue(any('potato_haulm.glb' in v['uri'] for v in mesh_visuals))
        self.assertTrue(any('weed_broadleaf.glb' in v['uri'] for v in mesh_visuals))
        self.assertTrue(any('soil_patch_7x5.glb' in v['uri'] for v in mesh_visuals))
        ridge_count=sum(1 for o in objects if o['name'].startswith('potato_') and o['name'].endswith('_ridge'))
        self.assertGreaterEqual(ridge_count,5)
        self.assertTrue(any('tracked_robot_shell.glb' in v['uri'] for v in mesh_visuals))
        text=world.read_text()
        self.assertIn('<collision name="collision">',text)
        self.assertIn('<mesh>',text)

    def test_generated_assets_exist(self):
        for rel in (
            'assets/visual/potato_ridge_340cm.glb',
            'assets/visual/potato_haulm.glb',
            'assets/visual/potato_haulm_b.glb',
            'assets/visual/potato_haulm_c.glb',
            'assets/visual/weed_broadleaf.glb',
            'assets/visual/soil_patch_7x5.glb',
            'assets/visual/tracked_robot_shell.glb',
            'assets/cad/TRK-BASE-001-visual-reference.step',
            'assets/cad/TRK-BASE-001-visual-reference.stl',
        ):
            path=ROOT/rel
            self.assertTrue(path.exists(),rel)
            self.assertGreater(path.stat().st_size,1000,rel)

if __name__=='__main__':unittest.main()

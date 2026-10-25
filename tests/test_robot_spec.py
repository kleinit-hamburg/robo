import json,sys,unittest,xml.etree.ElementTree as E
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from robot_spec import ACTIVE_CONCEPT,load_spec
from motion_core import SPEED_MODES

class RobotSpecTests(unittest.TestCase):
    def test_active_drive_limit_covers_transport_command_and_wheel_rate(self):
        drive=load_spec()['variants'][ACTIVE_CONCEPT]['drive']
        self.assertGreaterEqual(drive['max_linear_velocity_mps'],SPEED_MODES['transport']['forward'])
        self.assertLessEqual(SPEED_MODES['transport']['forward']/drive['wheel_radius_m'],drive['velocity_limit_radps'])
        self.assertLess(drive['min_linear_acceleration_mps2'],0)
    def test_dynamic_variants_have_generated_sdf_xacro_and_catalog_entry(self):
        spec=load_spec();catalog=json.loads((ROOT/'config/preview-concepts.json').read_text())
        self.assertEqual(set(catalog),{ACTIVE_CONCEPT})
        for name,data in spec['variants'].items():
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
        rows=json.loads((ROOT/'docs/validation/tracked-weight-class-summary.json').read_text())
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
        self.assertTrue(all(name.startswith('tracked') for name in cfg['variants']))

class VisualAssetPipelineTests(unittest.TestCase):
    def test_potato_ridge_uses_generated_mesh_visuals_and_keeps_collision_primitives(self):
        import sys
        sys.path.insert(0,str(ROOT/'scripts'))
        from browser_server import build_world
        world=ROOT/'build/test-potato-ridge-visual.sdf'
        objects=build_world(ACTIVE_CONCEPT,world,'potato_ridge')
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

    def test_field_driving_has_no_rigid_stems_or_small_stones(self):
        from browser_server import build_world
        world=ROOT/'build/test-potato-ridge-contact.sdf'
        build_world(ACTIVE_CONCEPT,world,'potato_ridge')
        models=E.parse(world).getroot().find('world').findall('model')
        ground=next(model for model in models if model.get('name')=='ground')
        self.assertEqual(ground.findtext('link/collision/geometry/box/size'),'20.0 6.0 0.1')
        for model in models:
            name=model.get('name','')
            if name.startswith('weed_between_ridges_') or name.startswith('soil_clod_') or ('_plant_' in name and name.startswith('potato_')):
                self.assertFalse(model.findall('.//collision'),name)
        ridges=[model for model in models if model.get('name','').endswith('_ridge')]
        self.assertEqual(len(ridges),5)
        self.assertTrue(all(model.findall('.//collision') for model in ridges))

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

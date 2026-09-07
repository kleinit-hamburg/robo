import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from task_core import WeedCycle
class WeedCycleTests(unittest.TestCase):
    def test_missing_contact_cannot_be_success(self):
        t=WeedCycle(0);t.advance('verify_grip',0)
        self.assertEqual(t.update(7,True,{'available':True}),'hold')
        self.assertFalse(t.result['success']);self.assertEqual(t.result['reason'],'grip_not_confirmed')
    def test_root_already_displaced_is_rejected(self):
        t=WeedCycle(0);self.assertEqual(t.update(.1,False,{'available':True,'released':True}),'hold')
        self.assertEqual(t.result['reason'],'plant_displaced_before_grasp')
    def test_complete_confirmed_sequence(self):
        plant={'available':True,'released':False,'left_contact':False,'right_contact':False};t=WeedCycle(0)
        self.assertEqual(t.update(0,False,plant),'work');t.update(1,True,plant)
        self.assertEqual(t.update(1.1,False,plant),'close')
        plant.update(left_contact=True,right_contact=True);t.update(2,True,plant);t.update(4.1,True,plant)
        self.assertEqual(t.update(4.2,False,plant),'extract');plant['released']=True;t.update(5.2,True,plant)
        self.assertEqual(t.update(5.3,False,plant),'open');plant.update(left_contact=False,right_contact=False);t.update(6.3,True,plant)
        self.assertEqual(t.update(6.4,False,plant),'home');t.update(7.4,True,plant)
        self.assertTrue(t.result['success'])

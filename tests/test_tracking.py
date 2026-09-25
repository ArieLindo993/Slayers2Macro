import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from detector import detect,Reading
from calibration import AutoCalibration
from engine import Engine
from macro import DEFAULTS


class TrackingRecovery(unittest.TestCase):
    def test_translucent_outlined_target_and_dim_marker(self):
        image=np.full((400,66,3),(44,90,140),np.uint8)
        # Interior azulado; contorno amarelo dessaturado de apenas dois pixels.
        image[60:102,3:63]=(87,117,115)
        image[60:62,3:63]=(107,146,143)
        image[100:102,3:63]=(107,146,143)
        image[60:102,3:5]=(127,177,165)
        image[60:102,61:63]=(127,177,165)
        image[350:373,23:43]=(132,153,192)
        r=detect(image)
        self.assertIsNotNone(r)
        self.assertAlmostEqual(r.target,80.5/400)
        self.assertAlmostEqual(r.marker,361/400)
        self.assertAlmostEqual(r.band,42/400)
        self.assertTrue(Engine(dict(DEFAULTS)).control.step(r,0))

    def test_unconnected_colored_lines_are_not_a_target(self):
        image=np.full((400,66,3),(44,90,140),np.uint8)
        image[60:62,:]=(107,146,143)
        image[100:102,:]=(107,146,143)
        image[350:373,23:43]=(132,153,192)
        self.assertIsNone(detect(image))

    def collecting(self,loot):
        e=Engine(dict(DEFAULTS));e.prepare_collect(0,loot)
        e.step(.25,None,False,loot)
        e.step(3.25,None,False,loot)
        return e

    def test_item_disappeared_ends_first_attempt_without_inventing_reward(self):
        e=self.collecting((.5,.3))
        for t in (3.3,3.9,4.55):e.step(t,None,False,None)
        self.assertEqual(e.state,'REINICIANDO')
        self.assertEqual(e.collected,0)
        self.assertIn('desapareceu',e.outcome)

    def test_no_item_exits_after_two_attempts(self):
        e=self.collecting(None)
        for t in (3.3,3.9,4.55,5.1):e.step(t,None,False,None)
        self.assertEqual(e.collect_attempts,2)
        e.step(5.36,None,False,None);e.step(8.37,None,False,None)
        for t in (8.4,9,9.65):e.step(t,None,False,None)
        self.assertEqual(e.state,'REINICIANDO')
        self.assertIn('duas tentativas',e.outcome)

    def test_rotating_item_and_repeated_or_stale_frames_do_not_finish(self):
        e=self.collecting((.5,.3))
        e.step(3.3,None,False,None,scene_stamp=3.3)
        e.step(4.55,None,False,None,scene_stamp=3.3)
        self.assertEqual(e.state,'VERIFICANDO_COLETA')
        e.step(4.6,None,False,(.5,.3))
        self.assertEqual(e.absent_frames,0)
        e.step(4.8,None,False,None,scene_valid=False)
        self.assertEqual(e.absent_frames,0)
        e.step(5.1,None,False,(.5,.3))
        self.assertEqual(e.collect_attempts,2)

    def test_reward_ends_collection_immediately(self):
        e=self.collecting((.5,.3))
        e.step(3.3,None,False,None,True)
        self.assertEqual(e.state,'REINICIANDO')
        self.assertEqual(e.collected,1)

    def test_white_overlap_keeps_target_center(self):
        image=np.zeros((300,50,3),np.uint8)
        image[130:180,:]=(80,150,40)
        image[147:159,:]=(235,235,235)
        reading=detect(image)
        self.assertIsNotNone(reading)
        self.assertAlmostEqual(reading.target,154.5/300)
        self.assertAlmostEqual(reading.marker,152.5/300)
        self.assertAlmostEqual(reading.band,50/300)

    def test_large_white_distraction_does_not_hide_marker(self):
        image=np.zeros((300,50,3),np.uint8)
        image[10:90,:]=(235,235,235)
        image[130:165,:]=(80,150,40)
        image[240:250,14:36]=(235,235,235)
        reading=detect(image)
        self.assertIsNotNone(reading)
        self.assertAlmostEqual(reading.marker,244.5/300)
        self.assertIsNone(detect(np.full_like(image,235)))

    def test_periodic_checks_relocate_without_resetting_stable_region(self):
        c=AutoCalibration();first={'roi':[.7,.2,.05,.5],'confidence':.9}
        for _ in range(3):c.observe(first)
        self.assertTrue(c.locked)
        for _ in range(3):self.assertIsNone(c.observe(first))
        moved={'roi':[.73,.2,.05,.5],'confidence':.9}
        for _ in range(2):self.assertIsNone(c.observe(moved))
        self.assertEqual(c.observe(moved),moved['roi'])
        c.check_tracking(None,1)
        self.assertTrue(c.check_tracking(None,1.21))

    def test_recovery_continues_with_active_minigame_and_resumes_control(self):
        e=Engine(dict(DEFAULTS));e.track(0)
        e.step(.02,Reading(.3,.7,.1),True,None)
        for t in (.3,5,21,30):
            actions=e.step(t,None,True,None)
            self.assertEqual(e.state,'PESCANDO')
            self.assertNotIn(('t',True),actions)
        actions=e.step(30.02,Reading(.3,.7,.1),True,None)
        self.assertIn(('mouse',True),actions)
        e.step(34,None,False,None)
        self.assertEqual(e.state,'RESULTADO')

    def test_recovery_still_has_overall_timeout(self):
        e=Engine(dict(DEFAULTS));e.track(0)
        e.step(121,None,True,None)
        self.assertEqual(e.state,'PARADO')

if __name__=='__main__':unittest.main()

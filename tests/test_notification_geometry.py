import sys,unittest
from pathlib import Path
import cv2
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from signals import Signals
from item_history import ItemHistory,parse_reward

class NotificationGeometry(unittest.TestCase):
    def setUp(self):
        self.signals=Signals(Path(__file__).resolve().parents[1]/'src/assets')

    def notification(self,w,h):
        frame=np.zeros((h,w,3),np.uint8)
        t=self.signals.templates['reward'];th,tw=t.shape
        x=1062-(1920-w)//2;y=587-(1080-h)//2
        frame[y:y+th,x:x+tw]=t[:,:,None]
        return frame

    def test_fixed_size_notifications_survive_window_resize(self):
        for w,h in ((800,599),(1280,720),(1920,1009)):
            with self.subTest(size=(w,h)):
                frame=self.notification(w,h)
                result=self.signals.scan(frame)
                self.assertTrue(result['reward'])
                self.assertEqual(result['reward_layout'],'native')
                self.assertEqual(result['reward_crop'].shape,(420,650,3))
                full=self.signals.scan(self.notification(1920,1080))
                np.testing.assert_array_equal(result['reward_crop'],full['reward_crop'])
                self.assertEqual(result['reward_icon'],full['reward_icon'])

    def test_proportional_notifications_keep_existing_path(self):
        frame=cv2.resize(self.notification(1920,1080),(1280,720))
        result=self.signals.scan(frame)
        self.assertTrue(result['reward'])
        self.assertEqual(result['reward_layout'],'scaled')

    def test_compact_notification_above_fullscreen_anchor_is_detected(self):
        frame=np.zeros((599,800,3),np.uint8)
        t=self.signals.templates['reward'];h,w=t.shape
        # In padded 1920x1080 coordinates, center the notice at y=432.
        x=960-w//2-560;y=432-h//2-240
        frame[y:y+h,x:x+w]=t[:,:,None]
        result=self.signals.scan(frame)
        self.assertTrue(result['reward'])
        self.assertEqual(result['reward_layout'],'native')
        self.assertEqual(result['reward_crop'].shape,(420,650,3))

    def test_small_ui_scaled_reward_badge_is_found_without_distorting_it(self):
        frame=np.full((599,800,3),52,np.uint8)
        template=self.signals.templates['reward']
        small=cv2.resize(template,(9,7),interpolation=cv2.INTER_AREA)
        frame[188:195,395:404]=small[:,:,None]
        result=self.signals.scan(frame)
        self.assertTrue(result['reward'])
        self.assertEqual(result['reward_layout'],'scaled')
        self.assertAlmostEqual(result['reward_scale'],.5,delta=.08)

    def test_weak_badge_candidate_exposes_ocr_anchor_without_confirming_reward(self):
        frame=np.full((599,800,3),52,np.uint8)
        template=self.signals.templates['reward']
        small=cv2.resize(template,(9,7),interpolation=cv2.INTER_AREA).astype(float)
        noise=np.random.default_rng(0).normal(0,35,small.shape)
        frame[188:195,395:404]=np.clip(small+noise,0,255).astype(np.uint8)[:,:,None]
        result=self.signals.scan(frame)
        self.assertFalse(result['reward'])
        self.assertIsNotNone(result['reward_candidate_point'])
        self.assertIsNotNone(result['reward_crop_candidate'])
        self.assertGreaterEqual(result['reward_candidate_score'],.70)
        self.assertLess(result['reward_candidate_score'],.91)
        self.assertEqual(result['reward_crop_candidate'].shape,(420,650,3))

    def test_native_collect_maps_click_to_client_coordinates(self):
        frame=np.zeros((599,800,3),np.uint8)
        t=self.signals.templates['collect'];h,w=t.shape
        frame[180:180+h,220:220+w]=t[:,:,None]
        result=self.signals.scan(frame)
        self.assertIsNotNone(result['loot'])
        self.assertAlmostEqual(result['loot'][0],(220+w/2)/800,places=2)
        self.assertAlmostEqual(result['loot'][1],(180+h/2)/599,places=2)

    def test_empty_frames_do_not_confirm_rewards(self):
        for w,h in ((800,599),(1920,1009)):
            result=self.signals.scan(np.zeros((h,w,3),np.uint8))
            self.assertFalse(result['reward']);self.assertIsNone(result['loot'])

    def test_live_crustadon_ocr_geometry_and_scores_are_accepted(self):
        # Transcribed OCR output from the local reproduction; no private image.
        result=parse_reward([
            ([[135,127],[386,127],[386,174],[135,174]],'Crustadon',.9979),
            ([[276,178],[322,178],[322,212],[276,212]],'x1',.8160)],width=1320)
        history=ItemHistory();history.record(0,result)
        self.assertEqual(history.totals(),{'Crustadon':1})
        self.assertTrue(history.by_cycle[0]['identified'])

if __name__=='__main__':unittest.main()

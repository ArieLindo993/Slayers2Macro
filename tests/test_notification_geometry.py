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
                self.assertEqual(result['reward_crop'].shape,(220,650,3))
                full=self.signals.scan(self.notification(1920,1080))
                np.testing.assert_array_equal(result['reward_crop'],full['reward_crop'])
                self.assertEqual(result['reward_icon'],full['reward_icon'])

    def test_proportional_notifications_keep_existing_path(self):
        frame=cv2.resize(self.notification(1920,1080),(1280,720))
        result=self.signals.scan(frame)
        self.assertTrue(result['reward'])
        self.assertEqual(result['reward_layout'],'scaled')

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

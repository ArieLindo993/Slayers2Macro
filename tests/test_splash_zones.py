"""Regressions from anonymized cyan masks, with no game input or recordings."""
import sys,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from splash import SplashReader
import test_circular_flow as flow_tests
import macro


class SplashZones(unittest.TestCase):
    def replay(self,name,armed_at=0):
        data=np.load(ROOT/'tests/fixtures'/name)
        shape=tuple(data['shape']);masks=np.unpackbits(data['masks'],count=int(np.prod(shape))).reshape(shape)
        w,h=map(int,data['frame_size']);x0,y0=map(int,data['origin']);point=tuple(data['point'])
        reader=SplashReader();events=[]
        for i,mask in enumerate(masks):
            rgb=np.zeros((h,w,3),np.uint8);crop=rgb[y0:y0+mask.shape[0],x0:x0+mask.shape[1]]
            crop[mask.astype(bool)]=(70,230,255)
            now=i/float(data['fps'])
            if reader.observe(rgb,point,now,now>=armed_at):events.append(now)
        return events

    def test_recorded_zone_animation_never_triggers_bite(self):
        self.assertEqual(self.replay('splash_zone_masks.npz'),[])

    def test_recorded_true_bite_is_detected_outside_zone(self):
        events=self.replay('splash_bite_masks.npz',2.8)
        self.assertEqual(len(events),1)
        self.assertAlmostEqual(events[0],4.2,delta=.1)

    def test_recorded_bite_is_detected_inside_animated_zone(self):
        events=self.replay('splash_bite_in_zone_masks.npz',.9)
        self.assertEqual(len(events),1)
        self.assertAlmostEqual(events[0],1.3,delta=.1)

    def test_disarmed_frames_learn_static_effect_and_do_not_reset_cooldown(self):
        import cv2
        reader=SplashReader();blank=np.zeros((599,800,3),np.uint8)
        burst=blank.copy()
        for x in (375,400,425):cv2.ellipse(burst,(x,150),(10,4),35,0,360,(70,230,255),-1)
        reader.observe(blank,(.5,.3),0,False)
        self.assertTrue(reader.observe(burst,(.5,.3),.1,True))
        reader.observe(blank,(.5,.3),.2,False)
        self.assertFalse(reader.observe(burst,(.5,.3),.3,True))
        reader.observe(blank,(.5,.3),1.5,False)
        self.assertTrue(reader.observe(burst,(.5,.3),1.7,True))

    def test_timed_out_pending_candidate_can_recover(self):
        import cv2
        reader=SplashReader();blank=np.zeros((599,800,3),np.uint8);burst=blank.copy()
        for x in (380,420):cv2.ellipse(burst,(x,150),(12,4),35,0,360,(70,230,255),-1)
        reader.observe(blank,(.5,.3),0)
        self.assertFalse(reader.observe(burst,(.5,.3),.1))
        self.assertFalse(reader.observe(burst,(.5,.3),.5))
        reader.observe(blank,(.5,.3),.6)
        self.assertFalse(reader.observe(burst,(.5,.3),.7))
        self.assertTrue(reader.observe(burst,(.5,.3),.75))


class SplashInputPriority(unittest.TestCase):
    setUp=flow_tests.CircularApp.setUp
    def test_hook_click_precedes_ring_claim_and_slow_analyses(self):
        app=self.app;app.active=True;app.engine.state='ESPERANDO';app.engine.splash_armed_at=0.
        image=np.zeros((1072,1920,3),np.uint8)
        with patch.object(macro,'game_window',return_value=app.window),patch.object(app,'sample',return_value=image),\
             patch.object(app.splash_reader,'observe',return_value=True),\
             patch.object(app.circle_reader,'read') as ring_read,patch.object(app.claim_reader,'scan') as claim_read,\
             patch.object(app,'update_analyses') as background:
            app.update(1)
            self.assertEqual(app.engine.state,'FISGANDO')
            macro.send_mouse.assert_called_with(True)
            ring_read.assert_not_called();claim_read.assert_not_called();background.assert_not_called()

    def test_hook_mouse_release_precedes_next_capture(self):
        app=self.app;app.active=True;app.held=True;app.engine.state='FISGANDO';app.engine.deadline=1.
        with patch.object(macro,'game_window',return_value=app.window),patch.object(app,'sample') as sample:
            app.update(1.1)
            self.assertEqual(app.engine.state,'AGUARDANDO_CIRCULO')
            macro.send_mouse.assert_called_with(False);sample.assert_not_called()


if __name__=='__main__':unittest.main()

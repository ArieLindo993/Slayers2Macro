import unittest,tempfile,json,sys,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import cv2,numpy as np
from detector import detect
from diagnostics import RuntimeJournal
from local_data import ProfileStore


class Stability(unittest.TestCase):
    def test_text_cannot_be_calibration_marker(self):
        image=np.zeros((300,66,3),np.uint8)
        image[80:110,:]=(80,150,40)
        cv2.putText(image,'WWW',(1,215),cv2.FONT_HERSHEY_SIMPLEX,.65,(240,240,240),2)
        self.assertIsNone(detect(image,require_marker_shape=True))
        image[170:240]=0;image[190:214,23:45]=(235,235,235)
        self.assertIsNotNone(detect(image,require_marker_shape=True))

    def test_old_automatic_profile_is_reset_manual_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'profiles.json';bad=[.02,.52,.034,.23];default=[.73,.29,.034,.37]
            path.write_text(json.dumps({'1920x1080-window-96':{'roi':bad,'automatic':True},
                                        '1920x1080-borderless-96':{'roi':bad,'automatic':False}}))
            profiles=ProfileStore(path)
            self.assertEqual(profiles.load('1920x1080-window-96',default),(default,{}))
            self.assertEqual(profiles.load('1920x1080-borderless-96',default)[0],bad)

    def test_journal_records_stop_and_survives_restart_with_bounded_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'runtime.json';j=RuntimeJournal(path)
            for i in range(220):j.record('started','PESCANDO',True,i)
            reopened=RuntimeJournal(path)
            self.assertEqual(reopened.events[-1]['event'],'previous_session_incomplete')
            reopened.record('fishing_timeout','PESCANDO',False,220)
            data=json.loads(path.read_text())
            self.assertLessEqual(len(data['events']),200)
            self.assertFalse(data['snapshot']['active'])
            self.assertNotIn(tmp,path.read_text())
            self.assertFalse(reopened.record('private message','PESCANDO'))

    def test_calibration_needs_independent_fishing_signal(self):
        if sys.platform!='win32':self.skipTest('Windows app')
        from unittest.mock import patch
        from concurrent.futures import Future
        import macro
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'FISHING_MACRO_DATA_DIR':tmp}):
            app=macro.App();app.root.withdraw()
            try:
                roi=[.72,.28,.04,.37];app.engine.state='PESCANDO'
                for _ in range(3):
                    future=Future();future.set_result({'roi':roi,'confidence':1})
                    app.calibration_job=(future,app.calibration_epoch,10)
                    app.scene={'fishing':False};app.scene_time=10;app.poll_calibration(10.1)
                self.assertFalse(app.calibration.locked)
                for _ in range(3):
                    future=Future();future.set_result({'roi':roi,'confidence':1})
                    app.calibration_job=(future,app.calibration_epoch,10)
                    app.scene={'fishing':True};app.poll_calibration(10.1)
                self.assertTrue(app.calibration.locked)
            finally:app.close()

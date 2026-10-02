"""A slow visual job must not hide the next short-lived reward or calibration."""
from concurrent.futures import Future
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import numpy as np
import macro


class CapturePipeline(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        env = patch.dict(os.environ, {'FISHING_MACRO_DATA_DIR': self.temp.name})
        env.start(); self.addCleanup(env.stop)
        for name in ('send_mouse', 'send_t'):
            mock = patch.object(macro, name)
            mock.start(); self.addCleanup(mock.stop)
        self.app = macro.App()
        self.app.root.withdraw()
        self.addCleanup(self.app.close)
        for timer in self.app.root.tk.call('after', 'info'):
            self.app.root.after_cancel(timer)
        self.app.window = (1, 0, 0, 800, 599)
        self.app.active = True
        self.app.config['cast'] = [.5, .5]
        self.frame = np.full((599, 800, 3), 73, np.uint8)

    def test_pending_scene_does_not_block_calibration_of_new_frame(self):
        app = self.app
        app.engine.track(99.)
        app.scene_job = (Future(), app.scene_epoch, 99., 0)
        app.calibration.begin()
        with patch.object(app, 'sample', return_value=self.frame) as sample, \
                patch.object(app, 'submit_background', side_effect=lambda *a: Future()) as submit, \
                patch.object(macro.time, 'monotonic', return_value=100.):
            app.update_analyses(100., None)
        sample.assert_called_once_with(full=True)
        calls = [call for call in submit.call_args_list
                 if call.args[0] is app.calibration_worker]
        self.assertEqual(len(calls), 1)
        np.testing.assert_array_equal(calls[0].args[2], self.frame)
        self.assertIsNotNone(app.calibration_job)
        self.assertFalse(app.scene_job[0].done())

    def test_pending_scene_and_ocr_preserve_new_compact_reward_frames(self):
        app = self.app
        app.config['auto_calibrate'] = False
        app.engine.state = 'TECLA_T'
        app.scene_job = (Future(), app.scene_epoch, 99., 0)
        app.ocr_job = (Future(), 0, 98.)
        with patch.object(app, 'sample', return_value=self.frame) as sample, \
                patch.object(app, 'submit_ocr', wraps=app.submit_ocr) as submit:
            for stamp in (100., 100.5):
                with patch.object(macro.time, 'monotonic', return_value=stamp):
                    app.update_analyses(stamp, None)
        self.assertEqual(sample.call_count, 2)
        self.assertEqual(submit.call_count, 2)
        self.assertEqual(len(app.ocr_queue), 2)
        self.assertFalse(app.ocr_job[0].done())

    def test_buffered_frame_keeps_pixels_timestamp_and_cycle_until_ocr_is_free(self):
        app = self.app
        first = Future()
        app.ocr_job = (first, 0, 99.)
        image = np.full((80, 140, 3), 127, np.uint8)
        alternate = np.full((90, 180, 3), 88, np.uint8)
        self.assertTrue(app.submit_ocr(image, 100., cycle=0, alternate_crops=(alternate,)))
        image[:] = 0; alternate[:] = 0
        app.cycle_id = 1
        app.engine.cycles = 1; app.engine.unconfirmed = 1
        app.history.record_outcome(0, 'Sem recompensa detectada')
        first.set_result(None)
        delayed = Future()
        with patch.object(app, 'submit_background', return_value=delayed) as submit:
            app.poll_ocr()
        self.assertEqual(app.ocr_job[1:], (0, 100.))
        self.assertTrue(np.all(submit.call_args.args[2] == 127))
        self.assertTrue(np.all(submit.call_args.args[3] == 88))
        delayed.set_result({'name': 'Metal Scraps', 'quantity': 1, 'name_validated': True})
        app.poll_ocr()
        self.assertEqual(app.history.totals(), {'Metal Scraps': 1})
        self.assertEqual(app.engine.collected, 1)
        self.assertNotIn(1, app.history.by_cycle)

    def test_buffer_bound_preserves_previous_and_current_cycle_evidence(self):
        app = self.app
        app.cycle_id = 1
        app.ocr_job = (Future(), 0, 99.)
        image = np.full((40, 80, 3), 90, np.uint8)
        app.submit_ocr(image, 100., cycle=0)
        for index in range(macro.OCR_FRAME_QUEUE_LIMIT + 3):
            app.submit_ocr(image, 101. + index, cycle=1)
        self.assertLessEqual(len(app.ocr_queue), macro.OCR_FRAME_QUEUE_LIMIT)
        self.assertEqual({frame[1] for frame in app.ocr_queue}, {0, 1})

    def test_new_history_discards_pending_frames_and_old_ocr_result(self):
        app = self.app
        old_result = Future()
        app.ocr_job = (old_result, 0, 99.)
        app.submit_ocr(self.frame, 100., cycle=0)
        self.assertTrue(app.ocr_queue)
        app.clear_history()
        self.assertEqual(app.ocr_queue, [])
        self.assertIsNone(app.ocr_job)
        old_result.set_result({'name': 'Metal Scraps', 'quantity': 1})
        app.poll_ocr()
        self.assertEqual(app.history.entries, [])
        self.assertEqual(app.pending_reward_readings, {})
        self.assertEqual(app.engine.collected, 0)

    def test_confirmed_minigame_keeps_marker_overlapping_bright_scenery(self):
        app=self.app;app.engine.track(99.)
        app.scene={'fishing':True};app.scene_time=100.
        frame=np.zeros((300,50,3),np.uint8)
        frame[130:165,:]=(80,150,40)
        frame[240:250,14:36]=(235,235,235)
        frame[200:300,35:36]=(235,235,235)
        self.assertFalse(app.calibration.locked)
        self.assertIsNotNone(app.read_bar(frame,100.2))
        self.assertIsNone(app.read_bar(frame,104.))

    def test_confirmed_notice_upgrades_buffered_hint_from_same_capture(self):
        app=self.app;app.ocr_job=(Future(),0,99.)
        hint=np.full((40,80,3),30,np.uint8)
        notice=np.full((40,80,3),200,np.uint8)
        app.submit_ocr(hint,100.,priority=.5)
        app.submit_ocr(notice,100.,priority=2.)
        self.assertEqual(len(app.ocr_queue),1)
        self.assertEqual(app.ocr_queue[0][0],2.)
        np.testing.assert_array_equal(app.ocr_queue[0][3],notice)


if __name__ == '__main__':
    unittest.main()

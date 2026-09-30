"""Integration regressions: real App, fake game input/capture, private temp data."""
from concurrent.futures import Future
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import macro
from background import BackgroundError, BackgroundBusy


class AppRecovery(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        env=patch.dict(os.environ,{'FISHING_MACRO_DATA_DIR':self.temp.name})
        env.start();self.addCleanup(env.stop)
        for name in ('send_mouse','send_t'):
            mock=patch.object(macro,name);mock.start();self.addCleanup(mock.stop)
        self.app=macro.App();self.app.root.withdraw()
        self.addCleanup(self.app.close)
        for timer in self.app.root.tk.call('after','info'):self.app.root.after_cancel(timer)
        self.app.config['cast']=[.5,.5]
        self.app.window=(1,0,0,1920,1080)
        self.app.active=True

    def completed(self,result=None,error=None):
        future=Future()
        if error:future.set_exception(error)
        else:future.set_result(result)
        return future

    def test_slow_scene_is_consumed_and_old_epoch_or_replay_is_ignored(self):
        app=self.app
        scene={'fishing':False,'loot':(.5,.3),'reward':False}
        app.scene_job=(self.completed(scene),app.scene_epoch,10)
        app.poll_scene(11.2)
        self.assertEqual(app.scene_time,10)
        self.assertEqual(app.scene['loot'],(.5,.3))
        for epoch,stamp in ((app.scene_epoch-1,10.5),(app.scene_epoch,9.9)):
            app.scene_job=(self.completed({'fishing':True}),epoch,stamp)
            app.poll_scene(11.3)
            self.assertEqual(app.scene_time,10)
            self.assertFalse(app.scene['fishing'])
        app.poll_scene(12.6)
        self.assertIsNone(app.scene['loot'])

    def test_calibration_uses_signal_from_its_own_frame_despite_scene_delay(self):
        app=self.app;app.engine.state='PESCANDO'
        candidate={'roi':[.72,.28,.04,.37],'confidence':1}
        app.scene={'fishing':True};app.scene_time=100
        for _ in range(3):
            app.calibration_job=(self.completed({'fishing':False,'candidate':candidate}),app.calibration_epoch,100)
            app.poll_calibration(100.1)
        self.assertFalse(app.calibration.locked)
        app.scene={'fishing':False};app.scene_time=0
        for _ in range(3):
            app.calibration_job=(self.completed({'fishing':True,'candidate':candidate}),app.calibration_epoch,100)
            app.poll_calibration(101.2)
        self.assertTrue(app.calibration.locked)

    def test_failed_analyses_do_not_stop_the_session(self):
        app=self.app
        app.scene_job=(self.completed(error=BackgroundError('test')),app.scene_epoch,10)
        app.calibration_job=(self.completed(error=BackgroundError('test')),app.calibration_epoch,10)
        app.poll_scene(10.5);app.poll_calibration(10.5)
        self.assertTrue(app.active)
        self.assertIsNone(app.scene_job);self.assertIsNone(app.calibration_job)
        with patch.object(app.vision_worker,'submit',side_effect=BackgroundBusy('retiring')):
            self.assertIsNone(app.submit_background(app.vision_worker,abs,-1))
        self.assertTrue(app.active)
        self.assertIn('FALHA_TAREFA_VISUAL',app.session_log.path.read_text('utf-8'))

    def test_same_window_geometry_changes_recover_but_focus_loss_pauses(self):
        app=self.app;app.held=True;app.t_down=True
        with patch.object(macro,'game_window',return_value=(1,20,30,1280,720)):
            with patch.object(macro.time,'monotonic',return_value=10.):
                self.assertFalse(app.sync_window())
            with patch.object(macro.time,'monotonic',return_value=10.3):
                self.assertTrue(app.sync_window())
        self.assertTrue(app.active)
        self.assertFalse(app.held);self.assertFalse(app.t_down)
        self.assertEqual(app.window[3:],(1280,720))
        self.assertEqual(app.engine.state,'RECUPERANDO')
        with patch.object(macro,'game_window',return_value=None):
            self.assertFalse(app.sync_window())
        self.assertFalse(app.active)
        self.assertEqual(app.engine.state,'PARADO')

    def test_window_origin_move_does_not_restart_fishing(self):
        app=self.app;app.held=True;app.t_down=True
        with patch.object(macro,'game_window',return_value=(2,20,30,1920,1080)):
            self.assertTrue(app.sync_window())
        self.assertEqual(app.window,(2,20,30,1920,1080))
        self.assertEqual(app.engine.state,'INICIO')
        self.assertTrue(app.active)

    def test_resize_stability_ignores_temporary_hwnd_and_origin_changes(self):
        app=self.app
        candidates=[(2,20,30,1280,720),(3,85,44,1280,720),(4,90,47,1280,720)]
        with patch.object(macro,'game_window',side_effect=candidates):
            with patch.object(macro.time,'monotonic',side_effect=[20.,20.1,20.26]):
                self.assertFalse(app.sync_window())
                self.assertFalse(app.sync_window())
                self.assertTrue(app.sync_window())
        self.assertEqual(app.window,candidates[-1])
        self.assertEqual(app.engine.state,'RECUPERANDO')

    def test_transient_window_size_jitter_is_debounced(self):
        app=self.app
        with patch.object(macro,'game_window',side_effect=[(1,0,0,1280,720),app.window,(1,0,0,1280,720)]):
            with patch.object(macro.time,'monotonic',return_value=20.):
                self.assertFalse(app.sync_window())
                self.assertTrue(app.sync_window())
                self.assertFalse(app.sync_window())
        self.assertEqual(app.window,(1,0,0,1920,1080))
        self.assertEqual(app.engine.state,'INICIO')
        self.assertTrue(app.active)

    def test_capture_failure_releases_inputs_and_schedules_next_tick(self):
        app=self.app;app.held=True;app.t_down=True
        failure=macro.mss.exception.ScreenShotError('temporary capture loss')
        with patch.object(app,'keys'),patch.object(app,'update',side_effect=failure),patch.object(app.root,'after') as after:
            app.tick()
        self.assertTrue(app.active)
        self.assertFalse(app.held);self.assertFalse(app.t_down)
        self.assertEqual(app.engine.state,'RECUPERANDO')
        after.assert_called_once()
        self.assertGreater(app.capture_retry_at,time.monotonic())

    def test_secondary_capture_error_is_logged_and_does_not_lose_callback(self):
        app=self.app
        with patch.object(app,'keys'),patch.object(app,'update',side_effect=macro.mss.exception.ScreenShotError('test')),patch.object(macro.mss,'MSS',side_effect=OSError('reopen failed')),patch.object(app.root,'after') as after:
            app.tick()
        self.assertFalse(app.active)
        after.assert_called_once()
        log=app.session_log.path.read_text('utf-8')
        self.assertIn('ERRO_INTERNO',log);self.assertIn('origem=',log)

    def test_visual_watchdog_waits_for_evidence_instead_of_pressing_T_blindly(self):
        app=self.app;now=time.monotonic();app.started_at=now-20
        app.engine.prepare_collect(now-2,(.5,.3));app.held=True;app.t_down=True
        app.last_scene=now;app.last_live_preview=now
        with patch.object(macro,'game_window',return_value=app.window),patch.object(app,'sample',return_value=np.zeros((400,66,3),np.uint8)):
            app.update(now)
        self.assertTrue(app.active);self.assertEqual(app.engine.state,'RECUPERANDO')
        self.assertEqual(app.engine.recovery_reason,'vision_unavailable')
        self.assertFalse(app.held);self.assertFalse(app.t_down)

    def test_manual_pause_is_never_undone_by_pending_analysis(self):
        app=self.app;app.stop('Pausado com F4.')
        app.scene_job=(self.completed({'fishing':True,'loot':None,'reward':False}),app.scene_epoch,time.monotonic())
        with patch.object(app,'keys'),patch.object(app,'update') as update,patch.object(app.root,'after'):
            app.tick()
        update.assert_not_called()
        self.assertFalse(app.active);self.assertEqual(app.engine.state,'PARADO')

    def test_direct_notification_ocr_uses_original_frame_and_cycle(self):
        app=self.app;app.engine.track(99)
        crop=np.full((220,650,3),31,dtype=np.uint8)
        scene={'fishing':False,'loot':None,'reward':True,'reward_crop':crop}
        app.scene_job=(self.completed(scene),app.scene_epoch,100,0)
        result=Future()
        with patch.object(app,'submit_background',return_value=result) as submit:
            app.poll_scene(100.2)
        np.testing.assert_array_equal(submit.call_args.args[2],crop)
        self.assertEqual(app.ocr_job[1:],(0,100))
        # A result arriving after the round stays with its original collection.
        app.cycle_id=1;app.engine.cycles=1;app.engine.unconfirmed=1
        app.history.record_outcome(0,'Sem recompensa detectada')
        result.set_result({'name':'Ore','quantity':1});app.poll_ocr()
        self.assertEqual(app.history.by_cycle[0]['name'],'Ore')
        self.assertEqual(app.engine.collected,1);self.assertNotIn(1,app.history.by_cycle)

    def test_reward_notice_waiting_for_a_new_bite_has_no_cycle_owner(self):
        self.assertIsNone(macro.reward_cycle_owner('ESPERANDO',12))
        self.assertEqual(macro.reward_cycle_owner('PESCANDO',12),12)
        self.assertEqual(macro.reward_cycle_owner('REINICIANDO',12),11)

    def test_early_ocr_is_attached_when_the_collection_row_is_created(self):
        app=self.app;reading={'name':'Clown Fish','quantity':1,'name_validated':True}
        app.apply_reward_reading(0,reading)
        self.assertIn(0,app.pending_reward_readings)
        app.engine.cycles=1;app.engine.unconfirmed=1
        app.history.record_outcome(0,'Item desapareceu após T; recompensa não confirmada')
        app.apply_reward_reading(0,app.pending_reward_readings.pop(0))
        self.assertEqual(app.history.totals(),{'Clown Fish':1})
        self.assertEqual(app.engine.collected,1)


if __name__=='__main__':unittest.main()

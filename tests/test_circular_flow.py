"""End-to-end state transitions with synthetic observations and mocked input."""
import sys,tempfile,os,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from circular import CircularReading
from circular_engine import CircularEngine
from splash import SplashReader
from claim import parse_claim,ClaimReader
import macro


def cfg():return dict(macro.DEFAULTS,cast=[.5,.3])
def ring(**kw):return CircularReading((1482,576),166,.9,**kw)


class Flow(unittest.TestCase):
    def test_delayed_first_impact_is_ignored_until_line_settles(self):
        engine=CircularEngine(cfg());engine.state='CLIQUE';engine.deadline=0.
        engine.step(0,None)
        self.assertEqual(engine.state,'ASSENTANDO_LINHA')
        self.assertNotIn(('mouse',True),engine.step(.95,None,splash=True,impact_activity=True))
        self.assertNotIn(('mouse',True),engine.step(1.81,None,splash=True,impact_activity=True))
        self.assertEqual(engine.state,'ASSENTANDO_LINHA')
        engine.step(2.0,None);self.assertEqual(engine.state,'ASSENTANDO_LINHA')
        engine.step(3.12,None);self.assertEqual(engine.state,'ESPERANDO')
        self.assertNotIn(('mouse',True),engine.step(3.3,None,splash=True))
        self.assertEqual(engine.state,'PREPARANDO_FISGADA')
        self.assertIn(('mouse',True),engine.step(3.49,None))

    def test_continuous_zone_activity_cannot_keep_settling_forever(self):
        engine=CircularEngine(cfg());engine.state='CLIQUE';engine.deadline=0.
        engine.step(0,None)
        for now in (.5,1.,1.5,1.9,2.5,3.01,3.6,4.21):engine.step(now,None,impact_activity=True)
        self.assertEqual(engine.state,'ESPERANDO')
        self.assertNotIn(('mouse',True),engine.step(4.3,None,splash=True,impact_activity=True))
        self.assertEqual(engine.state,'ESPERANDO')
        engine.step(4.65,None)
        engine.step(4.7,None,splash=True,impact_activity=True)
        self.assertEqual(engine.state,'PREPARANDO_FISGADA')

    def test_delayed_impact_after_old_guard_never_hooks(self):
        engine=CircularEngine(cfg());engine.state='CLIQUE';engine.deadline=0.
        engine.step(0,None)
        for now in (1.8,2.0,2.57,2.7,2.9):
            self.assertNotIn(('mouse',True),engine.step(now,None,splash=True,impact_activity=True))
            self.assertEqual(engine.state,'ASSENTANDO_LINHA')
        engine.step(3.25,None);self.assertEqual(engine.state,'ESPERANDO')
        engine.step(4.,None,splash=True,impact_activity=True)
        self.assertEqual(engine.state,'PREPARANDO_FISGADA')
        self.assertNotIn(('mouse',True),engine.step(4.17,None))
        self.assertIn(('mouse',True),engine.step(4.19,None))

    def test_pending_hook_is_cancelled_by_pause_or_visible_circle(self):
        for interruption in ('stop','circle'):
            engine=CircularEngine(cfg());engine.state='ESPERANDO';engine.splash_armed_at=0.
            engine.step(1.,None,splash=True)
            if interruption=='stop':engine.stop('Pausado.')
            else:engine.step(1.05,ring(mouse_button='left'))
            self.assertNotIn(('mouse',True),engine.step(1.3,None))
            self.assertNotEqual(engine.state,'FISGANDO')

    def test_wait_for_circle_does_not_repeatedly_reel_each_burst(self):
        engine=CircularEngine(cfg());engine.state='AGUARDANDO_CIRCULO';engine.deadline=5.
        for now in (1.,2.,3.,4.):
            self.assertNotIn(('mouse',True),engine.step(now,None,splash=True))
            self.assertEqual(engine.state,'AGUARDANDO_CIRCULO')
        engine.step(5.1,None);self.assertEqual(engine.state,'POSICIONANDO')

    def test_overdue_hook_is_dropped_instead_of_clicking_an_old_splash(self):
        engine=CircularEngine(cfg());engine.state='ESPERANDO';engine.splash_armed_at=0.
        engine.step(1.,None,splash=True)
        self.assertNotIn(('mouse',True),engine.step(2.,None))
        self.assertEqual(engine.state,'ESPERANDO')

    def test_existing_minigame_can_resume_during_settle_guard(self):
        engine=CircularEngine(cfg());engine.state='CLIQUE';engine.deadline=0.
        engine.step(0,None)
        self.assertIn(('right_mouse',True),engine.step(.5,ring(mouse_button='right')))
        self.assertEqual(engine.state,'PESCANDO')

    def test_five_hundred_consecutive_cycles_keep_advancing(self):
        engine=CircularEngine(cfg());now=1.
        for cycle in range(500):
            now=max(now,engine.deadline+.01);engine.step(now,None)
            now+=.2;engine.step(now,None)
            now+=.3;engine.step(now,None)
            now+=3.1;engine.step(now,None)
            now+=.1;engine.step(now,None,splash=True)
            now+=.2;engine.step(now,None)
            now+=.11;engine.step(now,None)
            now+=.1;engine.step(now,ring(mouse_button='right',key='D',presses=1))
            now+=.2;engine.step(now,ring(mouse_button='left'))
            now+=.2;engine.step(now,ring(complete=True))
            now+=.1;engine.step(now,None,loot=(.6,.4))
            now+=.3;engine.step(now,None,loot=(.6,.4))
            now+=3.1;engine.step(now,None,loot=(.6,.4))
            for _ in range(16):now+=.1;engine.step(now,None)
            self.assertEqual(engine.cycles,cycle+1)
            self.assertEqual(engine.collected,cycle+1)
            self.assertEqual(engine.state,'REINICIANDO')
            self.assertIsNone(engine.mouse_command.button)
            self.assertIsNone(engine.key_command.key)

    def test_cast_splash_simultaneous_mouse_and_keys_and_early_collection(self):
        engine=CircularEngine(cfg())
        self.assertIn(('aim',[.5,.3]),engine.step(1,None))
        self.assertIn(('mouse',True),engine.step(1.2,None))
        engine.step(1.5,None)
        self.assertEqual(engine.state,'ASSENTANDO_LINHA')
        self.assertEqual(engine.step(1.6,None,splash=True),[('mouse',False)]) # initial impact is not armed
        self.assertEqual(engine.step(2.5,None,splash=True),[('mouse',False)])
        engine.step(4.55,None)
        self.assertNotIn(('mouse',True),engine.step(4.6,None,splash=True))
        self.assertEqual(engine.state,'PREPARANDO_FISGADA')
        self.assertIn(('mouse',True),engine.step(4.8,None))
        self.assertEqual(engine.state,'FISGANDO')
        self.assertIn(('mouse',False),engine.step(4.9,None))
        r=ring(mouse_button='right',key='A',presses=2)
        actions=engine.step(5.1,r)
        self.assertIn(('right_mouse',True),actions);self.assertIn(('tap','A'),actions)
        self.assertIn(('tap','A'),engine.step(5.21,r))
        self.assertNotIn(('tap','A'),engine.step(5.4,r))
        self.assertIn(('mouse',True),engine.step(5.5,ring(mouse_button='left')))
        engine.step(6.3,ring(complete=True));self.assertEqual(engine.state,'RESULTADO')
        engine.step(6.4,None,loot=(.6,.4));engine.step(6.7,None,loot=(.6,.4))
        self.assertEqual(engine.state,'TECLA_T')
        engine.step(9.8,None,loot=(.6,.4))
        self.assertEqual(engine.state,'VERIFICANDO_COLETA')
        for t in (9.9,10.2,10.6,11.2,11.4):engine.step(t,None)
        self.assertEqual(engine.cycles,1);self.assertEqual(engine.collected,1)
        self.assertEqual(engine.collect_attempts,0)

    def test_lost_circle_releases_mouse_and_can_reacquire_outside_green(self):
        engine=CircularEngine(cfg());engine.step(1,ring(mouse_button='right'))
        self.assertIn(('mouse',False),engine.step(1.2,None))
        actions=engine.step(1.4,ring(marker=-.25,mouse_button='right'))
        self.assertEqual(engine.state,'PESCANDO');self.assertIn(('right_mouse',True),actions)
        engine.recover(2);self.assertIsNone(engine.mouse_command.button)

    def test_visible_circle_with_unreadable_controls_never_starts_collection(self):
        engine=CircularEngine(cfg());engine.step(1,ring(mouse_button='right'))
        for now in (1.3,2.,3.,5.,8.,12.):
            actions=engine.step(now,None,fishing=True,scene_stamp=now)
            self.assertEqual(engine.state,'PESCANDO')
            self.assertFalse(any(k=='aim' or (k in ('mouse','right_mouse','t') and v) for k,v in actions))
        self.assertIn(('mouse',True),engine.step(12.1,ring(mouse_button='left',marker=.2)))

    def test_tracking_failure_without_claim_never_blindly_presses_t(self):
        engine=CircularEngine(cfg());engine.step(1,ring(mouse_button='right'))
        for now in (1.3,1.8,2.6):engine.step(now,None,scene_stamp=now)
        self.assertEqual(engine.state,'RESULTADO');self.assertFalse(engine.result_confirmed)
        actions=engine.step(4.7,None,scene_stamp=4.7)
        self.assertEqual(engine.state,'REINICIANDO');self.assertEqual(engine.collected,0)
        self.assertNotIn(('t',True),actions);self.assertFalse(any(k=='aim' for k,v in actions))

    def test_old_or_reused_capture_does_not_confirm_circle_disappearance(self):
        engine=CircularEngine(cfg());engine.step(1,ring(mouse_button='left'))
        for now in (1.3,1.4,1.5,2.,3.):engine.step(now,None,scene_stamp=1.3)
        self.assertEqual(engine.state,'PESCANDO')

    def test_claim_after_tracking_loss_is_still_collected_without_delay(self):
        engine=CircularEngine(cfg());engine.step(1,ring(mouse_button='right'))
        engine.step(1.2,None,loot=(.5,.5),scene_stamp=1.2)
        self.assertEqual(engine.state,'MIRANDO_ITEM')
        self.assertIn(('t',True),engine.step(1.5,None,loot=(.5,.5),scene_stamp=1.5))

    def test_ring_reappearing_without_controls_cancels_unconfirmed_result(self):
        engine=CircularEngine(cfg());engine.step(1,ring(mouse_button='right'))
        for now in (1.3,1.8,2.6):engine.step(now,None,scene_stamp=now)
        self.assertEqual(engine.state,'RESULTADO')
        actions=engine.step(4.7,None,fishing=True,scene_stamp=4.7)
        self.assertEqual(engine.state,'PESCANDO');self.assertNotIn(('t',True),actions)

    def test_stale_circle_does_not_send_old_mouse_or_key_commands(self):
        engine=CircularEngine(cfg());engine.track(1.)
        actions=engine.step(2.,ring(mouse_button='right',key='A',presses=2),scene_stamp=1.1)
        self.assertFalse(any(k=='tap' or (k in ('mouse','right_mouse') and v) for k,v in actions))

    def test_result_name_is_not_reward_and_stale_prompt_is_ignored(self):
        engine=CircularEngine(cfg());engine.track(0)
        engine.step(1,ring(complete=True))
        engine.step(2,None,loot=(.5,.5),scene_stamp=0,scene_valid=False)
        self.assertEqual(engine.collected,0);self.assertEqual(engine.state,'RESULTADO')

    def test_direct_notification_while_circle_active_is_latched(self):
        engine=CircularEngine(cfg());engine.step(1,ring(),reward=True)
        engine.step(2,ring(complete=True));engine.step(2.1,None)
        self.assertEqual(engine.collected,1)

    def test_splash_is_temporal_and_rearms_without_spamming(self):
        import cv2
        reader=SplashReader();image=np.zeros((599,800,3),np.uint8)
        self.assertFalse(reader.observe(image,(.5,.3),0))
        cv2.ellipse(image,(380,158),(12,4),-40,0,360,(70,230,255),-1)
        cv2.ellipse(image,(420,155),(12,4),40,0,360,(70,230,255),-1)
        self.assertFalse(reader.observe(image,(.5,.3),.1))
        self.assertTrue(reader.observe(image,(.5,.3),.15))
        self.assertFalse(reader.observe(image,(.5,.3),.2))
        reader.reset();self.assertFalse(reader.observe(image,(.5,.3),1)) # static cyan is not splash

    def test_claim_name_weight_and_no_unrelated_text_confirmation(self):
        box=[[0,0],[300,0],[300,20],[0,20]]
        parsed=parse_claim([(box,"Chablas's Razorjaw, 3.50 kg",.99)],'one')
        self.assertEqual(parsed['weight_kg'],3.5);self.assertEqual(parsed['quantity'],1)
        self.assertEqual(parsed['source'],'claim')
        self.assertIsNone(parse_claim([(box,'Claim',.99)]))
        self.assertIsNone(parse_claim([(box,'Clown Fish, 1.20 kg',.5)]))


class CircularApp(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        env=patch.dict(os.environ,{'FISHING_MACRO_DATA_DIR':self.temp.name});env.start();self.addCleanup(env.stop)
        for name in ('send_mouse','send_t','send_fishing_key'):
            mock=patch.object(macro,name);mock.start();self.addCleanup(mock.stop)
        self.app=macro.App();self.app.root.withdraw();self.addCleanup(self.app.close)
        for timer in self.app.root.tk.call('after','info'):self.app.root.after_cancel(timer)
        self.app.config['cast']=[.5,.3];self.app.window=(1,0,0,1920,1072)

    def test_default_path_controls_and_pause_releases_all_inputs(self):
        app=self.app;self.assertIsInstance(app.engine,CircularEngine);app.active=True
        with patch.object(macro,'game_window',return_value=app.window):
            app.execute([('mouse',True),('tap','A'),('t',True)])
            self.assertTrue(app.held);self.assertIn('A',app.fishing_keys)
            app.stop('Pausado.')
            self.assertFalse(app.held);self.assertFalse(app.t_down);self.assertFalse(app.fishing_keys)
            macro.send_fishing_key.assert_any_call('A',False)

    def test_manual_circle_profiles_are_separate_and_survive_resize(self):
        app=self.app;app.choose_profile(app.window)
        app.save_selection([.60,.25,.32,.50]);self.assertFalse(app.config['auto_calibrate'])
        app.choose_profile((1,0,0,800,599));self.assertTrue(app.config['auto_calibrate'])
        app.choose_profile(app.window)
        self.assertEqual(app.config['circle_roi'],[.60,.25,.32,.50]);self.assertFalse(app.config['auto_calibrate'])

    def test_live_observations_reach_new_engine_without_legacy_bar(self):
        app=self.app;app.active=True
        image=np.full((1072,1920,3),35,np.uint8)
        with patch.object(macro,'game_window',return_value=app.window),patch.object(app,'sample',return_value=image),\
             patch.object(app.circle_reader,'read',return_value=ring(mouse_button='right',key='D',presses=1)),\
             patch.object(app.claim_reader,'scan',return_value=None),patch.object(app,'update_analyses'),\
             patch.object(app,'read_bar',side_effect=AssertionError('legacy bar used')):
            app.update(1)
            self.assertEqual(app.engine.state,'PESCANDO')
            macro.send_mouse.assert_called_with(True,'right');macro.send_fishing_key.assert_called_with('D',True)

    def test_control_is_applied_before_background_work(self):
        app=self.app;app.active=True;image=np.zeros((1072,1920,3),np.uint8)
        def background(*args):self.assertTrue(app.right_held)
        with patch.object(macro,'game_window',return_value=app.window),patch.object(app,'sample',return_value=image),\
             patch.object(app.circle_reader,'read',return_value=ring(mouse_button='right')),\
             patch.object(app.claim_reader,'scan',return_value=None),patch.object(app,'update_analyses',side_effect=background):
            app.update(1.)

    def test_missing_controls_are_rescanned_on_every_tracking_tick(self):
        app=self.app;app.active=True;app.engine.track(1.);app.diagnostic_var.set(False)
        app.circle_reader.visible=True;app.circle_reader.stats={'reason':'target_missing'}
        image=np.zeros((1072,1920,3),np.uint8)
        with patch.object(macro,'game_window',return_value=app.window),patch.object(app,'sample',return_value=image),\
             patch.object(app.circle_reader,'read',return_value=None) as read,\
             patch.object(app,'update_analyses'),patch.object(macro.time,'monotonic',return_value=2.):
            for now in (2.,2.02,2.04,2.06):app.update(now)
        self.assertEqual(read.call_count,4);self.assertEqual(app.engine.state,'PESCANDO')
        self.assertFalse(app.held);self.assertFalse(app.right_held);self.assertFalse(app.t_down)

    def test_missing_needle_does_not_flood_item_ocr(self):
        app=self.app;app.engine.track(1.);app.last_scene=2.
        image=np.zeros((1072,1920,3),np.uint8)
        with patch.object(app,'submit_ocr') as ocr:
            app.update_analyses(2.1,None,image,2.1)
        ocr.assert_not_called()

    def test_diagnostic_records_circular_reason_without_arbitrary_fields(self):
        import json
        from diagnostics import Diagnostics
        path=Path(self.temp.name)/'test_diagnostics'
        diag=Diagnostics(path)
        self.assertTrue(diag.save(np.zeros((50,50,3),np.uint8),'PESCANDO','current',
            self.app.metrics.summary(),2.,{'reason':'target_missing','ring_score':.65,'private':'omit'}))
        data=json.loads(next(path.glob('*.json')).read_text())
        self.assertEqual(data['circular'],{'reason':'target_missing','ring_score':.65})

    def test_unconfirmed_splash_has_local_diagnostic_with_bounded_fields(self):
        import json
        from diagnostics import Diagnostics
        path=Path(self.temp.name)/'water_diagnostics';diag=Diagnostics(path)
        self.assertTrue(diag.save(np.zeros((50,50,3),np.uint8),'ESPERANDO','current',
            self.app.metrics.summary(),2.,{'flash_mass':120.,'armed':True,'private':'omit'},'splash_unconfirmed'))
        data=json.loads(next(path.glob('*.json')).read_text())
        self.assertEqual(data['event'],'splash_unconfirmed');self.assertEqual(data['state'],'ESPERANDO')
        self.assertEqual(data['splash'],{'flash_mass':120.,'armed':True})


if __name__=='__main__':unittest.main()

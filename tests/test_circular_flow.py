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
        engine.step(2.12,None);self.assertEqual(engine.state,'ESPERANDO')
        self.assertIn(('mouse',True),engine.step(2.3,None,splash=True))

    def test_continuous_zone_activity_cannot_keep_settling_forever(self):
        engine=CircularEngine(cfg());engine.state='CLIQUE';engine.deadline=0.
        engine.step(0,None)
        for now in (.5,1.,1.5,1.9,2.5,3.01):engine.step(now,None,impact_activity=True)
        self.assertEqual(engine.state,'ESPERANDO')

    def test_existing_minigame_can_resume_during_settle_guard(self):
        engine=CircularEngine(cfg());engine.state='CLIQUE';engine.deadline=0.
        engine.step(0,None)
        self.assertIn(('mouse',True),engine.step(.5,ring(hold=True)))
        self.assertEqual(engine.state,'PESCANDO')

    def test_five_hundred_consecutive_cycles_keep_advancing(self):
        engine=CircularEngine(cfg());now=1.
        for cycle in range(500):
            now=max(now,engine.deadline+.01);engine.step(now,None)
            now+=.2;engine.step(now,None)
            now+=.3;engine.step(now,None)
            now+=1.9;engine.step(now,None)
            now+=.1;engine.step(now,None,splash=True)
            now+=.11;engine.step(now,None)
            now+=.1;engine.step(now,ring(hold=True,key='D',presses=1))
            now+=.2;engine.step(now,ring(hold=False))
            now+=.2;engine.step(now,ring(complete=True))
            now+=.1;engine.step(now,None,loot=(.6,.4))
            now+=.3;engine.step(now,None,loot=(.6,.4))
            now+=3.1;engine.step(now,None,loot=(.6,.4))
            for _ in range(16):now+=.1;engine.step(now,None)
            self.assertEqual(engine.cycles,cycle+1)
            self.assertEqual(engine.collected,cycle+1)
            self.assertEqual(engine.state,'REINICIANDO')
            self.assertFalse(engine.mouse_command.held)
            self.assertIsNone(engine.key_command.key)

    def test_cast_splash_simultaneous_mouse_and_keys_and_early_collection(self):
        engine=CircularEngine(cfg())
        self.assertIn(('aim',[.5,.3]),engine.step(1,None))
        self.assertIn(('mouse',True),engine.step(1.2,None))
        engine.step(1.5,None)
        self.assertEqual(engine.state,'ASSENTANDO_LINHA')
        self.assertEqual(engine.step(1.6,None,splash=True),[('mouse',False)]) # initial impact is not armed
        self.assertEqual(engine.step(2.5,None,splash=True),[('mouse',False)])
        engine.step(3.35,None)
        self.assertIn(('mouse',True),engine.step(3.5,None,splash=True))
        self.assertEqual(engine.state,'FISGANDO')
        self.assertIn(('mouse',False),engine.step(3.6,None))
        r=ring(hold=True,key='A',presses=2)
        actions=engine.step(3.8,r)
        self.assertIn(('mouse',True),actions);self.assertIn(('tap','A'),actions)
        self.assertIn(('tap','A'),engine.step(3.91,r))
        self.assertNotIn(('tap','A'),engine.step(4.1,r))
        self.assertIn(('mouse',False),engine.step(4.2,ring(hold=False)))
        engine.step(5,ring(complete=True));self.assertEqual(engine.state,'RESULTADO')
        engine.step(5.1,None,loot=(.6,.4));engine.step(5.4,None,loot=(.6,.4))
        self.assertEqual(engine.state,'TECLA_T')
        engine.step(8.5,None,loot=(.6,.4))
        self.assertEqual(engine.state,'VERIFICANDO_COLETA')
        for t in (8.6,8.9,9.3,9.9,10.1):engine.step(t,None)
        self.assertEqual(engine.cycles,1);self.assertEqual(engine.collected,1)
        self.assertEqual(engine.collect_attempts,0)

    def test_lost_circle_releases_mouse_and_can_reacquire_outside_green(self):
        engine=CircularEngine(cfg());engine.step(1,ring(hold=True))
        self.assertIn(('mouse',False),engine.step(1.2,None))
        actions=engine.step(1.4,ring(marker=-.25,hold=True))
        self.assertEqual(engine.state,'PESCANDO');self.assertIn(('mouse',True),actions)
        engine.recover(2);self.assertFalse(engine.mouse_command.held)

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
             patch.object(app.circle_reader,'read',return_value=ring(hold=True,key='D',presses=1)),\
             patch.object(app.claim_reader,'scan',return_value=None),patch.object(app,'update_analyses'),\
             patch.object(app,'read_bar',side_effect=AssertionError('legacy bar used')):
            app.update(1)
            self.assertEqual(app.engine.state,'PESCANDO')
            macro.send_mouse.assert_called_with(True);macro.send_fishing_key.assert_called_with('D',True)


if __name__=='__main__':unittest.main()

import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from detector import Reading
from engine import Engine


CONFIG={'cast':[.5,.5],'max_cast':3,'cast_hold':.25,'wait_seconds':20,
        'max_collect':5,'t_hold':3,'collect_timeout':35,'recast_seconds':1.5,
        'result_wait':2,'auto_calibrate':True,'anticipation':.1}


class EngineEndurance(unittest.TestCase):
    def test_processing_delay_is_not_counted_twice_when_expiring_evidence(self):
        for latency in (1.2,1.6,2.4):
            for fishing in (False,True):
                with self.subTest(latency=latency,fishing=fishing):
                    engine=Engine(dict(CONFIG));engine.recover(100)
                    for index in range(1,25):
                        stamp=100+index*latency;arrival=stamp+latency
                        engine.step(arrival,None,fishing,None,scene_stamp=stamp)
                        if engine.state!='RECUPERANDO':break
                        # The previous capture may expire during processing of
                        # the next one; this tick is not a new negative result.
                        engine.step(arrival+latency-.05,None,fishing,None,
                                    scene_stamp=stamp,scene_valid=False)
                    self.assertEqual(engine.state,'PESCANDO' if fishing else 'POSICIONANDO')
                    self.assertLess(arrival,120)

    def test_recovery_survives_gaps_between_slow_independent_captures(self):
        engine=Engine(dict(CONFIG));engine.cycles=1430;engine.recover(100)
        for index in range(1,40):
            captured=100+index*.7
            engine.step(captured+.7,None,False,None,scene_stamp=captured)
            if engine.state!='RECUPERANDO':break
            engine.step(captured+1.05,None,False,None,scene_stamp=captured,scene_valid=False)
        self.assertEqual(engine.state,'POSICIONANDO')
        self.assertLess(captured+.7,117)
        self.assertEqual(engine.cycles,1430)

    def test_recovery_rejects_old_replayed_and_future_observations(self):
        engine=Engine(dict(CONFIG));engine.recover(100)
        engine.step(116,None,False,None,scene_stamp=99)
        self.assertEqual(engine.recovery_frames,0)
        engine.step(116,None,False,None,scene_stamp=116)
        self.assertEqual(engine.recovery_frames,1)
        for now,stamp in ((116.1,116),(116.2,115.9),(116.3,117)):
            engine.step(now,None,False,None,scene_stamp=stamp)
            self.assertEqual(engine.state,'RECUPERANDO')
            self.assertEqual(engine.recovery_frames,1)
        engine.step(116.7,None,False,None,scene_stamp=116.7)
        self.assertEqual(engine.state,'POSICIONANDO')

    def test_long_gap_requires_two_new_empty_observations(self):
        engine=Engine(dict(CONFIG));engine.recover(100)
        engine.step(101,None,False,None,scene_stamp=101)
        engine.step(120,None,False,None,scene_stamp=120)
        self.assertEqual(engine.state,'RECUPERANDO')
        self.assertEqual(engine.recovery_frames,1)
        engine.step(120.7,None,False,None,scene_stamp=120.7)
        self.assertEqual(engine.state,'POSICIONANDO')

    def test_same_fishing_scene_does_not_confirm_twice(self):
        engine=Engine(dict(CONFIG));engine.recover(100)
        for now in (101,101.02,101.2):
            engine.step(now,None,True,None,scene_stamp=100.8)
        self.assertEqual(engine.state,'RECUPERANDO')
        engine.step(101.85,None,True,None,scene_stamp=100.8,scene_valid=False)
        engine.step(102,None,True,None,scene_stamp=101.5)
        self.assertEqual(engine.state,'PESCANDO')

    def test_recovery_ignores_stale_positive_and_stale_item(self):
        engine=Engine(dict(CONFIG));engine.recover(100)
        for now in (121,121.02,125):
            engine.step(now,None,True,(.5,.3),scene_stamp=100,scene_valid=False)
        self.assertEqual(engine.state,'RECUPERANDO')
        self.assertEqual(engine.collect_attempts,0)

    def test_fishing_observation_clears_empty_recovery_evidence(self):
        engine=Engine(dict(CONFIG));engine.recover(100)
        engine.step(114.2,None,False,None,scene_stamp=114.2)
        engine.step(114.8,None,True,None,scene_stamp=114.8)
        engine.step(115.4,None,False,None,scene_stamp=115.4)
        self.assertEqual(engine.state,'RECUPERANDO')
        self.assertEqual(engine.recovery_frames,1)
        engine.step(116,None,False,None,scene_stamp=116)
        self.assertEqual(engine.state,'POSICIONANDO')

    def test_vision_watchdog_recovery_waits_for_fresh_observations(self):
        engine=Engine(dict(CONFIG));engine.cycles=14;engine.prepare_collect(0,(.5,.3))
        actions=engine.recover(4,reason='vision_unavailable')
        self.assertEqual(engine.recovery_reason,'vision_unavailable')
        self.assertIn(('mouse',False),actions);self.assertIn(('t',False),actions)
        engine.step(20,None,False,None,scene_stamp=2,scene_valid=False)
        self.assertEqual(engine.state,'RECUPERANDO')
        engine.step(20.1,None,False,None,scene_stamp=20.1)
        engine.step(20.8,None,False,None,scene_stamp=20.8)
        self.assertEqual(engine.state,'POSICIONANDO')
        self.assertEqual(engine.cycles,14)

    def test_missing_marker_timeout_recovers_and_does_not_repeat_false_fishing(self):
        engine=Engine(dict(CONFIG));engine.cycles=9;engine.track(0)
        actions=engine.step(121,None,True,None)
        self.assertEqual(engine.state,'RECUPERANDO')
        self.assertIn(('mouse',False),actions);self.assertIn(('t',False),actions)
        self.assertFalse(any(kind=='stop' for kind,_ in actions))
        for now in (122,122.7,135.5,136.2):
            engine.step(now,None,True,None,scene_stamp=now)
        self.assertEqual(engine.state,'POSICIONANDO')
        self.assertEqual(engine.cycles,9)

    def test_collection_after_vision_recovery_gets_a_new_attempt_deadline(self):
        engine=Engine(dict(CONFIG));engine.prepare_collect(0,(.5,.3))
        engine.recover(40,reason='vision_unavailable')
        engine.step(41,None,False,(.5,.3))
        self.assertEqual(engine.state,'MIRANDO_ITEM')
        self.assertEqual(engine.collect_started,41)
        actions=engine.step(41.25,None,False,(.5,.3))
        self.assertEqual(engine.state,'TECLA_T')
        self.assertIn(('t',True),actions)

    def test_timeout_recovery_still_accepts_real_marker_and_manual_stop(self):
        engine=Engine(dict(CONFIG));engine.track(0);engine.step(121,None,True,None)
        reading=Reading(.3,.7,.1)
        engine.step(122,reading,True,None);engine.step(122.02,reading,True,None)
        self.assertEqual(engine.state,'PESCANDO')
        self.assertIn(('mouse',True),engine.step(122.04,reading,True,None))
        engine.stop('Parado com F10.')
        self.assertEqual(engine.step(500,reading,True,None),[])
        self.assertEqual(engine.state,'PARADO')

    def test_valid_tracking_is_not_interrupted_after_two_minutes(self):
        engine=Engine(dict(CONFIG));engine.track(0)
        reading=Reading(.3,.7,.1)
        for now in range(1,241):
            actions=engine.step(now,reading,True,None)
            self.assertEqual(engine.state,'PESCANDO')
            self.assertFalse(any(kind=='stop' for kind,_ in actions))

    def test_eight_hours_of_actual_cast_states_with_slow_scenes(self):
        engine=Engine(dict(CONFIG));engine.cycles=1430
        next_capture=0.;stamp=None;casts=0;retries=0;mouse=False;t=False
        for tick in range(8*3600*10):
            now=tick/10
            if now>=next_capture:
                stamp=now-.7;next_capture=now+.7
            actions=engine.step(now,None,False,None,scene_stamp=stamp,scene_valid=now-stamp<1)
            for kind,value in actions:
                if kind=='mouse':mouse=value
                if kind=='t':t=value
                if kind=='aim':casts+=1
                if kind=='recover':retries+=1
            self.assertNotEqual(engine.state,'PARADO')
            if engine.state=='RECUPERANDO':
                self.assertFalse(mouse);self.assertFalse(t)
                self.assertLessEqual(now,engine.deadline+2)
        self.assertGreater(casts,500)
        self.assertGreater(retries,100)
        self.assertEqual(engine.cycles,1430)


if __name__=='__main__':unittest.main()

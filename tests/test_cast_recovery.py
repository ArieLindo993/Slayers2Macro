import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from engine import Engine
from detector import Reading
from macro import DEFAULTS

class CastRecovery(unittest.TestCase):
    def exhausted(self):
        e=Engine(dict(DEFAULTS,cast=[.5,.5]));e.cycles=93
        e.state='ESPERANDO';e.attempts=3;e.deadline=100
        actions=e.step(100,None,False,None)
        self.assertEqual(e.state,'RECUPERANDO')
        self.assertIn(('recover',1),actions)
        self.assertNotIn(('stop',e.message),actions)
        return e

    def test_recorded_failure_recovers_preserving_history(self):
        e=self.exhausted()
        self.assertEqual(e.step(101,None,False,None),[])
        actions=e.step(115,None,False,None)
        self.assertEqual(e.state,'POSICIONANDO');self.assertEqual(e.cycles,93)
        self.assertEqual(e.attempts,1);self.assertIn(('aim',[.5,.5]),actions)

    def test_stale_or_duplicate_scenes_do_not_trigger_new_clicks(self):
        e=self.exhausted()
        for t in (101,115,120):e.step(t,None,False,None,scene_valid=False)
        self.assertEqual(e.state,'RECUPERANDO')
        for t in (121,121.1,121.2):e.step(t,None,False,None,scene_stamp=121)
        self.assertEqual(e.state,'RECUPERANDO')
        e.step(121.5,None,False,None,scene_stamp=121.5)
        self.assertEqual(e.state,'POSICIONANDO')

    def test_game_or_item_preempts_retry_and_manual_stop_stays_stopped(self):
        e=self.exhausted();r=Reading(.5,.6,.1)
        e.step(101,r,True,None);e.step(101.02,r,True,None)
        self.assertEqual(e.state,'PESCANDO');self.assertEqual(e.recovery_count,0)
        e=self.exhausted();e.step(101,None,False,(.5,.3))
        self.assertEqual(e.state,'MIRANDO_ITEM')
        e=self.exhausted();e.stop('Parado com F10.')
        self.assertEqual(e.step(200,None,False,None),[]);self.assertEqual(e.state,'PARADO')

    def test_repeated_failures_back_off_and_never_accumulate_pressed_inputs(self):
        e=self.exhausted();now=100
        for iteration in range(1,101):
            self.assertEqual(e.deadline-now,min(60,15*iteration))
            e.step(now+1,None,False,None)
            now=e.deadline;e.step(now,None,False,None)
            self.assertEqual(e.state,'POSICIONANDO')
            # Três lançamentos falharam de novo: reproduz a condição de entrada.
            now+=61;e.state='ESPERANDO';e.attempts=3;e.deadline=now
            actions=e.step(now,None,False,None)
            self.assertIn(('mouse',False),actions);self.assertIn(('t',False),actions)
            self.assertEqual(e.state,'RECUPERANDO')
        self.assertGreater(now,10000)

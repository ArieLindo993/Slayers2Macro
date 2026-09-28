import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from engine import Engine
from macro import DEFAULTS

class CollectionObservations(unittest.TestCase):
    def begin(self,loot=None):
        e=Engine(dict(DEFAULTS));e.prepare_collect(0,loot)
        e.step(.25,None,False,loot);e.step(3.25,None,False,loot)
        return e

    def slow_absence(self,e,base):
        for capture in (base,base+.8,base+1.6):
            e.step(capture+.7,None,False,None,scene_stamp=capture,scene_valid=True)
            if e.state!='VERIFICANDO_COLETA':break
            if e.state=='VERIFICANDO_COLETA':
                e.step(capture+1.05,None,False,None,scene_stamp=capture,scene_valid=False)

    def test_disappearance_survives_stale_intervals_between_fresh_frames(self):
        e=self.begin((.5,.3));self.slow_absence(e,3.3)
        self.assertEqual(e.state,'REINICIANDO');self.assertEqual(e.collected,0)
        self.assertIn('desapareceu',e.outcome)

    def test_empty_rod_stops_after_second_attempt_with_slow_processing(self):
        e=self.begin();self.slow_absence(e,3.3)
        self.assertEqual(e.state,'MIRANDO_ITEM');self.assertEqual(e.collect_attempts,2)
        e.step(6,None,False,None);e.step(9,None,False,None)
        self.slow_absence(e,9.1)
        self.assertEqual(e.state,'REINICIANDO')
        self.assertEqual(e.outcome,'Nenhum item identificado em duas tentativas')

    def test_no_extra_T_attempts_without_new_evidence(self):
        e=self.begin()
        for t in (4,5,8,12,20):
            actions=e.step(t,None,False,None,scene_stamp=3,scene_valid=False)
            self.assertNotIn(('t',True),actions)
        self.assertEqual(e.state,'VERIFICANDO_COLETA');self.assertEqual(e.collect_attempts,1)
        e.step(36,None,False,None,scene_valid=False)
        self.assertEqual(e.state,'REINICIANDO');self.assertEqual(e.collected,0)

    def test_long_observation_gap_restarts_absence_window(self):
        e=self.begin((.5,.3))
        e.step(3.4,None,False,None,scene_stamp=3.3)
        e.step(7,None,False,None,scene_stamp=6.9)
        self.assertEqual(e.absent_frames,1);self.assertEqual(e.state,'VERIFICANDO_COLETA')

    def test_item_reappearance_still_repeats_collection(self):
        e=self.begin((.5,.3));e.step(3.4,None,False,None)
        e.step(4,None,False,(.5,.3))
        self.assertEqual(e.state,'MIRANDO_ITEM');self.assertEqual(e.collect_attempts,2)

    def test_two_distinct_frames_finish_after_short_absence(self):
        e=self.begin((.5,.3))
        e.step(3.3,None,False,None,scene_stamp=3.3)
        e.step(3.8,None,False,None,scene_stamp=3.3)
        self.assertEqual(e.absent_frames,1)
        self.assertEqual(e.state,'VERIFICANDO_COLETA')
        e.step(3.91,None,False,None,scene_stamp=3.91)
        self.assertEqual(e.state,'REINICIANDO')

    def test_old_default_migrates_once_custom_value_survives(self):
        import tempfile,json,os
        from unittest.mock import patch
        import macro
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'FISHING_MACRO_DATA_DIR':tmp}):
            path=Path(tmp)/'config.json';path.write_text(json.dumps({'result_wait':12}))
            app=macro.App();app.root.withdraw()
            try:
                self.assertEqual(app.config['result_wait'],2)
                app.config['result_wait']=12;app.save()
            finally:app.close()
            app=macro.App();app.root.withdraw()
            try:self.assertEqual(app.config['result_wait'],12)
            finally:app.close()

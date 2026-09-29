import os,sys,tempfile,unittest
from pathlib import Path
from concurrent.futures import Future
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from item_history import ItemHistory,parse_reward,RewardReader

def line(text,x,y,width=60,height=16):
    return ([[x,y],[x+width,y],[x+width,y+height],[x,y+height]],text,.96)

class HistoryCounts(unittest.TestCase):
    def test_aliases_share_total_and_do_not_merge_other_species(self):
        h=ItemHistory()
        for cycle,name in enumerate(('clown','clown f','Clown Fish','CLOWNFISH','Clown Triggerfish','Blue Fish','blue fish')):
            h.record(cycle,{'name':name,'quantity':1})
        self.assertEqual(h.totals(),{'Clown Fish':4,'Clown Triggerfish':1,'Blue Fish':2})
        self.assertEqual(h.total,7)

    def test_split_words_are_joined_without_new_item_heading(self):
        result=parse_reward([line('NEW',0,0),line('Clown',20,25),line('Fish',85,27),line('x1',40,50)])
        self.assertEqual(result['name'],'Clown Fish');self.assertEqual(result['quantity'],1)
        self.assertIsNone(parse_reward([line('Clown Fish',20,25)]))

    def test_compact_reward_name_and_quantity_on_same_baseline(self):
        result=parse_reward([line('Clown Fish',20,50,110),line('x1',145,50,30)])
        self.assertEqual(result['name'],'Clown Fish');self.assertEqual(result['quantity'],1)

    def test_crop_keeps_taller_first_reward_layout(self):
        import numpy as np
        frame=np.zeros((1080,1920,3),dtype=np.uint8)
        frame[545:555,1020:1100]=255
        crop=RewardReader.crop(frame)
        self.assertEqual(crop.shape,(220,650,3));self.assertGreater(crop.sum(),0)

    def test_late_first_reward_updates_counter_once_and_original_cycle(self):
        import macro
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'FISHING_MACRO_DATA_DIR':tmp}):
            app=macro.App();app.root.withdraw()
            for timer in app.root.tk.call('after','info'):app.root.after_cancel(timer)
            try:
                app.cycle_id=1;app.engine.cycles=1;app.engine.unconfirmed=1
                app.history.record_outcome(0,'Item desapareceu após T; recompensa não confirmada')
                future=Future();future.set_result({'name':'clown f','quantity':1})
                app.ocr_job=(future,0,0);app.poll_ocr()
                self.assertEqual(app.engine.collected,1);self.assertEqual(app.engine.unconfirmed,0)
                self.assertEqual(app.history.totals(),{'Clown Fish':1})
                self.assertNotIn(1,app.history.by_cycle)
                self.assertIn('1 coletas confirmadas',app.counter.get())
                app.confirmation_jobs=[(future,0)];app.poll_ocr()
                self.assertEqual(app.engine.collected,1);self.assertEqual(len(app.history.entries),1)
                self.assertIn('COLETA_CONFIRMADA_TARDIA',app.session_log.path.read_text('utf-8'))
                app.history=ItemHistory();app.apply_reward_reading(0,future.result())
                self.assertEqual(app.history.entries,[])
            finally:app.close()

if __name__=='__main__':unittest.main()

import json,os,sys,tempfile,unittest
from pathlib import Path
from concurrent.futures import Future
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from item_icons import reward_icon,decode_icon,MAX_ICONS
from item_history import ItemHistory

def icon(color=(70,190,150)):
    frame=np.zeros((1080,1920,3),np.uint8)
    frame[554:602,976:1020]=color
    return reward_icon(frame,(1075.5,596.5))

class ItemIcons(unittest.TestCase):
    def test_crop_uses_reward_anchor_and_normalized_resolution(self):
        frame=np.zeros((1080,1920,3),np.uint8);frame[554:602,976:1020]=(70,190,150)
        from PIL import Image
        for width,height in ((1920,1080),(1280,720)):
            source=np.array(Image.fromarray(frame).resize((width,height)))
            decoded=decode_icon(reward_icon(source,(1075.5,596.5)))
            self.assertEqual(decoded.size,(44,48));self.assertEqual(decoded.getpixel((22,24)),(70,190,150))
        self.assertIsNone(reward_icon(frame,None))
        self.assertIsNone(reward_icon(frame,(10,10)))
        self.assertIsNone(decode_icon('not a png'))

    def test_icons_saved_once_per_identified_item_and_csv_stays_compatible(self):
        with tempfile.TemporaryDirectory() as tmp:
            h=ItemHistory(tmp);h.record(1,{'name':'Fish','quantity':1})
            self.assertTrue(h.set_icon(1,icon()))
            h.record(2,{'name':'Fish','quantity':2})
            self.assertFalse(h.set_icon(2,icon((100,50,70))))
            self.assertEqual(h.by_cycle[1]['icon'],h.by_cycle[2]['icon'])
            saved=json.loads(h.path.read_text('utf-8'))
            self.assertEqual(len(saved['icons']),1);self.assertEqual(h.total,3)
            self.assertNotIn(tmp,h.path.read_text('utf-8'))
            self.assertNotIn('icon',h.path.with_suffix('.csv').read_text('utf-8-sig'))

    def test_late_name_merges_icons_and_unconfirmed_never_has_one(self):
        h=ItemHistory();h.record(1,{'name':'Fish','quantity':1});h.set_icon(1,icon())
        h.record(2,quantity=1);h.set_icon(2,icon((100,50,70)))
        h.identify(2,{'name':'Fish','quantity':1})
        self.assertEqual(len(h.icons),1)
        h.record_outcome(3,'Sem recompensa')
        self.assertFalse(h.set_icon(3,icon()));self.assertNotIn('icon',h.by_cycle[3])
        h.record(4,quantity=1);self.assertFalse(h.set_icon(4,None))

    def test_icon_cache_has_limit_without_losing_history(self):
        h=ItemHistory();h.icons={str(i):'unused' for i in range(MAX_ICONS)}
        h.record(1,quantity=1);self.assertFalse(h.set_icon(1,icon()))
        self.assertEqual(h.total,1);self.assertEqual(len(h.icons),MAX_ICONS)

    def test_gui_shows_icon_and_late_frame_stays_with_original_cycle(self):
        import macro
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'FISHING_MACRO_DATA_DIR':tmp}):
            app=macro.App();app.root.withdraw()
            for timer in app.root.tk.call('after','info'):app.root.after_cancel(timer)
            try:
                app.cycle_id=2;app.history.record(1,{'name':'Fish','quantity':1})
                future=Future();future.set_result({'fishing':False,'loot':None,'reward':True,'reward_icon':icon()})
                app.scene_job=(future,app.scene_epoch,100,1);app.poll_scene(100.5)
                self.assertIn('icon',app.history.by_cycle[1]);self.assertNotIn(2,app.pending_icons)
                app.history.record_outcome(2,'Sem recompensa');app.open_history();app.root.update_idletasks()
                summary,rows=app.history_tables
                self.assertTrue(summary.item(summary.get_children()[0],'image'))
                self.assertEqual(rows.item(rows.get_children()[0],'text'),'—')
                self.assertTrue(rows.item(rows.get_children()[1],'image'))
                old=app.history.by_cycle[1]['icon']
                future=Future();future.set_result({'fishing':False,'loot':None,'reward':True,'reward_icon':icon((100,50,70))})
                app.scene_job=(future,app.scene_epoch-1,101,1);app.poll_scene(101.5)
                self.assertEqual(app.history.by_cycle[1]['icon'],old)
            finally:app.close()

if __name__=='__main__':unittest.main()

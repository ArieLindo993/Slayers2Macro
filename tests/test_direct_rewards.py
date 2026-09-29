import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from engine import Engine
from item_icons import IconSampler
from item_history import ItemHistory
from test_item_icons import icon

CONFIG={'cast':[.5,.5],'cast_hold':.25,'wait_seconds':20,'result_wait':2,'recast_seconds':1.5,
        'max_cast':3,'max_collect':5,'collect_timeout':35,'t_hold':3,'anticipation':.1,'auto_calibrate':True}

class DirectRewards(unittest.TestCase):
    def test_inventory_reward_ends_fishing_without_prompt_or_t(self):
        engine=Engine(dict(CONFIG));engine.track(0)
        actions=engine.step(1,None,False,None,True)
        self.assertEqual(engine.collected,1);self.assertEqual(engine.state,'REINICIANDO')
        self.assertNotIn(('t',True),actions)
        engine.step(1.5,None,False,None,True)
        engine.step(3,None,False,None,True)
        engine.step(3.3,None,False,None,True)
        engine.step(3.7,None,False,None,True)
        self.assertEqual(engine.collected,1)

    def test_reward_event_survives_last_minigame_frame(self):
        engine=Engine(dict(CONFIG));engine.track(0)
        engine.step(1,None,True,None,True)
        self.assertTrue(engine.reward_pending);self.assertEqual(engine.collected,0)
        engine.step(1.5,None,False,None,False)
        self.assertEqual(engine.collected,1)

    def test_preexisting_notification_and_stale_gap_do_not_duplicate(self):
        engine=Engine(dict(CONFIG))
        engine.step(.1,None,False,None,True)
        engine.step(1.2,None,False,None,True)
        engine.step(1.5,None,False,None,True)
        engine.step(2,None,False,None,False,scene_stamp=0,scene_valid=False)
        engine.step(2.2,None,False,None,True)
        self.assertEqual(engine.collected,0)

    def test_samples_require_distinct_frames_and_reject_fades(self):
        sampler=IconSampler()
        self.assertIsNone(sampler.observe(0,1,'fade',.3))
        self.assertIsNone(sampler.observe(0,1,'replay',1.))
        self.assertEqual(sampler.observe(0,1.4,'clear',.95),('clear',.95))
        self.assertEqual(sampler.observe(0,1.8,'fade-out',.2),('clear',.95))
        self.assertIsNone(sampler.observe(1,2,'other',.95))
        sampler.prune(2);self.assertNotIn(0,sampler.samples)

    def test_clearer_icon_replaces_shared_thumbnail_without_duplication(self):
        h=ItemHistory();h.record(0,{'name':'Fish','quantity':1})
        h.set_icon(0,icon(),quality=.71)
        h.record(1,{'name':'Fish','quantity':1});old=h.by_cycle[0]['icon']
        self.assertTrue(h.set_icon(1,icon((200,30,80)),quality=.98))
        self.assertNotEqual(h.by_cycle[0]['icon'],old)
        self.assertEqual(h.by_cycle[0]['icon'],h.by_cycle[1]['icon']);self.assertEqual(len(h.icons),1)
        self.assertFalse(h.set_icon(0,icon(),quality=.5));self.assertEqual(h.total,2)

    def test_late_name_keeps_better_icon_instead_of_cached_fade(self):
        h=ItemHistory();h.record(0,{'name':'Fish','quantity':1});h.set_icon(0,icon(),.71)
        h.record(1,quantity=1);h.set_icon(1,icon((200,30,80)),.98);best=h.by_cycle[1]['icon']
        h.identify(1,{'name':'Fish','quantity':1})
        self.assertEqual(h.by_cycle[0]['icon'],best);self.assertEqual(len(h.icons),1)

    def test_quick_scan_checks_reward_and_returns_its_own_crop(self):
        import numpy as np
        from signals import Signals
        from unittest.mock import patch
        s=Signals(Path(__file__).resolve().parents[1]/'src/assets')
        frame=np.zeros((1080,1920,3),dtype=np.uint8)
        with patch.object(s,'match',side_effect=[(True,(0,0),1.),(True,(1075.5,596.5),.99)]):
            result=s.scan(frame,fishing_only=True)
        self.assertTrue(result['reward']);self.assertTrue(result['fishing'])
        self.assertEqual(result['reward_crop'].shape,(100,440,3))

if __name__=='__main__':unittest.main()

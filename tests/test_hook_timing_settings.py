"""Upgrade timing defaults once, preserving deliberate user adjustments."""
import json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import macro


class HookTimingSettings(unittest.TestCase):
    def load_case(self,saved):
        with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'FISHING_MACRO_DATA_DIR':directory}),\
             patch.object(macro,'send_mouse'),patch.object(macro,'send_t'),patch.object(macro,'send_fishing_key'):
            (Path(directory)/'config.json').write_text(json.dumps(saved),encoding='utf-8')
            app=macro.App();app.root.withdraw()
            try:return dict(app.config)
            finally:app.close()

    def test_old_default_is_upgraded_and_hook_delay_is_added(self):
        config=self.load_case({'cast_settle_seconds':1.8,'t_hold':3.})
        self.assertEqual(config['cast_settle_seconds'],3.)
        self.assertEqual(config['splash_click_delay'],.18)
        self.assertEqual(config['hook_timing_revision'],1)
        self.assertEqual(config['t_hold'],3.)

    def test_custom_guard_and_valid_delay_survive_upgrade(self):
        config=self.load_case({'cast_settle_seconds':4.,'splash_click_delay':.25})
        self.assertEqual(config['cast_settle_seconds'],4.)
        self.assertEqual(config['splash_click_delay'],.25)

    def test_shorter_guard_deliberately_saved_after_upgrade_is_preserved(self):
        config=self.load_case({'cast_settle_seconds':1.8,'hook_timing_revision':1,'splash_click_delay':.12})
        self.assertEqual(config['cast_settle_seconds'],1.8)
        self.assertEqual(config['splash_click_delay'],.12)


if __name__=='__main__':unittest.main()

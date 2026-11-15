"""Both Windows buttons, exclusive switching and complete release; no real input."""
import sys,unittest
from pathlib import Path
from unittest.mock import patch,call
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import macro
from circular import CircularReading
from circular_engine import CircularEngine
import test_circular_flow as flow_tests


class MouseFlags(unittest.TestCase):
    def test_left_and_right_have_distinct_windows_down_and_up_flags(self):
        flags=[]
        def accept(count,pointer,size):
            event=macro.C.cast(pointer,macro.C.POINTER(macro.Input)).contents
            self.assertEqual((count,size,event.type),(1,40,0))
            flags.append(event.mi.dwFlags)
            return 1
        with patch.object(macro.U,'SendInput',side_effect=accept):
            for button in ('left','right'):
                macro.send_mouse(True,button);macro.send_mouse(False,button)
        self.assertEqual(flags,[0x0002,0x0004,0x0008,0x0010])

    def test_engine_releases_opposite_before_press_and_both_at_end(self):
        engine=CircularEngine(flow_tests.cfg());held={'mouse':False,'right_mouse':False}
        for index,button in enumerate(('right','right','left','left','right')):
            actions=engine.step(index*.1,CircularReading((1,1),1,1,mouse_button=button))
            for kind,value in actions:
                if kind in held:
                    held[kind]=value
                    self.assertFalse(all(held.values()),actions)
            self.assertEqual(held,{'mouse':button=='left','right_mouse':button=='right'})
        actions=engine.step(.6,CircularReading((1,1),1,1,complete=True))
        self.assertIn(('mouse',False),actions);self.assertIn(('right_mouse',False),actions)


class MouseOwnership(unittest.TestCase):
    setUp=flow_tests.CircularApp.setUp

    def test_switching_releases_previous_button_and_does_not_repeat_down(self):
        app=self.app;app.active=True
        with patch.object(macro,'game_window',return_value=app.window):
            app.mouse(True,'right');self.assertTrue(app.right_held);self.assertFalse(app.held)
            macro.send_mouse.reset_mock()
            app.mouse(True)
            self.assertEqual(macro.send_mouse.call_args_list,[call(False,'right'),call(True)])
            self.assertFalse(app.right_held);self.assertTrue(app.held)
            macro.send_mouse.reset_mock()
            app.mouse(True,'right');app.mouse(True,'right')
            self.assertEqual(macro.send_mouse.call_args_list,[call(False),call(True,'right')])
            app.tap_fishing_key('A')
            self.assertTrue(app.right_held)

    def test_pause_and_focus_loss_release_right_and_pending_keys(self):
        app=self.app;app.active=True
        with patch.object(macro,'game_window',return_value=app.window):
            app.mouse(True,'right');app.tap_fishing_key('D');app.key_t(True)
            app.stop('Pausado.')
            self.assertFalse(app.right_held);self.assertFalse(app.held)
            self.assertFalse(app.t_down);self.assertFalse(app.fishing_keys)
            app.active=True;app.mouse(True,'right')
        with patch.object(macro,'game_window',return_value=None):
            self.assertFalse(app.sync_window())
        self.assertFalse(app.right_held);self.assertFalse(app.active)

    def test_resize_releases_right_before_recovery(self):
        app=self.app;app.active=True
        with patch.object(macro,'game_window',return_value=app.window):app.mouse(True,'right')
        with patch.object(macro,'game_window',return_value=(1,0,0,800,599)):
            self.assertFalse(app.sync_window())
        self.assertFalse(app.right_held)

    def test_release_failure_does_not_skip_other_button_or_keyboard(self):
        app=self.app;app.held=True;app.right_held=True;app.t_down=True;app.fishing_keys={'A':0.}
        def send(down,button='left'):
            if button=='left':raise RuntimeError('input unavailable')
        with patch.object(macro,'send_mouse',side_effect=send) as mouse:
            with self.assertRaises(RuntimeError):app.release_inputs()
            mouse.assert_any_call(False,'right')
        self.assertFalse(app.right_held);self.assertFalse(app.t_down);self.assertFalse(app.fishing_keys)

    def test_failed_release_never_presses_opposite_button(self):
        app=self.app;app.active=True;app.held=True
        with patch.object(macro,'game_window',return_value=app.window),\
             patch.object(macro,'send_mouse',side_effect=RuntimeError('release failed')) as send:
            with self.assertRaises(RuntimeError):app.mouse(True,'right')
            self.assertEqual(send.call_args_list,[call(False)])
        self.assertFalse(app.right_held)

    def test_observation_mode_does_not_press_either_button(self):
        app=self.app;app.active=True;app.dry.set(True)
        with patch.object(macro,'game_window',return_value=app.window):
            app.mouse(True);app.mouse(True,'right')
        macro.send_mouse.assert_not_called()


if __name__=='__main__':unittest.main()

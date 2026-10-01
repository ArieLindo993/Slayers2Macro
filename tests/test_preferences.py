import csv,os,re,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from preferences import DEFAULT_HOTKEYS,KEY_CODES,load_preferences,validate_hotkeys
from i18n import CATALOG,Translator
from item_history import ItemHistory

class Preferences(unittest.TestCase):
    def test_defaults_migration_and_invalid_config(self):
        self.assertEqual(load_preferences({}),{'language':'pt','hotkeys':DEFAULT_HOTKEYS})
        for keys in (None,[],{'stop':'F4'},{'toggle':'T'},{'water':'invalid'}):
            self.assertEqual(load_preferences({'hotkeys':keys})['hotkeys'],DEFAULT_HOTKEYS)
        self.assertEqual(load_preferences({'language':[]})['language'],'pt')
        self.assertEqual(validate_hotkeys({'toggle':'f9'})['toggle'],'F9')

    def test_catalog_placeholders_match_and_runtime_messages_translate(self):
        for source,translations in CATALOG.items():
            expected=set(re.findall(r'\{\w+\}',source))
            for text in translations.values():self.assertEqual(set(re.findall(r'\{\w+\}',text)),expected,source)
        for language in ('en','es'):
            tr=Translator({'language':language,'hotkeys':dict(DEFAULT_HOTKEYS,toggle='F9',water='F4')})
            for source in ('Conferindo a tela…','Tentativa de coleta 2/5','Coleta confirmada. Próxima pesca…',
                'Lançamento não confirmado. Conferindo a tela; nova tentativa em 15s.',
                'Desde 12:00:00 · 2 itens · 3 ciclos registrados · 1 nome(s) não identificado(s)',
                'Dentro da faixa: 72.5%\nLeituras válidas: 90.0%\nTempo medido: 42.0s'):
                self.assertNotEqual(tr(source),source)
            self.assertIn('F9',tr('Volte ao Roblox e pressione F4.'))
            self.assertIn('F4',tr('Aponte para a água e pressione F8'))
            self.assertEqual(tr('Resolução Roblox: 800 × 599'),
                'Roblox resolution: 800 × 599' if language=='en' else 'Resolución de Roblox: 800 × 599')
            self.assertEqual(tr('Perfil: Janela · escala 100%'),
                'Profile: Window · scale 100%' if language=='en' else 'Perfil: Ventana · escala 100%')
            self.assertEqual(tr('Clown Fish'),'Clown Fish')
        self.assertEqual(Translator({'language':'pt'})('Iniciar'),'Iniciar')

    def test_export_headers_translate_but_game_names_do_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            h=ItemHistory();h.record(0,{'name':'Clown Fish','quantity':1})
            path=Path(tmp)/'items.csv';h.export(path,translate=Translator({'language':'en'}))
            with path.open(encoding='utf-8-sig') as stream:rows=list(csv.reader(stream,delimiter=';'))
            self.assertEqual(rows[0],['Time','Item','Quantity','Name recognized'])
            self.assertEqual(rows[1][1],'Clown Fish')

class PreferenceUI(unittest.TestCase):
    def setUp(self):
        import macro
        self.macro=macro;self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        env=patch.dict(os.environ,{'FISHING_MACRO_DATA_DIR':self.tmp.name});env.start();self.addCleanup(env.stop)
        for name in ('send_t','send_mouse'):
            mock=patch.object(macro,name);mock.start();self.addCleanup(mock.stop)
        self.app=macro.App();self.app.root.withdraw();self.addCleanup(self.app.close)
        for timer in self.app.root.tk.call('after','info'):self.app.root.after_cancel(timer)

    def test_save_language_keys_preserves_history_and_persists(self):
        import json
        app=self.app;app.history.record(0,{'name':'Clown Fish','quantity':1})
        app.engine.cycles=1;app.engine.collected=1;app.open_history();app.open_settings()
        app.language_var.set('English');app.hotkey_vars['toggle'].set('F9')
        with patch.object(self.macro.U,'GetAsyncKeyState',return_value=0):app.apply_settings()
        self.assertEqual(app.start_button.cget('text'),'Start')
        self.assertEqual(app.history.total,1);self.assertEqual(app.engine.collected,1)
        self.assertIn('1 confirmed collections',app.counter.get());self.assertIn('F9',app.status.get())
        self.assertEqual(app.history_window.title(),'Items obtained this session')
        saved=json.loads(app.config_path.read_text('utf-8'))
        self.assertEqual(load_preferences(saved)['hotkeys']['toggle'],'F9')
        self.assertEqual(load_preferences(saved)['language'],'en')

    def test_duplicate_validation_does_not_apply_partial_settings(self):
        app=self.app;app.open_settings();app.hotkey_vars['water'].set('F4');app.language_var.set('Español')
        with patch.object(self.macro.messagebox,'showerror') as error:app.apply_settings();error.assert_called_once()
        self.assertEqual(app.config['language'],'pt');self.assertTrue(app.settings.winfo_exists())
        app.reset_hotkey_fields();self.assertEqual({k:v.get() for k,v in app.hotkey_vars.items()},DEFAULT_HOTKEYS)

    def test_only_selected_shortcuts_fire_and_settings_suppress_keys(self):
        app=self.app;app.config['hotkeys']=dict(DEFAULT_HOTKEYS,toggle='F9',water='K',calibrate='F2',stop='F12')
        window=(1,0,0,1920,1080)
        def press(key):
            app.previous_keys={}
            with patch.object(self.macro.U,'GetAsyncKeyState',side_effect=lambda k:0x8000 if k==KEY_CODES[key] else 0):app.keys()
        with patch.object(self.macro,'game_window',return_value=window),patch.object(app,'start') as start,patch.object(app,'open_selection') as select:
            press('F4');start.assert_not_called()
            press('F9');start.assert_called_once_with(window)
            press('F6');select.assert_not_called()
            press('F2');select.assert_called_once_with(window)
            with patch.object(self.macro,'cursor_relative',return_value=(.4,.6)):
                press('K');self.assertEqual(app.config['cast'],[.4,.6])
            with patch.object(app,'stop') as stop:press('F12');stop.assert_called_once()
            app.open_settings();start.reset_mock();press('F9');start.assert_not_called()

    def test_manual_selection_uses_language_and_custom_stop_key(self):
        import numpy as np
        app=self.app;app.config['language']='en';app.config['hotkeys']['stop']='F12'
        with patch.object(app,'sample',return_value=np.zeros((360,640,3),dtype=np.uint8)),patch.object(app,'choose_profile'):
            app.open_selection((1,0,0,640,360))
        selection=app.selection
        self.assertEqual(selection.button.cget('text'),'Save selection (Enter)')
        self.assertTrue(selection.win.bind('<F12>'));self.assertFalse(selection.win.bind('<F10>'))
        self.assertTrue(selection.win.bind('<Escape>'));self.assertTrue(selection.win.bind('<Return>'))
        selection.cancel();self.assertIsNone(app.selection)

if __name__=='__main__':unittest.main()

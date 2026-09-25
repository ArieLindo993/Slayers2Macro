import sys,tempfile,unittest,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from session_log import SessionLog
from item_history import ItemHistory

class TextLog(unittest.TestCase):
    def test_timestamps_append_without_truncating_and_session_files_unique(self):
        with tempfile.TemporaryDirectory() as tmp:
            log=SessionLog(tmp)
            for i in range(250):self.assertTrue(log.event('EVENTO',ciclo=i))
            lines=log.path.read_text('utf-8').splitlines()
            self.assertEqual(len(lines),250)
            self.assertRegex(lines[0],r'^\[\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}[+-]\d\d:\d\d\]')
            other=SessionLog(tmp);other.event('NOVA_EXECUCAO')
            self.assertNotEqual(other.path,log.path)
            self.assertEqual(len(log.path.read_text('utf-8').splitlines()),250)

    def test_confirmed_unconfirmed_and_late_identification_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            log=SessionLog(tmp);history=ItemHistory(log=log)
            history.record(1,quantity=1)
            result={'name':'Metal Scraps','quantity':1,'confidence':.99}
            history.identify(1,result);history.identify(1,result)
            history.record_outcome(2,'Item desapareceu; recompensa não confirmada')
            text=log.path.read_text('utf-8')
            self.assertEqual(text.count('COLETA_CONFIRMADA'),1)
            self.assertEqual(text.count('ITEM_IDENTIFICADO'),1)
            self.assertIn('COLETA_NAO_CONFIRMADA',text)
            self.assertIn('Metal Scraps',text)

    def test_log_injection_and_disk_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            log=SessionLog(tmp);log.event('ITEM',nome='Fish\nFAKE EVENT\x00')
            self.assertEqual(len(log.path.read_text().splitlines()),1)
            blocked=Path(tmp)/'file';blocked.write_text('existing')
            bad=SessionLog(blocked)
            self.assertFalse(bad.event('EVENTO'));self.assertTrue(bad.error)

    def test_app_start_stop_written(self):
        if sys.platform!='win32':self.skipTest('Windows app')
        import os,macro
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'FISHING_MACRO_DATA_DIR':tmp}):
            app=macro.App();app.root.withdraw();app.config['cast']=[.5,.5]
            try:
                with patch.object(macro,'game_window',return_value=(1,0,0,800,500)):
                    app.start((1,0,0,800,500));app.stop('Pausado com F4.')
                path=app.session_log.path
            finally:app.close()
            text=path.read_text('utf-8')
            for event in ('APLICATIVO_ABERTO','MACRO_INICIADO','MACRO_PAUSADO','ENCERRAMENTO_CONCLUIDO'):
                self.assertIn(event,text)

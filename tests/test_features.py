import json,os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from detector import Reading
from diagnostics import Diagnostics,TrackingMetrics,annotated_preview
from local_data import ProfileStore,data_directory,migrate_legacy
from calibration import AutoCalibration,search_bar

def frame(x=580,y=100):
    import cv2
    rgb=np.zeros((500,800,3),np.uint8)
    cv2.rectangle(rgb,(x,y),(x+46,y+300),(170,170,170),2)
    cv2.rectangle(rgb,(x-2,y+100),(x+48,y+129),(80,150,40),-1)
    cv2.rectangle(rgb,(x+12,y+150),(x+34,y+164),(235,235,235),-1)
    return rgb

class Features(unittest.TestCase):
    def test_metrics_are_time_weighted(self):
        m=TrackingMetrics();inside=Reading(.5,.5,.1);outside=Reading(.5,.8,.1)
        m.observe(inside,0);m.observe(outside,.05);m.observe(None,.10);m.observe(inside,.15)
        s=m.summary();self.assertAlmostEqual(s['inside_percent'],50);self.assertAlmostEqual(s['valid_percent'],66.7)
        m.pause();m.observe(inside,99);self.assertAlmostEqual(m.total,.15)

    def test_private_bounded_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Diagnostics(tmp,limit=2);m=TrackingMetrics().summary()
            for t in (0,11,22):self.assertTrue(d.save(frame()[100:400,580:627],'C:'+chr(47)+'Users'+chr(47)+'PRIVATE','secret',m,t))
            self.assertFalse(d.save(frame(),'PESCANDO','screen',m,23))
            self.assertEqual(len(list(Path(tmp).glob('*.json'))),2)
            for p in Path(tmp).glob('*.json'):
                text=p.read_text();self.assertNotIn('PRIVATE',text);self.assertNotIn('secret',text)
            from PIL import Image
            for p in Path(tmp).glob('*.png'):
                with Image.open(p) as im:self.assertEqual(im.width,47)

    def test_profiles_isolated_and_persistent(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=ProfileStore(Path(tmp)/'profiles.json');roi=[.7,.2,.05,.5];other=[.3,.2,.05,.5]
            k=p.key(1920,1080,'window',96);k2=p.key(1920,1080,'borderless',96)
            p.save(k,roi,{});p.save(k2,other,{})
            restored=ProfileStore(p.path)
            self.assertEqual(restored.load(k,other)[0],roi)
            self.assertEqual(restored.load(k2,roi)[0],other)
            self.assertEqual(restored.load(p.key(1280,720,'window',144),roi)[0],roi)

    def test_local_migration_does_not_publish_or_delete(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'install';src.mkdir();dst=Path(tmp)/'data';dst.mkdir()
            (src/'config.json').write_text('{"cast":[0.5,0.5]}')
            (src/'unrelated.txt').write_text('private')
            migrate_legacy(src,dst)
            self.assertTrue((src/'config.json').exists());self.assertFalse((dst/'unrelated.txt').exists())
            (dst/'config.json').write_text('{}');migrate_legacy(src,dst)
            self.assertEqual((dst/'config.json').read_text(),'{}')

    def test_staged_search_and_recovery(self):
        a=AutoCalibration();self.assertEqual(a.search_stage,'current')
        for _ in range(2):a.observe(None)
        self.assertEqual(a.search_stage,'nearby')
        for _ in range(2):a.observe(None)
        self.assertEqual(a.search_stage,'screen')
        roi=[.72,.19,.065,.62];im=frame()
        for stage in ('current','nearby','screen'):
            result=search_bar(im,roi,stage);self.assertIsNotNone(result,stage)
        far=frame(200,100)
        self.assertIsNone(search_bar(far,roi,'current'))
        self.assertIsNotNone(search_bar(far,roi,'screen'))
        for _ in range(3):a.observe(result)
        self.assertTrue(a.locked);a.check_tracking(None,0);self.assertTrue(a.check_tracking(None,.6))
        self.assertEqual(a.search_stage,'current')

    def test_preview_contains_annotations(self):
        im=annotated_preview(np.zeros((300,60,3),np.uint8),Reading(.5,.7,.1))
        colors=set(map(tuple,np.array(im).reshape(-1,3)));self.assertIn((18,237,140),colors);self.assertIn((255,102,210),colors)

    def test_offline_rollback_preserves_data(self):
        if sys.platform!='win32':self.skipTest('Windows updater')
        import subprocess,shutil
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);script=base/'Atualizar.ps1'
            shutil.copy2(Path(__file__).resolve().parents[1]/'Atualizar.ps1',script)
            for release in ('1','2'):
                folder=base/'.install'/release;folder.mkdir(parents=True)
                (folder/'Slayers2Macro.exe').write_bytes(b'test placeholder; never executed')
            (base/'.install/current.txt').write_text('2');(base/'.install/previous.txt').write_text('1')
            local=base/'appdata';data=local/'FishingMacro';(data/'historico').mkdir(parents=True)
            (data/'config.json').write_text('{"cast":[0.4,0.5]}');(data/'historico/session.json').write_text('{"items":7}')
            env=dict(os.environ,LOCALAPPDATA=str(local))
            r=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(script),'-Voltar','-NaoAbrir'],env=env,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            self.assertEqual((base/'.install/current.txt').read_text().strip(),'1')
            self.assertEqual((base/'.install/1/historico/session.json').read_text(),'{"items":7}')
            self.assertEqual((data/'historico/session.json').read_text(),'{"items":7}')
            (base/'.install/previous.txt').write_text('../outside')
            r=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(script),'-Voltar','-NaoAbrir'],env=env,capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)

    def test_gui_profiles_and_preview(self):
        if sys.platform!='win32':self.skipTest('Windows application')
        from unittest.mock import patch
        import macro
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'FISHING_MACRO_DATA_DIR':tmp}):
            app=macro.App();app.root.withdraw()
            try:
                w=(1,0,0,800,500)
                with patch.object(macro,'game_window',return_value=w):
                    app.config['cast']=[.5,.5];app.start(w)
                    first=app.profile_key
                    app.save_selection([.72,.19,.065,.62]);app.choose_profile((1,0,0,1280,720))
                    self.assertNotEqual(first,app.profile_key)
                    self.assertTrue(app.config['auto_calibrate'])
                    self.assertNotEqual(app.config['roi'],[.72,.19,.065,.62])
                    app.choose_profile(w);self.assertEqual(app.config['roi'],[.72,.19,.065,.62])
                    self.assertFalse(app.config['auto_calibrate'])
                    app.dry.set(True);app.window=w
                    with patch.object(app,'sample',side_effect=lambda full=False:frame() if full else frame()[100:400,580:627]):
                        app.update(__import__('time').monotonic());app.root.update_idletasks()
                        self.assertIsNotNone(app.live_photo)
                self.assertTrue((Path(tmp)/'profiles.json').exists())
            finally:app.close()

if __name__=='__main__':unittest.main()

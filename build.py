from pathlib import Path
import subprocess,sys,shutil,hashlib,json,zipfile
from importlib import metadata
root=Path(__file__).resolve().parent
subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--clean','--windowed',
 '--name','Slayers2Macro','--distpath',str(root/'dist'),'--workpath',str(root/'build'),
 '--specpath',str(root/'build'),'--collect-data','rapidocr_onnxruntime',
 '--collect-binaries','onnxruntime','--add-data',str(root/'src/assets')+';assets',
 str(root/'src/macro.py')],check=True,cwd=root)
exe=root/'dist/Slayers2Macro/Slayers2Macro.exe'
result=root/'build/self-test.json'
subprocess.run([str(exe),'--self-test',str(result)],check=True,timeout=45)
data=json.loads(result.read_text())
assert data['startup'] and data['collect_without_prompt'] and data['auto_calibration']
notices=root/'dist/Slayers2Macro/THIRD_PARTY';notices.mkdir(exist_ok=True)
dependencies=[]
for name in ('mss','numpy','opencv-python','Pillow','rapidocr-onnxruntime','onnxruntime','pyinstaller'):
    dist=metadata.distribution(name);dependencies.append({'name':name,'version':dist.version})
    for f in dist.files or []:
        if '..' not in f.parts and not Path(f).is_absolute() and any(part.lower().startswith(('license','copying','notice')) for part in f.parts) and dist.locate_file(f).is_file():
            target=notices/name/Path(*f.parts);target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(dist.locate_file(f),target)
(notices/'dependencies.json').write_text(json.dumps(dependencies,indent=2),encoding='utf-8')
shutil.copy2(root/'README.md',root/'dist/Slayers2Macro/README.md')
archive=Path(shutil.make_archive(str(root/'dist/Slayers2Macro'),'zip',root/'dist/Slayers2Macro'))
archive.with_suffix('.zip.sha256').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'\n',encoding='ascii')
with zipfile.ZipFile(root/'dist/Atualizador.zip','w',zipfile.ZIP_DEFLATED) as bundle:
    for name in ('Atualizar.cmd','Atualizar.ps1','Iniciar.cmd','Voltar-versao.cmd','README.md'):
        bundle.write(root/name,name)
print('Build e teste de inicialização concluídos:',archive)

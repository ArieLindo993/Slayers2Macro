"""Dados por usuário, fora da instalação e sem envio pela rede."""
import json,os,re,shutil
from pathlib import Path
from product import APP_ID

def data_directory():
    override=os.environ.get('FISHING_MACRO_DATA_DIR')
    path=Path(override) if override else Path(os.environ.get('LOCALAPPDATA',Path.home()/'.local/share'))/APP_ID
    path.mkdir(parents=True,exist_ok=True)
    return path

def migrate_legacy(source,destination):
    """Migração aditiva: não altera nem apaga dados da versão anterior."""
    marker=destination/'migration-v1.json'
    if marker.exists():return
    for name in ('config.json','historico'):
        original=source/name;target=destination/name
        if original.is_file() and not target.exists():shutil.copy2(original,target)
        elif original.is_dir():
            target.mkdir(parents=True,exist_ok=True)
            for item in original.iterdir():
                if item.is_file() and item.suffix in ('.json','.csv') and not (target/item.name).exists():
                    shutil.copy2(item,target/item.name)
    marker.write_text('{"schema":1}',encoding='utf-8')

def valid_roi(roi):
    return (isinstance(roi,list) and len(roi)==4 and
            all(type(x) in (int,float) for x in roi) and
            0<=roi[0]<1 and 0<=roi[1]<1 and .005<roi[2]<.3 and .05<roi[3]<.9 and
            roi[0]+roi[2]<=1 and roi[1]+roi[3]<=1)

class ProfileStore:
    def __init__(self,path):
        self.path=Path(path);self.profiles={}
        try:
            data=json.loads(self.path.read_text('utf-8'))
            for key,item in data.items():
                if re.fullmatch(r'\d+x\d+-(window|borderless)-\d+',key) and isinstance(item,dict) and valid_roi(item.get('roi')):
                    self.profiles[key]=item
        except (OSError,ValueError,AttributeError):pass

    @staticmethod
    def key(width,height,mode,dpi):return f'{int(width)}x{int(height)}-{mode}-{int(dpi)}'

    def load(self,key,default):
        item=self.profiles.get(key,{})
        learned=item.get('learned',{})
        if not isinstance(learned,dict) or not valid_roi(learned.get('roi')):learned={}
        return list(item.get('roi',default)),learned

    def save(self,key,roi,learned):
        if not key or not valid_roi(roi):return
        self.profiles[key]={'roi':list(roi),'learned':learned if isinstance(learned,dict) else {}}
        temp=self.path.with_suffix('.tmp')
        temp.write_text(json.dumps(self.profiles,indent=2),encoding='utf-8');temp.replace(self.path)

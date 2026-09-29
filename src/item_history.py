"""Histórico local por execução, com uma entrada por coleta confirmada."""
from datetime import datetime
from pathlib import Path
import csv
import json
import re
import hashlib
from item_icons import decode_icon,MAX_ICONS


def canonical_name(name):
    name=' '.join(str(name).split())
    key=re.sub(r'[^a-z0-9]', '',name.casefold())
    # Apenas aliases conhecidos: prefixos arbitrários podem ser espécies distintas.
    if key in ('clown','clownf','clownfi','clownfis','clownfish'):return 'Clown Fish'
    if key=='metalscraps':return 'Metal Scraps'
    return name


def parse_reward(lines):
    if not lines:return None
    names=[];quantities=[]
    for box,text,score in lines:
        text=' '.join(str(text).split())
        y=sum(p[1] for p in box)/len(box)
        match=re.fullmatch(r'[xX×]\s*(\d{1,4})',text)
        if match and score>=.65:
            qty=int(match[1])
            if 1<=qty<=9999:quantities.append((y,qty,score))
        elif score>=.85 and 2<=len(text)<=90 and re.search(r'[A-Za-zÀ-ÿ]',text):
            names.append((y,text,score,min(p[0] for p in box),max(p[1] for p in box)-min(p[1] for p in box)))
    if not quantities or not names:return None
    qty_y,qty,qty_score=max(quantities,key=lambda v:v[2])
    above=[n for n in names if n[0]<qty_y]
    if not above:return None
    closest=max(above,key=lambda v:v[0])
    row=sorted((n for n in above if abs(n[0]-closest[0])<=max(3,min(n[4],closest[4])*.4)),key=lambda n:n[3])
    name=canonical_name(' '.join(n[1] for n in row));confidence=min(n[2] for n in row)
    return {'name':name,'quantity':qty,'confidence':min(confidence,qty_score)}


class ItemHistory:
    def __init__(self,directory=None,log=None):
        self.log=log
        self.started=datetime.now().astimezone()
        self.entries=[];self.by_cycle={};self.error=None
        self.icons={};self.icons_by_name={};self.icon_quality={}
        self.path=Path(directory)/('sessao-'+self.started.strftime('%Y%m%d-%H%M%S-%f')+'.json') if directory else None

    def record(self,cycle,result=None,quantity=None):
        if cycle in self.by_cycle:return self.by_cycle[cycle]
        entry={'cycle':cycle,'time':datetime.now().astimezone().isoformat(timespec='seconds'),
               'name':'Nome não identificado','quantity':quantity,'identified':False}
        self.entries.append(entry);self.by_cycle[cycle]=entry
        if self.log and quantity!=0:self.log.event('COLETA_CONFIRMADA',ciclo=cycle,item=result['name'] if result else 'Nome ainda não identificado',quantidade=result['quantity'] if result else quantity)
        if result:self.identify(cycle,result)
        else:self.save()
        return entry

    def identify(self,cycle,result,*,confirm=False):
        if not result or cycle not in self.by_cycle:return False
        entry=self.by_cycle[cycle]
        if entry.get('status')=='unconfirmed':
            if not confirm:return False
            entry.pop('status',None)
            if self.log:self.log.event('COLETA_CONFIRMADA_TARDIA',ciclo=cycle,item=result['name'],quantidade=result['quantity'])
        result=dict(result,name=canonical_name(result['name']))
        # Reutiliza grafia da sessão, sem fundir espécies por semelhança.
        result['name']=next((e['name'] for e in self.entries if e.get('identified') and e.get('status')!='unconfirmed'
            and e['name'].casefold()==result['name'].casefold()),result['name'])
        changed=not entry['identified'] or entry['name']!=result['name'] or entry['quantity']!=result['quantity']
        entry.update(name=result['name'],quantity=result['quantity'],identified=True)
        self._associate_icon(entry)
        if self.log and changed:self.log.event('ITEM_IDENTIFICADO',ciclo=cycle,item=result['name'],quantidade=result['quantity'],confianca=result.get('confidence'))
        self.save();return True

    def _associate_icon(self,entry):
        if not entry.get('identified') or entry.get('status')=='unconfirmed':return
        name=entry['name'].casefold().strip();previous=entry.get('icon')
        known=self.icons_by_name.get(name)
        if known:
            if previous and self.icon_quality.get(previous,0.)>self.icon_quality.get(known,0.)+.04:
                for other in self.entries:
                    if other.get('icon')==known:other['icon']=previous
                self.icons_by_name[name]=previous
                self.icons.pop(known,None);self.icon_quality.pop(known,None)
                return
            entry['icon']=known
            if previous and previous!=known and not any(e.get('icon')==previous for e in self.entries):
                self.icons.pop(previous,None)
                self.icon_quality.pop(previous,None)
        elif previous:self.icons_by_name[name]=previous

    def set_icon(self,cycle,encoded,quality=0.):
        entry=self.by_cycle.get(cycle)
        if not entry or entry.get('status')=='unconfirmed':return False
        self._associate_icon(entry)
        previous=entry.get('icon')
        if previous and quality<=self.icon_quality.get(previous,0.)+.04:return False
        if (not previous and len(self.icons)>=MAX_ICONS) or decode_icon(encoded) is None:return False
        key=hashlib.sha256(encoded.encode('ascii')).hexdigest()
        if key==previous:
            self.icon_quality[key]=max(quality,self.icon_quality.get(key,0.));return False
        self.icons[key]=encoded;self.icon_quality[key]=quality;entry['icon']=key
        if previous:
            for other in self.entries:
                if other.get('icon')==previous:other['icon']=key
            for name,known in list(self.icons_by_name.items()):
                if known==previous:self.icons_by_name[name]=key
            self.icons.pop(previous,None);self.icon_quality.pop(previous,None)
        self._associate_icon(entry);self.save()
        return True

    def record_outcome(self,cycle,message):
        entry=self.record(cycle,quantity=0)
        entry.update(name=message or 'Sem recompensa detectada',status='unconfirmed',identified=True)
        if self.log:self.log.event('COLETA_NAO_CONFIRMADA',ciclo=cycle,motivo=entry['name'])
        self.save()
        return entry

    @property
    def total(self):return sum(e['quantity'] or 0 for e in self.entries)

    def totals(self):
        result={}
        for entry in self.entries:
            if entry.get('status')=='unconfirmed':continue
            name=entry['name'];result[name]=result.get(name,0)+(entry['quantity'] or 0)
        return result

    def save(self):
        if not self.path:return
        try:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            temporary=self.path.with_suffix('.tmp')
            temporary.write_text(json.dumps({'started':self.started.isoformat(),'entries':self.entries,'icons':self.icons},ensure_ascii=False,indent=2),encoding='utf-8')
            temporary.replace(self.path);self.error=None
            self.export(self.path.with_suffix('.csv'))
        except OSError as exc:self.error=str(exc)

    def export(self,path,translate=str):
        with open(path,'w',encoding='utf-8-sig',newline='') as stream:
            writer=csv.writer(stream,delimiter=';');writer.writerow([translate(s) for s in ('Horário','Item','Quantidade','Nome reconhecido')])
            for e in self.entries:
                name=translate(e['name']) if e.get('status')=='unconfirmed' or not e['identified'] else e['name']
                if name.startswith(('=','+','-','@')):name="'"+name
                writer.writerow([e['time'],name,e['quantity'] if e['quantity'] is not None else '', translate('Sim' if e['identified'] else 'Não')])


class RewardReader:
    """Inicializado e usado apenas na thread de leitura; não bloqueia o mouse."""
    def __init__(self):self.reader=None

    def read(self,rgb):
        import cv2
        if self.reader is None:
            from rapidocr_onnxruntime import RapidOCR
            self.reader=RapidOCR(intra_op_num_threads=1,inter_op_num_threads=1,det_limit_side_len=320)
        enlarged=cv2.resize(rgb[:,:,::-1],None,fx=3,fy=3,interpolation=cv2.INTER_CUBIC)
        result,_=self.reader(enlarged,use_cls=False)
        return parse_reward(result)

    @staticmethod
    def crop(rgb,point=None):
        import cv2
        normalized=cv2.resize(rgb,(1920,1080))
        x,y=point if point else (1075.5,596.5)
        left=max(0,int(x-100));top=max(0,int(y-65))
        return normalized[top:min(1080,top+100),left:min(1920,left+440)].copy()

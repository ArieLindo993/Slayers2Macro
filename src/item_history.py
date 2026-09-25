"""Histórico local por execução, com uma entrada por coleta confirmada."""
from datetime import datetime
from pathlib import Path
import csv
import json
import re


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
            names.append((y,text,score))
    if not quantities or not names:return None
    qty_y,qty,qty_score=max(quantities,key=lambda v:v[2])
    above=[n for n in names if n[0]<qty_y]
    if not above:return None
    _,name,confidence=max(above,key=lambda v:v[0])
    # Nome verificado na própria gravação; o OCR por vezes junta o espaço.
    if name.casefold().replace(' ','')=='metalscraps':name='Metal Scraps'
    return {'name':name,'quantity':qty,'confidence':min(confidence,qty_score)}


class ItemHistory:
    def __init__(self,directory=None,log=None):
        self.log=log
        self.started=datetime.now().astimezone()
        self.entries=[];self.by_cycle={};self.error=None
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

    def identify(self,cycle,result):
        if not result or cycle not in self.by_cycle:return False
        entry=self.by_cycle[cycle]
        if entry.get('status')=='unconfirmed':return False
        changed=not entry['identified'] or entry['name']!=result['name'] or entry['quantity']!=result['quantity']
        entry.update(name=result['name'],quantity=result['quantity'],identified=True)
        if self.log and changed:self.log.event('ITEM_IDENTIFICADO',ciclo=cycle,item=result['name'],quantidade=result['quantity'],confianca=result.get('confidence'))
        self.save();return True

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
            temporary.write_text(json.dumps({'started':self.started.isoformat(),'entries':self.entries},ensure_ascii=False,indent=2),encoding='utf-8')
            temporary.replace(self.path);self.error=None
            self.export(self.path.with_suffix('.csv'))
        except OSError as exc:self.error=str(exc)

    def export(self,path):
        with open(path,'w',encoding='utf-8-sig',newline='') as stream:
            writer=csv.writer(stream,delimiter=';');writer.writerow(['Horário','Item','Quantidade','Nome reconhecido'])
            for e in self.entries:
                name=e['name']
                if name.startswith(('=','+','-','@')):name="'"+name
                writer.writerow([e['time'],name,e['quantity'] if e['quantity'] is not None else '', 'Sim' if e['identified'] else 'Não'])


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
        left=max(0,int(x-67.5));top=max(0,int(y-31.5))
        return normalized[top:min(1080,top+48),left:min(1920,left+352)].copy()

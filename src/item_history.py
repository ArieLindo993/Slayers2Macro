"""Histórico local por execução, com uma entrada por coleta confirmada."""
from datetime import datetime
from pathlib import Path
import csv
import json
import re
import hashlib
import numpy as np
from item_icons import decode_icon,MAX_ICONS
from item_names import canonical_name,name_evidence,key as name_key,resembles_known


def quantity_reading(text):
    """Read an item count, including the compact HUD's OCR form of ``x1``."""
    value=''.join(str(text).split()).casefold().replace('×','x').replace('\uff01','!')
    match=re.fullmatch(r'x\s*(\d{1,4})',value)
    if match:
        quantity=int(match[1])
        return (quantity,False) if 1<=quantity<=9999 else (None,False)
    # At 800x599 the in-world reward tag makes RapidOCR read its tiny ``1``
    # as punctuation or omit it, leaving a lone X. It is accepted only when
    # tightly aligned with a known item name below.
    if value in {'x','x!','x|','xi','xl','xı'}:return 1,True
    return None,False


def parse_reward(lines,width=None):
    if not lines:return None
    names=[];quantities=[];uncertain_quantities=[]
    for box,text,score in lines:
        text=' '.join(str(text).split())
        y=sum(p[1] for p in box)/len(box)
        quantity,uncertain=quantity_reading(text)
        if quantity is not None and score>=(.60 if uncertain else .65):
            xs=[p[0] for p in box];ys=[p[1] for p in box]
            item=(y,quantity,score,min(xs),max(xs),max(ys)-min(ys))
            (uncertain_quantities if uncertain else quantities).append(item)
        elif score>=.85 and 2<=len(text)<=90 and re.search(r'[A-Za-zÀ-ÿ]',text):
            xs=[p[0] for p in box];ys=[p[1] for p in box]
            names.append((y,text,score,min(xs),max(ys)-min(ys),max(xs)))
    if not quantities and uncertain_quantities:
        aligned=[]
        for qty in uncertain_quantities:
            qy,_,qscore,qleft,qright,qheight=qty
            qcenter=(qleft+qright)/2
            for name in names:
                ny,ntext,nscore,nleft,nheight,nright=name
                canonical,known,fragment=name_evidence(ntext)
                if not known or fragment or ny>qy:continue
                if qy-ny>max(qheight,nheight)*1.5:continue
                if not nleft-nheight*.5<=qcenter<=nright+nheight*.5:continue
                aligned.append((qty,name))
        if aligned:
            # Prefer the nearest strong item label, not unrelated HUD text.
            qty,name=min(aligned,key=lambda pair:(pair[0][0]-pair[1][0],-pair[1][2]))
            quantities=[qty]
            names=[name]
    if not quantities or not names:return None
    qty_y,qty,qty_score,_,_,_=max(quantities,key=lambda v:v[2])
    # In the compact client the label and x1 can share a baseline. Keep the
    # quantity-to-name pairing in the same row as well as the older stacked UI.
    above=[n for n in names if n[0]<=qty_y]
    if not above:return None
    closest=max(above,key=lambda v:v[0])
    row=sorted((n for n in above if abs(n[0]-closest[0])<=max(3,min(n[4],closest[4])*.4)),key=lambda n:n[3])
    raw=' '.join(n[1] for n in row);name,known,fragment=name_evidence(raw)
    confidence=min(n[2] for n in row)
    clipped=min(n[3] for n in row)<=2 or (width is not None and max(n[5] for n in row)>=width-2)
    return {'name':name,'quantity':qty,'confidence':min(confidence,qty_score),
            'raw_name':raw,'name_confidence':confidence,'name_known':known,
            'name_ambiguous':fragment or clipped,'name_validated':known and not clipped and confidence>=.90}


class ItemHistory:
    def __init__(self,directory=None,log=None):
        self.log=log
        self.started=datetime.now().astimezone()
        self.entries=[];self.by_cycle={};self.error=None
        self.icons={};self.icons_by_name={};self.icon_quality={}
        self.name_votes={};self.last_name_cycle=-1;self.validated_names={}
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
        self.last_name_cycle=max(self.last_name_cycle,cycle)
        self.name_votes={k:v for k,v in self.name_votes.items() if k>=self.last_name_cycle-1}
        entry=self.by_cycle[cycle]
        if entry.get('status')=='unconfirmed':
            if not confirm:return False
            entry.pop('status',None)
            entry.update(name='Nome não identificado',quantity=result['quantity'],identified=False)
            if self.log:self.log.event('COLETA_CONFIRMADA_TARDIA',ciclo=cycle,item=result['name'],quantidade=result['quantity'])
        result=dict(result,name=canonical_name(result['name']))
        if not result.get('name_validated',True):
            normalized=name_key(result['name']);known=self.validated_names.get(normalized)
            if known and not result.get('name_ambiguous') and result.get('name_confidence',0)>=.9:
                result.update(name=known,name_validated=True)
            elif not result.get('name_known') and any(resembles_known(normalized,k) for k in self.validated_names):
                result['name_ambiguous']=True
        if not result.get('name_validated',True):
            # New names need agreement from two different captured images.
            # Reprocessing the same crop cannot manufacture confirmation.
            accepted=False
            if not result.get('name_ambiguous') and result.get('name_confidence',0)>= (.85 if result.get('name_known') else .92):
                vote=self.name_votes.get(cycle)
                if not vote or vote['name'].casefold()!=result['name'].casefold():
                    vote={'name':result['name'],'samples':set()};self.name_votes[cycle]=vote
                sample=result.get('sample_id')
                if sample:vote['samples'].add(sample)
                accepted=len(vote['samples'])>=2
            if not accepted:
                if not entry['identified']:entry['quantity']=result['quantity']
                if self.log:self.log.event('NOME_AGUARDANDO_CONFIRMACAO',ciclo=cycle,leitura=result.get('raw_name',result['name']),confianca=result.get('name_confidence'))
                self.save();return True
        if entry.get('identified') and entry['name']!='Nome não identificado' and entry['name']!=result['name']:
            # A later OCR error must not rename a validated item.
            if result.get('name_validated') is not None:
                if self.log:self.log.event('NOME_CONFLITANTE_IGNORADO',ciclo=cycle,item=entry['name'],leitura=result['name'])
                self.save();return True
        self.name_votes.pop(cycle,None)
        # Reutiliza grafia da sessão, sem fundir espécies por semelhança.
        result['name']=next((e['name'] for e in self.entries if e.get('identified') and e.get('status')!='unconfirmed'
            and e['name'].casefold()==result['name'].casefold()),result['name'])
        changed=not entry['identified'] or entry['name']!=result['name'] or entry['quantity']!=result['quantity']
        entry.update(name=result['name'],quantity=result['quantity'],identified=True)
        self.validated_names[name_key(entry['name'])]=entry['name']
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
        return self.read_with_diagnostics(rgb)['reading']

    def read_with_diagnostics(self,rgb,*alternate_crops):
        import cv2
        if self.reader is None:
            from rapidocr_onnxruntime import RapidOCR
            self.reader=RapidOCR(intra_op_num_threads=1,inter_op_num_threads=1,det_limit_side_len=320)
        crops=[];seen=set()
        for crop in (rgb,*alternate_crops):
            if crop is None or getattr(crop,'size',0)==0:continue
            fingerprint=(crop.shape,hashlib.sha256(crop.tobytes()).digest())
            if fingerprint in seen:continue
            seen.add(fingerprint);crops.append(crop)
        parsed=None;ocr_boxes=0;name_boxes=0;quantity_boxes=0;best_name_score=0.;best_quantity_score=0.
        variant_count=0;crop_diagnostics=[]
        for crop in crops:
            bgr=crop[:,:,::-1]
            # Run OCR on each independent anchor. A weak badge match must not
            # suppress the fixed compact-window fallback crop.
            enlarged=cv2.resize(bgr,None,fx=3,fy=3,interpolation=cv2.INTER_CUBIC)
            gray=cv2.cvtColor(bgr,cv2.COLOR_BGR2GRAY)
            gray=cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8)).apply(gray)
            enhanced=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
            variants=(enlarged,cv2.resize(enhanced,None,fx=4,fy=4,interpolation=cv2.INTER_CUBIC))
            crop_boxes=crop_names=crop_quantities=0
            for variant in variants:
                variant_count+=1
                result,_=self.reader(variant,use_cls=False)
                for box,text,score in result or []:
                    text=' '.join(str(text).split());score=float(score)
                    ocr_boxes+=1;crop_boxes+=1
                    quantity,uncertain=quantity_reading(text)
                    if quantity is not None:
                        quantity_boxes+=1;crop_quantities+=1;best_quantity_score=max(best_quantity_score,score)
                    elif score>=.65 and 2<=len(text)<=90 and re.search(r'[A-Za-zÀ-ÿ]',text):
                        name_boxes+=1;crop_names+=1;best_name_score=max(best_name_score,score)
                candidate=parse_reward(result,width=variant.shape[1])
                if candidate and (parsed is None or
                        (candidate['name_validated'],candidate['name_confidence'],candidate['confidence']) >
                        (parsed['name_validated'],parsed['name_confidence'],parsed['confidence'])):
                    parsed=candidate
            crop_diagnostics.append({'largura':int(crop.shape[1]),'altura':int(crop.shape[0]),
                                     'caixas':crop_boxes,'nomes':crop_names,'quantidades':crop_quantities})
        if parsed:parsed['sample_id']=hashlib.sha256(rgb.tobytes()).hexdigest()
        return {'reading':parsed,'__ocr_debug__':{
            'recorte_largura':int(rgb.shape[1]),'recorte_altura':int(rgb.shape[0]),
            'recortes_ocr':crop_diagnostics,'variantes_ocr':variant_count,'caixas_ocr':ocr_boxes,
            'candidatos_nome':name_boxes,'candidatos_quantidade':quantity_boxes,
            'melhor_confianca_nome':round(best_name_score,3),
            'melhor_confianca_quantidade':round(best_quantity_score,3)}}

    @staticmethod
    def crop(rgb,point=None):
        import cv2
        # Preserve the captured UI scale. Stretching an 800x599 Roblox client
        # to 1920x1080 distorts the notification text and degrades OCR.
        h,w=rgb.shape[:2]
        normalized=np.zeros((1080,1920,3),dtype=rgb.dtype)
        if w<=1920 and h<=1080:
            left=(1920-w)//2;top=(1080-h)//2
            normalized[top:top+h,left:left+w]=rgb
        else:
            normalized=cv2.resize(rgb,(1920,1080))
        x,y=point if point else (1075.5,596.5)
        # The reward banner moves relative to the item prompt at lower window
        # sizes. Include the full banner and both stacked and one-line layouts.
        # Compact-window notifications can sit well above the fullscreen
        # anchor; scan a taller central strip so OCR still sees the whole card.
        left=max(0,min(1920-650,int(x-250)));top=max(0,min(1080-420,int(y-260)))
        return normalized[top:top+420,left:left+650].copy()

    @staticmethod
    def fallback_crop(rgb):
        """Capture the game's center at its native scale when badge matching is weak."""
        h,w=rgb.shape[:2]
        if w>1920 or h>1080:return RewardReader.crop(rgb,(1075.5,596.5))
        normalized=np.zeros((1080,1920,3),dtype=rgb.dtype)
        left=(1920-w)//2;top=(1080-h)//2
        normalized[top:top+h,left:left+w]=rgb
        if (w,h)==(1920,1080):point=(1075.5,596.5)
        else:point=(left+w/2,top+h/2)
        return RewardReader.crop(normalized,point)

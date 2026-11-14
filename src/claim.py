"""Claim label geometry and OCR of name/weight, separate from acquisition."""
from pathlib import Path
import hashlib,re
import cv2
import numpy as np
from item_names import name_evidence


def parse_claim(lines,sample_id=None):
    for box,text,score in lines or []:
        match=re.fullmatch(r"\s*(.+?)\s*,\s*(\d+(?:[.,]\d+)?)\s*kg\s*",str(text),re.I)
        if not match or float(score)<.85:continue
        raw=match[1].strip();name,known,fragment=name_evidence(raw)
        weight=float(match[2].replace(',','.'))
        if not 0<weight<100000:continue
        return {'name':name,'raw_name':raw,'quantity':1,'weight_kg':weight,
                'confidence':float(score),'name_confidence':float(score),
                'name_known':known,'name_ambiguous':fragment,
                'name_validated':known and not fragment and score>=.90,
                'sample_id':sample_id,'source':'claim'}
    return None


class ClaimReader:
    def __init__(self,assets):
        self.templates={key:cv2.imdecode(np.fromfile(Path(assets)/('claim_'+key+'.png'),np.uint8),0)
                        for key in ('label','key')}
        self.ocr=None

    def scan(self,rgb):
        h,w=rgb.shape[:2];gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY);best=None
        scales=sorted({round(v,3) for v in (1.,h/1072,w/1920,(w/1920*h/1072)**.5) if .3<=v<=2})
        for scale in scales:
            template=cv2.resize(self.templates['label'],None,fx=scale,fy=scale)
            th,tw=template.shape;top=int(h*.15);bottom=int(h*.90)
            if th>=bottom-top or tw>=w:continue
            _,score,_,(x,y)=cv2.minMaxLoc(cv2.matchTemplate(gray[top:bottom],template,cv2.TM_CCOEFF_NORMED));y+=top
            if score<.80:continue
            # The white T circle must be next to Claim. A menu saying Claim
            # is not a fishing item. Match independently of the item's name.
            left=max(0,x-round(95*scale));right=min(w,x-round(20*scale))
            up=max(0,y-round(43*scale));down=min(h,y+round(32*scale))
            key=cv2.resize(self.templates['key'],None,fx=scale,fy=scale)
            area=gray[up:down,left:right]
            if area.shape[0]<key.shape[0] or area.shape[1]<key.shape[1]:continue
            _,key_score,_,_=cv2.minMaxLoc(cv2.matchTemplate(area,key,cv2.TM_CCOEFF_NORMED))
            if key_score<.73:continue
            if best is None or min(score,key_score)>best['score']:
                x0=max(0,x-round(6*scale));y0=max(0,y-round(32*scale))
                x1=min(w,x+round(460*scale));y1=min(h,y+round(27*scale))
                best={'point':((x+tw/2)/w,(y+th/2)/h),'score':float(min(score,key_score)),
                      'crop':rgb[y0:y1,x0:x1].copy()}
        return best

    def read(self,rgb):
        if self.ocr is None:
            from rapidocr_onnxruntime import RapidOCR
            self.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=1)
        result,_=self.ocr(cv2.resize(rgb[:,:,::-1],None,fx=3,fy=3,interpolation=cv2.INTER_CUBIC),use_cls=False)
        return parse_claim(result,hashlib.sha256(rgb.tobytes()).hexdigest())

"""Localização geométrica da barra e aprendizado conservador entre pescas."""
import cv2
import numpy as np
from detector import detect


def locate_bar(rgb,preferred=None):
    h,w=rgb.shape[:2]
    # Bordas compridas e paralelas distinguem o trilho da faixa móvel.
    gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
    edges=cv2.Canny(gray,20,60)
    joined=cv2.morphologyEx(edges,cv2.MORPH_CLOSE,np.ones((9,1),np.uint8))
    contours,_=cv2.findContours(joined,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    boxes=[cv2.boundingRect(c) for c in contours]
    complete_count=len(boxes)
    rails=cv2.morphologyEx(joined,cv2.MORPH_OPEN,np.ones((31,1),np.uint8))
    parts,_=cv2.findContours(rails,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    lines=[cv2.boundingRect(c) for c in parts if cv2.boundingRect(c)[3]>.20*h]
    for x1,y1,w1,h1 in lines:
        for x2,y2,w2,h2 in lines:
            if not 16<x2-x1<.10*w:continue
            if abs(y1-y2)>.03*h or abs(h1-h2)>.03*h:continue
            boxes.append((x1,min(y1,y2),x2+w2-x1,max(y1+h1,y2+h2)-min(y1,y2)))
    candidates=[]
    for index,(x,y,bw,bh) in enumerate(boxes):
        if not .18*h<bh<.7*h or not .07<bw/bh<.25 or bw<16:continue
        left=max(0,x-int(bw*.10));right=min(w,x+bw+int(bw*.10))
        top=max(0,y-2);bottom=min(h,y+bh+2)
        crop=rgb[top:bottom,left:right]
        reading=detect(crop)
        if reading is None:continue
        # Bordas externas têm que atravessar boa parte do trilho.
        side1=np.any(edges[y:y+bh,max(0,x-2):x+4]>0,axis=1).mean()
        side2=np.any(edges[y:y+bh,max(0,x+bw-4):min(w,x+bw+2)]>0,axis=1).mean()
        confidence=min(side1,side2)
        if confidence<.45:continue
        roi=[left/w,top/h,(right-left)/w,(bottom-top)/h]
        distance=sum(abs(a-b) for a,b in zip(roi,preferred)) if preferred else 0
        candidates.append((confidence+(.12 if index<complete_count else 0)-min(.15,distance*.1),roi))
    if not candidates:return None
    score,roi=max(candidates,key=lambda a:a[0])
    return {'roi':roi,'confidence':min(1.,float(score))}


class AutoCalibration:
    def __init__(self,profile=None):
        self.profile=profile if isinstance(profile,dict) else {}
        self.begin()

    def begin(self):
        self.pending=[];self.locked=False;self.roi=None
        self.samples=0;self.valid=0
        self.missing_since=None;self.recoveries=0

    def check_tracking(self,reading,now):
        if reading is not None:
            self.missing_since=None;return False
        if self.missing_since is None:self.missing_since=now
        if self.locked and now-self.missing_since>=.5:
            self.locked=False;self.pending=[];self.roi=None
            self.samples=0;self.valid=0;self.recoveries+=1
            return True
        return False

    def observe(self,candidate):
        if self.locked:return None
        if not candidate or candidate['confidence']<.45:
            self.pending=[];return None
        roi=candidate['roi']
        if self.pending and max(abs(a-b) for a,b in zip(roi,self.pending[-1]))>.015:
            self.pending=[]
        self.pending.append(roi)
        if len(self.pending)<3:return None
        self.roi=np.median(self.pending[-3:],axis=0).tolist();self.locked=True
        self.missing_since=None
        return self.roi

    def sample(self,reading):
        if self.locked:
            self.samples+=1;self.valid+=int(reading is not None)

    def finish(self):
        # Uma detecção isolada ou rodada com leituras ruins não ensina o perfil.
        if not self.locked or self.samples<25 or self.valid/self.samples<.75:return None
        old=self.profile.get('roi')
        if old and max(abs(a-b) for a,b in zip(old,self.roi))<.025:
            learned=[.75*a+.25*b for a,b in zip(old,self.roi)]
        else:learned=list(self.roi)
        self.profile={'roi':learned,'rounds':int(self.profile.get('rounds',0))+1,
                      'quality':round(self.valid/self.samples,3)}
        return self.profile


def selection_roi(start,end,size):
    """Arrastar em qualquer direção; retorna região normalizada ou None."""
    w,h=size
    x1,x2=sorted((max(0,min(w,start[0])),max(0,min(w,end[0]))))
    y1,y2=sorted((max(0,min(h,start[1])),max(0,min(h,end[1]))))
    if x2-x1<16 or y2-y1<60 or x2-x1>w*.3:return None
    return [x1/w,y1/h,(x2-x1)/w,(y2-y1)/h]

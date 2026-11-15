"""Local coherent cyan particles distinguish bites from a fishing-zone glow."""
import cv2
import numpy as np


class SplashReader:
    def __init__(self):self.reset()
    def reset(self):
        self.baseline=None;self.previous_mass=0.;self.previous_time=None
        self.last_burst=-float('inf');self.geometry=None;self.stats={}
        self.pending=None

    def observe(self,rgb,point,now,armed=True):
        if not point:self.reset();return False
        h,w=rgb.shape[:2];cx,cy=point[0]*w,point[1]*h
        geometry=(w,h,tuple(point))
        if self.geometry!=geometry:self.reset();self.geometry=geometry
        scale=max(.2,min(w,h)/1072)**2
        radius=max(35,round(min(w,h)*.19))
        x0,x1=max(0,int(cx-radius)),min(w,int(cx+radius))
        y0,y1=max(0,int(cy-radius)),min(h,int(cy+radius))
        crop=rgb[y0:y1,x0:x1].astype(np.int16)
        rr,gg,bb=[crop[:,:,i] for i in range(3)]
        yy,xx=np.ogrid[y0:y1,x0:x1]
        # Bites throw compact cyan droplets. The zone effect is largely white
        # arcs, fish silhouettes and fragmented mist, not coherent droplets.
        mask=((gg>210)&(bb>242)&(gg-rr>55)&(rr<195)&
              ((xx-cx)**2+(yy-cy)**2<radius*radius)).astype(np.uint8)
        _,labels,components,_=cv2.connectedComponentsWithStats(mask)
        masses=[]
        for identity,(x,y,bw,bh,area) in enumerate(components[1:],1):
            if not max(4,85*scale)<=area<=1200*scale:continue
            ys,xs=np.where(labels[y:y+bh,x:x+bw]==identity)
            if len(xs)<3:continue
            eigen=np.linalg.eigvalsh(np.cov(np.stack((xs,ys))))
            aspect=float(np.sqrt(eigen[1]/max(.1,eigen[0])))
            if 1.35<=aspect<=8:masses.append(float(area))
        mass=sum(sorted(masses,reverse=True)[:4])
        coherence=mass/max(1,int(mask.sum()))
        feature=mass/scale if len(masses)>=2 and coherence>=.72 else 0.
        first=self.baseline is None or self.previous_time is None or now-self.previous_time>1.
        if first:self.baseline=feature;self.previous_mass=feature
        rise=feature-self.previous_mass
        candidate=(not first and armed and feature>self.baseline*1.35+40
                   and now-self.last_burst>=1.5)
        if self.pending is not None and now-self.pending>.25:self.pending=None
        sustained=candidate and self.pending is not None and .025<=now-self.pending<=.25
        strong=candidate and len(masses)>=3 and coherence>=.90 and rise>max(25,feature*.12)
        event=strong or sustained
        if event or not candidate:self.pending=None
        elif rise>max(25,feature*.12) and self.pending is None:self.pending=now
        self.stats={'particles':len(masses),'coherence':round(coherence,3),
                    'mass':round(feature,1),'baseline':round(self.baseline,1),
                    'armed':bool(armed),'detected':bool(event)}
        # Learn during arming too. Keep cooldown/history across brief disarmed
        # intervals; a sustained bright frame cannot repeatedly trigger clicks.
        dt=.05 if self.previous_time is None else max(0,min(1.,now-self.previous_time))
        alpha=1-np.exp(-dt/1.2)
        if not event:self.baseline+=(feature-self.baseline)*alpha
        self.previous_mass=feature;self.previous_time=now
        if event:self.last_burst=now
        return bool(event)

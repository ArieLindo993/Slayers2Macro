"""Coherent cyan or small radial blue droplets distinguish bites from zone glow."""
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
        blue_masses,blue_coherence,spread=self.blue_droplets(crop,cx-x0,cy-y0,radius,scale)
        blue_mass=sum(blue_masses)/scale
        blue_valid=len(blue_masses)>=2 and blue_coherence>=.50*min(1.,np.sqrt(scale)) and spread>=.55 and blue_mass>=20
        blue_feature=blue_mass*3 if blue_valid else 0.
        source='cyan' if feature else 'none'
        if blue_feature>feature:
            feature=blue_feature;masses=blue_masses;coherence=blue_coherence;source='blue_radial'
        first=self.baseline is None or self.previous_time is None or now-self.previous_time>1.
        if first:self.baseline=feature;self.previous_mass=feature
        rise=feature-self.previous_mass
        candidate=(not first and armed and feature>self.baseline*1.35+40
                   and now-self.last_burst>=1.5)
        if self.pending is not None and now-self.pending>.25:self.pending=None
        sustained=candidate and self.pending is not None and .025<=now-self.pending<=.25
        strong_shape=(len(masses)>=3 and coherence>=.90) or (
            source=='blue_radial' and blue_mass>=30 and (len(masses)>=3 or coherence>=.85))
        strong=candidate and strong_shape and rise>max(25,feature*.12)
        event=strong or sustained
        if event or not candidate:self.pending=None
        elif rise>max(25,feature*.12) and self.pending is None:self.pending=now
        self.stats={'particles':len(masses),'coherence':round(coherence,3),
                    'mass':round(feature,1),'baseline':round(self.baseline,1),
                    'source':source,'blue_particles':len(blue_masses),
                    'blue_mass':round(blue_mass,1),'blue_coherence':round(blue_coherence,3),
                    'blue_spread':round(spread,3),
                    'capture_interval_ms':None if self.previous_time is None else round((now-self.previous_time)*1000,1),
                    'burst_onset':bool(not first and feature>self.baseline*1.35+40 and rise>max(25,feature*.12)),
                    'armed':bool(armed),'detected':bool(event)}
        # Learn during arming too. Keep cooldown/history across brief disarmed
        # intervals; a sustained bright frame cannot repeatedly trigger clicks.
        dt=.05 if self.previous_time is None else max(0,min(1.,now-self.previous_time))
        alpha=1-np.exp(-dt/1.2)
        if not event:self.baseline+=(feature-self.baseline)*alpha
        self.previous_mass=feature;self.previous_time=now
        if event:self.last_burst=now
        return bool(event)

    @staticmethod
    def blue_droplets(crop,cx,cy,radius,scale):
        """Small saturated droplets fan out near the marked landing point.

        Zone fish and mist contribute to the denominator but cannot issue a
        command unless compact, radially aligned droplets dominate the mask.
        This lane complements the larger, brighter cyan splash detector.
        """
        rr,gg,bb=[crop[:,:,i] for i in range(3)]
        yy,xx=np.ogrid[:crop.shape[0],:crop.shape[1]]
        # Downsampling dilutes a small bright core into surrounding water.
        # Adjust only its minimum blue brightness; retain colour separation.
        shrink=1-min(1.,np.sqrt(scale))
        mask=((bb>=240-30*shrink)&(bb-gg>=40)&(gg-rr>=65)&(gg>=130)&(gg<=215)&(rr<150)&
              ((xx-cx)**2+(yy-cy)**2<radius*radius)).astype(np.uint8)
        size=max(1,round(2*np.sqrt(scale)))
        if size>1:
            mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,np.ones((size,size),np.uint8))
        _,labels,components,centers=cv2.connectedComponentsWithStats(mask)
        core=[];outer=[]
        for identity,((x,y,bw,bh,area),(px,py)) in enumerate(zip(components[1:],centers[1:]),1):
            if not max(3,4*scale)<=area<=250*scale or area/(bw*bh)<.40:continue
            vector=np.array([px-cx,py-cy]);distance=float(np.linalg.norm(vector))
            if not max(2,3*np.sqrt(scale))<=distance<=radius*.60:continue
            ys,xs=np.where(labels[y:y+bh,x:x+bw]==identity)
            eigen,axes=np.linalg.eigh(np.cov(np.stack((xs,ys))))
            aspect=float(np.sqrt(eigen[1]/max(.1,eigen[0])))
            direction=vector/distance
            radial=abs(float(np.dot(axes[:,1],direction)))
            # A few pixels cannot reliably describe an ellipse's axis. Such
            # cores still need proximity, spread and group-level dominance.
            tiny=scale<.75 and area<=12
            if not tiny and (not 1.25<=aspect<=8 or radial<.70):continue
            hull=cv2.convexHull(np.column_stack((xs,ys)).astype(np.float32))
            if area/max(area,cv2.contourArea(hull))<.82:continue
            if distance<=radius*.27:core.append((float(area),direction))
            if radial>=.90:outer.append((float(area),direction))
        def summarize(droplets):
            droplets=sorted(droplets,key=lambda item:item[0],reverse=True)[:12]
            masses=[area for area,_ in droplets];spread=0.
            if len(droplets)>=2:
                directions=np.asarray([direction for _,direction in droplets])
                spread=float(np.arccos(np.clip((directions@directions.T).min(),-1,1)))
            return masses,sum(masses)/max(1,int(mask.sum())),spread
        result=summarize(core);wide=summarize(outer)
        # Later frames spread farther out. A wider group needs much stronger
        # shape alignment and dominance so rotating zone fragments cannot win.
        if len(wide[0])>=2 and wide[1]>=.85 and wide[2]>=.55 and sum(wide[0])>sum(result[0]):
            result=wide
        return result

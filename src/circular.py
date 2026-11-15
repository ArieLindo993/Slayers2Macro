"""Visual reader for the November circular fishing UI.

Only screen pixels are used. Missing arrow frames carry no new command.
The segmented ring must match before either arrow can issue an instruction.
"""
from dataclasses import dataclass
from pathlib import Path
import math
import cv2
import numpy as np


@dataclass
class CircularReading:
    center: tuple
    radius: float
    score: float
    mouse_button: object = None
    marker: object = None
    target: float = 0.
    band: float = .25
    complete: bool = False
    key: object = None
    presses: int = 0
    marker_source: object = None


class CircularReader:
    def __init__(self, assets):
        cv2.setNumThreads(2)
        self.templates={}
        for key in ('ring','ring_mask','green_right','red_left','red_left_faint'):
            raw=np.fromfile(Path(assets)/('circle_'+key+'.png'),np.uint8)
            self.templates[key]=cv2.imdecode(raw,cv2.IMREAD_GRAYSCALE)
        self.reset()

    def reset(self):
        self.geometry=None
        self.shape=None
        self.last_mouse_scores={}
        self.last_cue_angle=None
        self.visible=False;self.stats={'reason':'not_scanned'}
        self.scaled_templates={}

    def read(self,rgb,search_roi=None):
        h,w=rgb.shape[:2]
        if self.shape!=(h,w):self.reset();self.shape=(h,w)
        self.visible=False;self.last_mouse_scores={};self.last_cue_angle=None
        self.stats={'reason':'ring_missing'}
        # Search at a bounded working resolution. Reacquisition is independent
        # of marker colour, position and whether an arrow is currently visible.
        factor=min(1.,800/w)
        image=cv2.resize(rgb,None,fx=factor,fy=factor,interpolation=cv2.INTER_AREA)
        # Empty waiting frames need no expensive multiscale ring search.
        a=image.astype(np.int16)
        neon=(a[:,:,1]>170)&(a[:,:,1]-a[:,:,0]>45)&(a[:,:,1]-a[:,:,2]>50)
        if self.geometry is None and int(neon.sum())<max(8,int(h*w*factor*factor*.000025)):
            self.stats={'reason':'no_green_pixels'};return None
        gray=cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
        edges=cv2.Canny(gray,25,60)
        scales=[self.geometry[2]] if self.geometry else []
        base=h/1072*factor
        scales+= [base*v for v in (1.,.85,1.15,.7,1.3)]
        best=None
        for scale in dict.fromkeys(round(s,4) for s in scales):
            size=max(24,round(360*scale))
            if size>=min(edges.shape):continue
            if size not in self.scaled_templates:
                self.scaled_templates[size]=(
                    cv2.resize(self.templates['ring'],(size,size),interpolation=cv2.INTER_AREA),
                    cv2.resize(self.templates['ring_mask'],(size,size),interpolation=cv2.INTER_NEAREST))
            template,mask=self.scaled_templates[size]
            x0,y0,x1,y1=0,round(h*factor*.12),edges.shape[1],round(h*factor*.94)
            if search_roi is not None:
                rx,ry,rw,rh=search_roi
                x0,y0=round(rx*w*factor),round(ry*h*factor)
                x1,y1=round((rx+rw)*w*factor),round((ry+rh)*h*factor)
            if self.geometry and scale==round(self.geometry[2],4):
                cx,cy,_=self.geometry
                x0=max(x0,round(cx-size*.65));y0=max(y0,round(cy-size*.65))
                x1=min(x1,round(cx+size*.65));y1=min(y1,round(cy+size*.65))
            area=edges[y0:y1,x0:x1]
            if area.shape[0]<size or area.shape[1]<size:continue
            matches=cv2.matchTemplate(area,template,cv2.TM_CCORR_NORMED,mask=mask)
            matches=np.nan_to_num(matches,nan=0.,posinf=0.,neginf=0.)
            _,score,_,point=cv2.minMaxLoc(matches)
            if best is None or score>best[0]:best=(score,x0+point[0]+size/2,y0+point[1]+size/2,scale)
            if score>.60 or (self.geometry and scale==round(self.geometry[2],4) and score>.55):break
        if best is None or best[0]<.46:
            self.stats={'reason':'ring_missing','ring_score':round(best[0],3) if best else 0.}
            return None
        score,x,y,scale=best
        self.geometry=(x,y,scale)
        cx,cy,r=x/factor,y/factor,166*scale/factor
        self.visible=True
        self.stats={'reason':'target_missing','ring_score':round(score,3),
                    'center':[round(cx,1),round(cy,1)],'radius':round(r,1)}
        # Target ticks form a curved group in the ring's upper sector. A green
        # scene alone is insufficient: both segmented side arcs matched above.
        x0,x1=max(0,int(cx-r*1.12)),min(w,int(cx+r*1.12)+1)
        y0,y1=max(0,int(cy-r*1.12)),min(h,int(cy+r*1.12)+1)
        pixels=rgb[y0:y1,x0:x1]
        yy,xx=np.ogrid[y0:y1,x0:x1]
        dx,dy=xx-cx,yy-cy
        distance=np.hypot(dx,dy)
        angle=np.arctan2(dx,-dy)/(2*math.pi)
        rr,gg,bb=[pixels[:,:,i].astype(np.int16) for i in range(3)]
        ring=(distance>r*.85)&(distance<r*1.08)
        green=ring&(gg>170)&(gg-rr>45)&(gg-bb>50)
        top=green&(np.abs(angle)<.22)
        if np.count_nonzero(top)<max(8,r*r*.007):
            return None
        angles=angle[top]
        target=float(np.median(angles));band=float(np.percentile(angles,95)-np.percentile(angles,5))
        marker=self.read_marker(pixels,cx-x0,cy-y0,r)
        marker_source='needle' if marker is not None else None
        # Commands are the coloured chevrons next to the marker. The white
        # arrows above the ring are not mouse instructions.
        mouse_button=self.read_mouse_cue(rgb,cx,cy,r,marker)
        if marker is None and mouse_button is not None and self.last_cue_angle is not None:
            marker=self.last_cue_angle/(2*math.pi);marker_source='chevrons'
        center=(distance<r*.36)
        gold=center&(rr>180)&(gg>140)&(bb<130)
        complete=np.count_nonzero(gold)>r*r*.018
        key,presses=self.read_keys(rgb,cx,cy,r) if not complete else (None,0)
        self.stats.update(reason='complete' if complete else 'tracking' if marker is not None else 'needle_missing',
                          marker=round(marker,4) if marker is not None else None,
                          marker_source=marker_source,target=round(target,4),band=round(band,4),
                          mouse_button=mouse_button,**self.last_mouse_scores)
        return CircularReading((cx,cy),r,score,mouse_button,marker,target,band,bool(complete),key,presses,marker_source)

    @staticmethod
    def read_marker(rgb,cx,cy,r):
        """Read the radial white needle, not the median of white scenery."""
        a=rgb.astype(np.int16);rr,gg,bb=[a[:,:,i] for i in range(3)]
        yy,xx=np.ogrid[:rgb.shape[0],:rgb.shape[1]]
        distance=np.hypot(xx-cx,yy-cy)
        mask=((distance>r*.78)&(distance<r*1.15)&(rr>210)&(gg>210)&(bb>195)).astype(np.uint8)
        _,labels,stats,centers=cv2.connectedComponentsWithStats(mask)
        best=None
        for identity,((x,y,w,h,area),(px,py)) in enumerate(zip(stats[1:],centers[1:]),1):
            if not max(4,r*r*.0008)<=area<=r*r*.04:continue
            ys,xs=np.where(labels[y:y+h,x:x+w]==identity)
            if len(xs)<3:continue
            eigen,axes=np.linalg.eigh(np.cov(np.stack((xs,ys))))
            aspect=np.sqrt(eigen[1]/max(.1,eigen[0]))
            vector=np.array([px-cx,py-cy]);norm=float(np.linalg.norm(vector))
            if not r*.85<=norm<=r*1.10:continue
            radial=abs(float(np.dot(axes[:,1],vector/norm)))
            if aspect<1.5 or radial<.80:continue
            quality=area*radial
            if best is None or quality>best[0]:best=(quality,math.atan2(vector[0],-vector[1])/(2*math.pi))
        return best[1] if best else None

    def read_mouse_cue(self,rgb,cx,cy,r,marker):
        h,w=rgb.shape[:2]
        x0,x1=max(0,int(cx-r*1.55)),min(w,int(cx+r*1.55)+1)
        y0,y1=max(0,int(cy-r*1.55)),min(h,int(cy+r*1.55)+1)
        crop=rgb[y0:y1,x0:x1].astype(np.int16)
        rr,gg,bb=[crop[:,:,i] for i in range(3)]
        yy,xx=np.ogrid[y0:y1,x0:x1];distance=np.hypot(xx-cx,yy-cy)
        annulus=(distance>r*1.15)&(distance<r*1.54)
        masks=[(gg>150)&(gg-rr>45)&(gg-bb>45),
               (rr>125)&(rr-gg>25)&(rr-bb>10)]
        u,v=np.meshgrid(np.arange(-58,59,dtype=np.float32),np.arange(192,257,dtype=np.float32))
        best=[];orientations=[]
        for mask,key in zip(masks,('green_right','red_left')):
            mask=(mask&annulus).astype(np.uint8)
            _,_,stats,centers=cv2.connectedComponentsWithStats(mask)
            candidates=[]
            for (x,y,bw,bh,area),(px,py) in zip(stats[1:],centers[1:]):
                if not max(3,r*r*.00025)<=area<=r*r*.03:continue
                if not .08<=area/(bw*bh)<=.88:continue
                theta=math.atan2(px+x0-cx,-(py+y0-cy))
                candidates.append((area,theta))
            angles=([marker*2*math.pi] if marker is not None else [])
            candidates=sorted(candidates,reverse=True)[:3]
            if candidates:
                mean=math.atan2(sum(area*math.sin(theta) for area,theta in candidates),
                                sum(area*math.cos(theta) for area,theta in candidates))
                angles += [mean,mean-.04,mean+.04]
            angles += [theta for _,theta in candidates]
            score=0.;orientation=None
            for theta in angles:
                sx=cx+(u*math.cos(theta)+v*math.sin(theta))*r/166
                sy=cy+(u*math.sin(theta)-v*math.cos(theta))*r/166
                strip=cv2.remap(rgb,sx.astype(np.float32),sy.astype(np.float32),cv2.INTER_LINEAR)
                a=strip.astype(np.int16);red,green,blue=[a[:,:,j] for j in range(3)]
                binary=((green>150)&(green-red>45)&(green-blue>45)) if key=='green_right' else ((red>125)&(red-green>25)&(red-blue>10))
                references=[self.templates[key]]
                if key=='red_left':references.append(self.templates['red_left_faint'])
                for reference in references:
                    values=cv2.matchTemplate(binary.astype(np.uint8)*255,reference,cv2.TM_CCOEFF_NORMED)
                    value=float(np.nan_to_num(values,nan=0.).max())
                    if value>score:score=value;orientation=theta
            best.append(score)
            orientations.append(orientation)
        self.last_mouse_scores={'green_right':round(best[0],3),'red_left':round(best[1],3)}
        if max(best)>=.64 and abs(best[0]-best[1])>=.08:
            winner=0 if best[0]>best[1] else 1
            self.last_cue_angle=orientations[winner]
            return 'right' if winner==0 else 'left'
        return None

    @staticmethod
    def read_keys(rgb,cx,cy,r):
        """Active side card + gold countdown + one/two dots; ignore grey keys."""
        h,w=rgb.shape[:2];candidates=[]
        for key,direction in (('A',-1),('D',1)):
            x=cx+direction*r*1.65
            left,right=round(x-r*.32),round(x+r*.32)
            top,bottom=round(cy-r*.32),round(cy+r*.47)
            if left<0 or right>w or top<0 or bottom>h:continue
            crop=rgb[top:bottom,left:right].astype(np.int16)
            yy,xx=np.ogrid[top:bottom,left:right]
            distance=np.hypot(xx-x,yy-cy)
            rr,gg,bb=[crop[:,:,i] for i in range(3)]
            white=(rr>170)&(gg>170)&(bb>170)&(np.maximum.reduce([rr,gg,bb])-np.minimum.reduce([rr,gg,bb])<50)
            inner=(np.abs(xx-x)<r*.13)&(np.abs(yy-cy)<r*.12)
            if white[inner].mean()<.45:continue
            gold=(rr>185)&(gg>140)&(bb<145)&(rr-bb>65)
            ring=gold&(distance>r*.19)&(distance<r*.29)
            if ring.sum()<max(6,r*r*.004):continue
            dots=gold&(yy>cy+r*.30)&(yy<cy+r*.43)&(np.abs(xx-x)<r*.15)
            count,_,stats,_=cv2.connectedComponentsWithStats(dots.astype(np.uint8))
            sizes=stats[1:,cv2.CC_STAT_AREA] if count>1 else []
            n=int(sum(max(2,r*r*.00065)<=area<=r*r*.008 for area in sizes))
            if n in (1,2):candidates.append((key,n))
        return candidates[0] if len(candidates)==1 else (None,0)


class CircularCommand:
    """Green/right selects M2; red/left selects M1. None releases both."""
    def __init__(self):self.reset()

    def reset(self):
        self.button=None
        self.last_visible=None
        self.instruction=None
        self.last_instruction=None
        self.edge_paused=None;self.reason='no_cue'

    def step(self,reading,now):
        if reading is not None and reading.complete:
            self.reset()
            return None
        if reading is None:
            if self.last_visible is None or now-self.last_visible>=.15:self.reset()
        else:
            self.last_visible=now
            if reading.mouse_button in ('left','right'):
                if self.instruction!=reading.mouse_button:self.edge_paused=None
                self.instruction=reading.mouse_button;self.last_instruction=now
            preferred=self.instruction if self.last_instruction is not None and now-self.last_instruction<=.35 else None
            if preferred is None and reading.marker is not None:
                # Re-read position after a missing/stale instruction as well.
                error=(reading.target-reading.marker+.5)%1.-.5
                margin=max(.006,min(.025,reading.band*.08))
                if error>margin:preferred='right'
                elif error<-margin:preferred='left'
            self.button=preferred;self.reason='direction' if preferred else 'no_cue'
            if reading.marker is None and (self.last_instruction is None or now-self.last_instruction>.20):
                self.button=None;self.reason='needle_missing'
                return self.button
            if preferred is not None:
                if reading.marker is None:
                    if self.edge_paused==preferred:self.button=None;self.reason='green_edge'
                else:
                    offset=(reading.marker-reading.target+.5)%1.-.5
                    toward=offset*(1 if preferred=='right' else -1)
                    half=max(.015,reading.band*.5)
                    # Pause inside the edge towards which this input pulls.
                    # A separate resume margin prevents flicker/chattering;
                    # no assumption about inertia past the centre is needed.
                    limit=half*(.35 if self.edge_paused==preferred else .75)
                    if toward>=limit:
                        self.button=None;self.edge_paused=preferred;self.reason='green_edge'
                    else:self.edge_paused=None
        return self.button


class KeyPromptCommand:
    """Propose bounded taps independently of the held mouse command.

    A persistent request is one event. Counts falling after the first tap do
    not create another event. The caller supplies a fresh frame per step.
    """
    def __init__(self):self.reset()

    def reset(self):
        self.key=None;self.remaining=0;self.next_tap=0.;self.absent_since=None

    def step(self,reading,now):
        if reading is not None and reading.complete:
            self.reset();return []
        if reading is None or reading.key is None:
            if self.absent_since is None:self.absent_since=now
            if now-self.absent_since>=.25:self.reset()
            return []
        self.absent_since=None
        if self.key!=reading.key:
            self.key=reading.key;self.remaining=reading.presses;self.next_tap=now
        if self.remaining and now>=self.next_tap:
            self.remaining-=1;self.next_tap=now+.10
            return [self.key]
        return []

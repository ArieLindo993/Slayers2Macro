"""Temporal bright-cyan bite particles near the marked water point."""
import cv2
import numpy as np


class SplashReader:
    def __init__(self):self.reset()
    def reset(self):
        self.baseline=None;self.previous=None;self.since=None;self.last_burst=-float('inf')

    def observe(self,rgb,point,now,armed=True):
        if not point or not armed:self.reset();return False
        h,w=rgb.shape[:2];cx,cy=point[0]*w,point[1]*h
        radius=max(40,round(min(w,h)*.15))
        x0,x1=max(0,int(cx-radius)),min(w,int(cx+radius))
        y0,y1=max(0,int(cy-radius)),min(h,int(cy+radius))
        crop=rgb[y0:y1,x0:x1].astype(np.int16)
        rr,gg,bb=[crop[:,:,i] for i in range(3)]
        mask=((gg>165)&(bb>220)&(gg-rr>35)&(bb-rr>55)).astype(np.uint8)
        count=float(mask.sum());scale=max(.2,min(w,h)/1072)**2
        if self.baseline is None or self.previous.shape!=mask.shape:
            self.baseline=count;self.previous=mask;return False
        changed=int(((mask>0)&(self.previous==0)).sum());self.previous=mask
        burst=count>self.baseline*1.6+35*scale and changed>15*scale
        # Debounce two distinct captures, but allow a sustained cyan burst on
        # the second capture after the initial particles have stopped changing.
        if self.since is not None:
            burst=count>self.baseline*1.6+35*scale
        if burst and now-self.last_burst>1.5:
            if self.since is None:self.since=now
            elif .025<=now-self.since<=.35:
                self.last_burst=now;self.since=None;return True
        else:
            self.since=None
            self.baseline=.92*self.baseline+.08*count
        return False

"""Sinais visuais da gravação; não lê memória do Roblox."""
from pathlib import Path
import cv2
import numpy as np
from item_icons import reward_icon
from item_history import RewardReader


class Signals:
    def __init__(self, assets):
        self.templates={}
        cv2.setNumThreads(2)
        for name in ('collect','collect_small','collect_small2','collect_medium','collect_user','exit','reward'):
            # imdecode permite caminhos Unicode no Windows.
            raw=np.fromfile(Path(assets)/(name+'.png'),np.uint8)
            template=cv2.imdecode(raw,cv2.IMREAD_GRAYSCALE)
            if template is None:raise RuntimeError('Indicador visual ausente: '+name)
            self.templates[name]=template
        self.collect_templates=[self.templates[n] for n in ('collect','collect_small','collect_small2','collect_medium')]
        for scale in (.75,.85,1.,1.15,1.3,1.5):
            self.collect_templates.append(cv2.resize(self.templates['collect_user'],None,fx=scale,fy=scale))

    def scan(self,rgb,fishing_only=False):
        cv2.setNumThreads(2)
        h,w=rgb.shape[:2]
        native_gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
        # Prefer a centre-anchored, fixed-size notification when its template
        # matches in the unscaled game image. Scaling first can stretch a
        # partial match into a false positive and crop the name incorrectly.
        reward=False;reward_point=None;reward_score=0.
        reward_rgb=rgb;reward_gray=native_gray;reward_layout='scaled'
        if (w,h)!=(1920,1080) and w<=1920 and h<=1080:
            reference=np.zeros((1080,1920,3),dtype=rgb.dtype)
            left=(1920-w)//2;top=(1080-h)//2
            reference[top:top+h,left:left+w]=rgb
            reference_gray=cv2.cvtColor(reference,cv2.COLOR_RGB2GRAY)
            # The compact Roblox client can place its reward notice above the
            # fullscreen anchor. The old y=490 lower bound discarded it.
            found,point,score=self.match(reference_gray,self.templates['reward'],(600,300,1400,850),.91)
            if found:
                reward=True;reward_point=point;reward_score=score
                reward_rgb=reference;reward_gray=reference_gray;reward_layout='native'
        # Keep support for Roblox clients whose UI scales with the window.
        if not reward:
            th,tw=self.templates['reward'].shape
            scaled_template=cv2.resize(self.templates['reward'],(max(1,round(tw*w/1920)),max(1,round(th*h/1080))),interpolation=cv2.INTER_AREA)
            search=(round(.25*w),round(.15*h),round(.75*w),round(.85*h))
            reward,native_point,reward_score=self.match(native_gray,scaled_template,search,.91)
            if reward:reward_point=(native_point[0]*1920/w,native_point[1]*1080/h)
            reward_gray=cv2.resize(native_gray,(1920,1080),interpolation=cv2.INTER_LINEAR)
            reward_rgb=rgb;reward_layout='scaled'
        # Other fishing indicators keep their established proportional search.
        gray=cv2.resize(native_gray,(1920,1080),interpolation=cv2.INTER_LINEAR)
        fishing,_,exit_score=self.match(gray,self.templates['exit'],(760,950,1170,1080),.83)
        reward_data={'reward':reward,'reward_point':reward_point if reward else None,
                     'reward_icon':reward_icon(reward_rgb,reward_point) if reward else None,
                     'reward_crop':RewardReader.crop(reward_rgb,reward_point) if reward else None,
                     'reward_score':reward_score,
                     'reward_layout':reward_layout,
                     'reward_quality':self.reward_quality(reward_gray,reward_point) if reward else 0.}
        # Com a barra sendo controlada, o indicador independente basta.
        # Se ele sumir, procure coleta/recompensa já nesta mesma captura.
        if fishing_only and fishing:
            return {'fishing':True,'loot':None,'collect_score':0.,'exit_score':exit_score,**reward_data}
        results=[]
        for template in self.collect_templates:
            results.append(self.match(gray,template,(0,0,1920,1080),.80))
        found,point,score=max(results,key=lambda r:r[2])
        if not found and (w,h)!=(1920,1080):
            native_results=[self.match(native_gray,t,(0,0,w,h),.80) for t in self.collect_templates
                            if t.shape[0]<=h and t.shape[1]<=w]
            if native_results:
                native_found,native_point,native_score=max(native_results,key=lambda r:r[2])
                if native_found:
                    found=True;score=native_score
                    point=(native_point[0]*1920/w,native_point[1]*1080/h)
        return {'fishing':fishing,'loot':(point[0]/1920,point[1]/1080) if found else None,
                'collect_score':score,'exit_score':exit_score,**reward_data}

    def reward_quality(self,gray,point):
        """Contrast of the matched notification text estimates its fade opacity.

        Template correlation alone is insensitive to fade-in/fade-out.
        Compare the same text, not the item artwork (which may be dark).
        """
        template=self.templates['reward'];h,w=template.shape
        x=round(point[0]-w/2);y=round(point[1]-h/2)
        patch=gray[y:y+h,x:x+w]
        if patch.shape!=template.shape:return 0.
        bright=template>=np.percentile(template,85);dark=template<=np.percentile(template,25)
        reference=float(np.median(template[bright]))-float(np.median(template[dark]))
        contrast=float(np.median(patch[bright]))-float(np.median(patch[dark]))
        opacity=max(0.,min(1.,contrast/max(1.,reference)))
        left=round(point[0]-99.5);top=round(point[1]-42.5)
        icon=gray[max(0,top):top+48,max(0,left):left+44].astype(np.float32)
        # Artwork can finish fading after the quantity text. Prefer its sharper
        # later frame too, while text visibility remains the dominant factor.
        detail=(float(np.abs(np.diff(icon,axis=0)).mean())+float(np.abs(np.diff(icon,axis=1)).mean())) if min(icon.shape)>1 else 0.
        return opacity*(.8+.2*min(1.,detail/20.))

    def find_bar(self,rgb,preferred,stage):
        """O candidato e a confirmação da pesca pertencem à MESMA captura."""
        from calibration import search_bar
        cv2.setNumThreads(2)
        gray=cv2.resize(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY),(1920,1080))
        fishing,_,_=self.match(gray,self.templates['exit'],(760,950,1170,1080),.83)
        return {'fishing':fishing,'candidate':search_bar(rgb,preferred,stage) if fishing else None}

    @staticmethod
    def match(gray,template,box,threshold):
        x,y,x2,y2=box
        area=gray[y:y2,x:x2]
        scores=cv2.matchTemplate(area,template,cv2.TM_CCOEFF_NORMED)
        _,score,_,loc=cv2.minMaxLoc(scores)
        th,tw=template.shape
        return score>=threshold,(x+loc[0]+tw/2,y+loc[1]+th/2),float(score)

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
        # Prefer the original template, but keep its best location even when
        # it is too weak to confirm. The OCR can use that location as an anchor.
        reward=False;reward_point=None;reward_score=0.;reward_scale=1.
        candidate_point=None;candidate_score=0.;candidate_scale=None
        candidate_rgb=rgb;quality_point=None
        reward_rgb=rgb;reward_gray=native_gray;reward_template=self.templates['reward']
        reward_layout='scaled';scale_x=scale_y=1.
        if (w,h)!=(1920,1080) and w<=1920 and h<=1080:
            reference=np.zeros((1080,1920,3),dtype=rgb.dtype)
            left=(1920-w)//2;top=(1080-h)//2
            reference[top:top+h,left:left+w]=rgb
            reference_gray=cv2.cvtColor(reference,cv2.COLOR_RGB2GRAY)
            # The compact client can move the notice above its fullscreen
            # anchor. The search now covers the central game area vertically.
            found,point,score=self.match(reference_gray,self.templates['reward'],(600,300,1400,850),.91)
            candidate_point=point;candidate_score=score;candidate_scale=1.
            candidate_rgb=reference
            if found:
                reward=True;reward_point=point;reward_score=score;reward_scale=1.
                reward_rgb=reference;reward_gray=reference_gray;reward_layout='native';quality_point=point
        # Roblox scales this tiny x1 badge differently in compact clients.
        # Search several aspect-preserving scales; the old single resize used
        # separate X/Y factors and could blur or distort the text into scores
        # around .7 even when the badge was visible.
        if not reward:
            th,tw=self.templates['reward'].shape
            rx,ry=w/1920,h/1080
            # Prefer the scales implied by the client geometry instead of an
            # exhaustive sweep. These cover the width, height, and both
            # blended estimates used by Roblox UI scaling.
            scales={round(float(s),3) for s in (rx,ry,(rx*ry)**.5,(rx+ry)/2)}
            search=(round(.25*w),round(.15*h),round(.75*w),round(.85*h))
            for scale in sorted(scales):
                size=(max(1,round(tw*scale)),max(1,round(th*scale)))
                if min(size)<5 or size[0]>search[2]-search[0] or size[1]>search[3]-search[1]:continue
                interpolation=cv2.INTER_AREA if scale<1 else cv2.INTER_CUBIC
                scaled_template=cv2.resize(self.templates['reward'],size,interpolation=interpolation)
                found,point,score=self.match(native_gray,scaled_template,search,.91)
                if score>candidate_score:
                    candidate_point=(point[0]*1920/w,point[1]*1080/h)
                    candidate_score=score;candidate_scale=scale;candidate_rgb=rgb
                if found and (not reward or score>reward_score):
                    reward=True;reward_score=score;reward_scale=scale
                    reward_point=(point[0]*1920/w,point[1]*1080/h)
                    reward_rgb=rgb;reward_gray=native_gray;reward_template=scaled_template
                    reward_layout='scaled';scale_x=scale*1920/w;scale_y=scale*1080/h;quality_point=point
                    # A near-perfect correlation is already decisive; avoid
                    # scanning the remaining scales on ordinary catches.
                    if score>=.985:break
        else:
            candidate_point=reward_point;candidate_score=reward_score;candidate_scale=reward_scale
        # Other fishing indicators keep their established proportional search.
        gray=cv2.resize(native_gray,(1920,1080),interpolation=cv2.INTER_LINEAR)
        fishing,_,exit_score=self.match(gray,self.templates['exit'],(760,950,1170,1080),.83)
        icon_point=reward_point if reward else None
        quality=(self.reward_quality(reward_gray,quality_point,reward_template,reward_scale)
                 if reward else 0.)
        reward_data={'reward':reward,'reward_point':icon_point,
                     'reward_candidate_point':candidate_point if candidate_score>=.65 else None,
                     'reward_candidate_score':candidate_score,
                     'reward_candidate_scale':candidate_scale,
                     'reward_icon':reward_icon(reward_rgb,reward_point,scale_x,scale_y) if reward else None,
                     'reward_crop':RewardReader.crop(reward_rgb,reward_point) if reward else None,
                     'reward_crop_candidate':RewardReader.crop(candidate_rgb,candidate_point)
                         if not reward and candidate_point is not None and candidate_score>=.70 else None,
                     'reward_score':reward_score if reward else candidate_score,
                     'reward_scale':reward_scale if reward else candidate_scale,
                     'reward_layout':reward_layout,
                     'reward_quality':quality}
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

    def reward_quality(self,gray,point,template=None,scale=1.):
        """Contrast of the matched notification text estimates its fade opacity.

        Template correlation alone is insensitive to fade-in/fade-out.
        Compare the same text, not the item artwork (which may be dark).
        """
        template=self.templates['reward'] if template is None else template;h,w=template.shape
        x=round(point[0]-w/2);y=round(point[1]-h/2)
        patch=gray[y:y+h,x:x+w]
        if patch.shape!=template.shape:return 0.
        bright=template>=np.percentile(template,85);dark=template<=np.percentile(template,25)
        reference=float(np.median(template[bright]))-float(np.median(template[dark]))
        contrast=float(np.median(patch[bright]))-float(np.median(patch[dark]))
        opacity=max(0.,min(1.,contrast/max(1.,reference)))
        left=round(point[0]-99.5*scale);top=round(point[1]-42.5*scale)
        ih=max(2,round(48*scale));iw=max(2,round(44*scale))
        icon=gray[max(0,top):top+ih,max(0,left):left+iw].astype(np.float32)
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

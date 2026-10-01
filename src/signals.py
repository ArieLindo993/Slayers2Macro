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
        self.collect_sources=[self.templates[n] for n in ('collect','collect_small','collect_small2','collect_medium','collect_user')]
        for scale in (.75,.85,1.,1.15,1.3,1.5):
            self.collect_templates.append(cv2.resize(self.templates['collect_user'],None,fx=scale,fy=scale))

    @staticmethod
    def resolution_scales(w,h):
        """Aspect-preserving UI scales suggested by the Roblox client size."""
        rx,ry=w/1920,h/1080
        return sorted({round(float(scale),3) for scale in (rx,ry,(rx*ry)**.5,(rx+ry)/2,1.)
                       if .28<=scale<=1.5})

    def match_scaled(self,gray,name,box,threshold,scales=None):
        source=self.templates[name];source_h,source_w=source.shape
        best=(False,None,0.,None,None)
        for scale in self.resolution_scales(gray.shape[1],gray.shape[0]) if scales is None else scales:
            size=(max(1,round(source_w*scale)),max(1,round(source_h*scale)))
            if min(size)<5 or size[0]>box[2]-box[0] or size[1]>box[3]-box[1]:continue
            method=cv2.INTER_AREA if scale<1 else cv2.INTER_CUBIC
            template=cv2.resize(source,size,interpolation=method)
            found,point,score=self.match(gray,template,box,threshold)
            if score>best[2]:best=(found,point,score,template,scale)
            if found and score>=.985:break
        return best

    def exit_indicator(self,gray):
        h,w=gray.shape[:2]
        box=(max(0,round(760*w/1920)),max(0,round(950*h/1080)),
             min(w,round(1170*w/1920)),h)
        return self.match_scaled(gray,'exit',box,.83)

    def scan(self,rgb,fishing_only=False):
        cv2.setNumThreads(2)
        h,w=rgb.shape[:2]
        native_gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
        # Prefer the original template, but keep its best location even when
        # it is too weak to confirm. The OCR can use that location as an anchor.
        reward=False;reward_point=None;reward_score=0.;reward_scale=1.
        candidate_point=None;candidate_score=0.;candidate_scale=None
        quality_point=None;icon_point=None
        reward_rgb=rgb;reward_gray=native_gray;reward_template=self.templates['reward']
        reward_layout='scaled';scale_x=scale_y=1.
        compact_client=(w,h)!=(1920,1080) and w<=1920 and h<=1080
        ocr_source=rgb
        if compact_client:
            ocr_source=np.zeros((1080,1920,3),dtype=rgb.dtype)
            left=(1920-w)//2;top=(1080-h)//2
            ocr_source[top:top+h,left:left+w]=rgb
        def ocr_position(point):
            if compact_client:return ((1920-w)//2+point[0],(1080-h)//2+point[1])
            return (point[0]*1920/w,point[1]*1080/h)
        if (w,h)!=(1920,1080) and w<=1920 and h<=1080:
            reference=ocr_source
            reference_gray=cv2.cvtColor(reference,cv2.COLOR_RGB2GRAY)
            # The compact client can move the notice above its fullscreen
            # anchor. The search now covers the central game area vertically.
            found,point,score=self.match(reference_gray,self.templates['reward'],(600,300,1400,850),.91)
            candidate_point=point;candidate_score=score;candidate_scale=1.
            if found:
                reward=True;reward_point=point;icon_point=point;reward_score=score;reward_scale=1.
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
            scales=set(self.resolution_scales(w,h))
            search=(round(.25*w),round(.15*h),round(.75*w),round(.85*h))
            for scale in sorted(scales):
                size=(max(1,round(tw*scale)),max(1,round(th*scale)))
                if min(size)<5 or size[0]>search[2]-search[0] or size[1]>search[3]-search[1]:continue
                interpolation=cv2.INTER_AREA if scale<1 else cv2.INTER_CUBIC
                scaled_template=cv2.resize(self.templates['reward'],size,interpolation=interpolation)
                found,point,score=self.match(native_gray,scaled_template,search,.91)
                if score>candidate_score:
                    candidate_point=ocr_position(point)
                    candidate_score=score;candidate_scale=scale
                if found and (not reward or score>reward_score):
                    reward=True;reward_score=score;reward_scale=scale
                    reward_point=ocr_position(point)
                    icon_point=(point[0]*1920/w,point[1]*1080/h)
                    reward_rgb=rgb;reward_gray=native_gray;reward_template=scaled_template
                    reward_layout='scaled';scale_x=scale*1920/w;scale_y=scale*1080/h;quality_point=point
                    # A near-perfect correlation is already decisive; avoid
                    # scanning the remaining scales on ordinary catches.
                    if score>=.985:break
        else:
            candidate_point=reward_point;candidate_score=reward_score;candidate_scale=reward_scale
        # Other fishing indicators keep their established proportional search.
        gray=cv2.resize(native_gray,(1920,1080),interpolation=cv2.INTER_LINEAR)
        fishing,_,exit_score,_,_=self.exit_indicator(native_gray)
        if not fishing:
            fishing,_,legacy_score=self.match(gray,self.templates['exit'],(760,950,1170,1080),.83)
            exit_score=max(exit_score,legacy_score)
        quality=(self.reward_quality(reward_gray,quality_point,reward_template,reward_scale)
                 if reward else 0.)
        reward_data={'reward':reward,'reward_point':reward_point,
                     'reward_candidate_point':candidate_point if candidate_score>=.50 else None,
                     'reward_candidate_score':candidate_score,
                     'reward_candidate_scale':candidate_scale,
                     'reward_icon':reward_icon(reward_rgb,icon_point,scale_x,scale_y) if reward else None,
                     'reward_crop':RewardReader.crop(ocr_source,reward_point) if reward else None,
                     'reward_crop_candidate':RewardReader.crop(ocr_source,candidate_point)
                         if not reward and candidate_point is not None and candidate_score>=.50 else None,
                     'reward_crop_fallback':RewardReader.fallback_crop(rgb) if compact_client else None,
                     'reward_score':reward_score if reward else candidate_score,
                     'reward_scale':reward_scale if reward else candidate_scale,
                     'reward_layout':reward_layout,
                     'reward_quality':quality}
        # Com a barra sendo controlada, o indicador independente basta.
        # Se ele sumir, procure coleta/recompensa já nesta mesma captura.
        if fishing_only and fishing:
            return {'fishing':True,'loot':None,'collect_score':0.,'exit_score':exit_score,**reward_data}
        # The collection prompt shrinks with the game UI. Match templates at
        # resolution-relative sizes on the un-stretched client image so small
        # prompts do not become oversized or distorted before comparison.
        native_results=[]
        for scale in self.resolution_scales(w,h):
            for source in self.collect_sources:
                sh,sw=source.shape;size=(max(1,round(sw*scale)),max(1,round(sh*scale)))
                if min(size)<5 or size[0]>w or size[1]>h:continue
                method=cv2.INTER_AREA if scale<1 else cv2.INTER_CUBIC
                template=cv2.resize(source,size,interpolation=method)
                native_results.append(self.match(native_gray,template,(0,0,w,h),.80))
        found=False;point=(0.,0.);score=0.
        if native_results:
            found,point,score=max(native_results,key=lambda result:result[2])
            if found:point=(point[0]*1920/w,point[1]*1080/h)
        if not found:
            results=[self.match(gray,template,(0,0,1920,1080),.80) for template in self.collect_templates]
            found,legacy_point,legacy_score=max(results,key=lambda result:result[2])
            if found:point=legacy_point;score=legacy_score
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
        gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
        fishing,_,_,_,_=self.exit_indicator(gray)
        if not fishing:
            full=cv2.resize(gray,(1920,1080))
            fishing,_,_=self.match(full,self.templates['exit'],(760,950,1170,1080),.83)
        return {'fishing':fishing,'candidate':search_bar(rgb,preferred,stage) if fishing else None}

    @staticmethod
    def match(gray,template,box,threshold):
        x,y,x2,y2=box
        area=gray[y:y2,x:x2]
        scores=cv2.matchTemplate(area,template,cv2.TM_CCOEFF_NORMED)
        _,score,_,loc=cv2.minMaxLoc(scores)
        th,tw=template.shape
        return score>=threshold,(x+loc[0]+tw/2,y+loc[1]+th/2),float(score)

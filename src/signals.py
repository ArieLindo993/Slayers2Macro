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
        gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
        # Escala de referência do vídeo, mantendo as coordenadas proporcionais.
        gray=cv2.resize(gray,(1920,1080),interpolation=cv2.INTER_LINEAR)
        fishing,_,exit_score=self.match(gray,self.templates['exit'],(760,950,1170,1080),.83)
        reward,reward_point,reward_score=self.match(gray,self.templates['reward'],(820,490,1230,740),.91)
        reward_data={'reward':reward,'reward_point':reward_point if reward else None,
                     'reward_icon':reward_icon(rgb,reward_point) if reward else None,
                     'reward_crop':RewardReader.crop(rgb,reward_point) if reward else None,
                     'reward_score':reward_score,
                     'reward_quality':self.reward_quality(gray,reward_point) if reward else 0.}
        # Com a barra sendo controlada, o indicador independente basta.
        # Se ele sumir, procure coleta/recompensa já nesta mesma captura.
        if fishing_only and fishing:
            return {'fishing':True,'loot':None,'collect_score':0.,'exit_score':exit_score,**reward_data}
        results=[]
        for template in self.collect_templates:
            results.append(self.match(gray,template,(0,0,1920,1080),.80))
        found,point,score=max(results,key=lambda r:r[2])
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

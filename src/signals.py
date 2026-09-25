"""Sinais visuais da gravação; não lê memória do Roblox."""
from pathlib import Path
import cv2
import numpy as np


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
        h,w=rgb.shape[:2]
        gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
        # Escala de referência do vídeo, mantendo as coordenadas proporcionais.
        gray=cv2.resize(gray,(1920,1080),interpolation=cv2.INTER_LINEAR)
        fishing,_,exit_score=self.match(gray,self.templates['exit'],(760,950,1170,1080),.83)
        results=[]
        for template in self.collect_templates:
            results.append(self.match(gray,template,(0,0,1920,1080),.80))
        found,point,score=max(results,key=lambda r:r[2])
        reward,reward_point,reward_score=self.match(gray,self.templates['reward'],(820,490,1230,740),.91)
        return {'fishing':fishing,'loot':(point[0]/1920,point[1]/1080) if found else None,
                'reward':reward,'reward_point':reward_point if reward else None,
                'collect_score':score,'exit_score':exit_score,'reward_score':reward_score}

    @staticmethod
    def match(gray,template,box,threshold):
        x,y,x2,y2=box
        area=gray[y:y2,x:x2]
        scores=cv2.matchTemplate(area,template,cv2.TM_CCOEFF_NORMED)
        _,score,_,loc=cv2.minMaxLoc(scores)
        th,tw=template.shape
        return score>=threshold,(x+loc[0]+tw/2,y+loc[1]+th/2),float(score)

"""Miniatura do aviso de recompensa; nenhum download ou captura inteira salva."""
import base64
import io
from PIL import Image

ICON_SIZE=(44,48)
MAX_ICONS=256

class IconSampler:
    """Bounded per-round sampling; don't save the first animation frame."""
    def __init__(self):self.samples={}
    def observe(self,cycle,stamp,encoded,quality):
        if not encoded:return None
        previous=self.samples.get(cycle)
        if previous and stamp<=previous['last']:return None
        if previous is None or stamp-previous['last']>3:
            previous={'first':stamp,'last':stamp,'count':0,'best':None,'quality':-1.}
            self.samples[cycle]=previous
        previous['last']=stamp;previous['count']+=1
        if quality>previous['quality']:previous.update(best=encoded,quality=quality)
        if previous['count']>=2 and stamp-previous['first']>=.2 and previous['quality']>=.7:
            return previous['best'],previous['quality']
        return None
    def prune(self,cycle):self.samples={k:v for k,v in self.samples.items() if k>=cycle-1}

def reward_icon(rgb,point):
    if point is None:return None
    # Coordenadas relativas ao indicador x1, na mesma escala do detector.
    x,y=point;left=round(x-99.5);top=round(y-42.5)
    if left<0 or top<0 or left+44>1920 or top+48>1080:return None
    image=Image.fromarray(rgb).resize((1920,1080),Image.Resampling.BILINEAR)
    crop=image.crop((left,top,left+44,top+48))
    stream=io.BytesIO();crop.save(stream,format='PNG')
    return base64.b64encode(stream.getvalue()).decode('ascii')

def decode_icon(encoded):
    if not isinstance(encoded,str) or len(encoded)>16384:return None
    try:
        raw=base64.b64decode(encoded,validate=True)
        with Image.open(io.BytesIO(raw)) as image:
            if image.format!='PNG' or image.size!=ICON_SIZE:return None
            return image.convert('RGB')
    except (ValueError,OSError):return None

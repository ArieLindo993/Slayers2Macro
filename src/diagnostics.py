"""Métricas e evidências locais limitadas à região da barra."""
import json,time
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
from product import VERSION

class RuntimeJournal:
    """Estado de execução persistente, sem imagens, caminhos ou mensagens livres."""
    events_allowed={'startup','started','closed','internal_error','focus_lost','fishing_timeout','cast_unconfirmed','user_pause','previous_session_incomplete'}
    states_allowed={'INICIO','POSICIONANDO','CLIQUE','ESPERANDO','PESCANDO','RESULTADO','MIRANDO_ITEM','TECLA_T','VERIFICANDO_COLETA','REINICIANDO','PARADO'}

    def __init__(self,path):
        self.path=Path(path);self.events=[];self.snapshot={}
        try:
            old=json.loads(self.path.read_text('utf-8'))
            self.events=[{k:v for k,v in row.items() if k in ('time','event','state','version')}
                         for row in old.get('events',[]) if isinstance(row,dict) and row.get('event') in self.events_allowed][-199:]
            if old.get('snapshot',{}).get('active'):
                self.record('previous_session_incomplete',old['snapshot'].get('state','PARADO'))
        except (OSError,ValueError,TypeError,AttributeError):pass

    def write(self):
        try:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            temp=self.path.with_suffix('.tmp')
            temp.write_text(json.dumps({'events':self.events,'snapshot':self.snapshot},indent=2),encoding='utf-8')
            temp.replace(self.path)
            return True
        except OSError:return False

    def checkpoint(self,state,active,cycles,scene_age=0):
        self.snapshot={'time':datetime.now(timezone.utc).isoformat(),'version':VERSION,
                       'state':state if state in self.states_allowed else 'PARADO',
                       'active':bool(active),'cycles':max(0,int(cycles)),
                       'scene_age_seconds':round(max(0,min(9999,scene_age)),2)}
        return self.write()

    def record(self,event,state,active=False,cycles=0):
        if event not in self.events_allowed:return False
        self.events.append({'time':datetime.now(timezone.utc).isoformat(),'version':VERSION,
                            'event':event,'state':state if state in self.states_allowed else 'PARADO'})
        self.events=self.events[-200:]
        return self.checkpoint(state,active,cycles)

class TrackingMetrics:
    def __init__(self):self.reset()
    def reset(self):
        self.last=None;self.total=0.;self.valid=0.;self.inside=0.;self.last_reading=None
    def observe(self,reading,now):
        if self.last is not None:
            dt=max(0,min(.1,now-self.last));self.total+=dt
            if self.last_reading is not None:
                self.valid+=dt
                if abs(self.last_reading.marker-self.last_reading.target)<=self.last_reading.band/2:self.inside+=dt
        self.last=now;self.last_reading=reading
    def pause(self):self.last=None;self.last_reading=None
    def summary(self):
        return {'observed_seconds':round(self.total,2),
                'valid_percent':round(100*self.valid/self.total,1) if self.total else 0.,
                'inside_percent':round(100*self.inside/self.valid,1) if self.valid else None}

def annotated_preview(rgb,reading):
    im=Image.fromarray(rgb).convert('RGB');im.thumbnail((160,200))
    draw=ImageDraw.Draw(im);w,h=im.size
    draw.rectangle((0,0,w-1,h-1),outline='#20b8ed',width=2)
    if reading:
        y0=int((reading.target-reading.band/2)*h);y1=int((reading.target+reading.band/2)*h)
        draw.rectangle((2,max(1,y0),w-3,min(h-2,y1)),outline='#12ed8c',width=2)
        y=max(0,min(h-1,int(reading.marker*h)))
        draw.line((0,y,w-1,y),fill='#ff66d2',width=2)
    return im

class Diagnostics:
    def __init__(self,directory,limit=20):
        self.directory=Path(directory);self.limit=limit;self.last=-float('inf')
    def save(self,rgb,state,stage,metrics,now=None):
        now=time.monotonic() if now is None else now
        if now-self.last<10:return False
        self.last=now;self.directory.mkdir(parents=True,exist_ok=True)
        # Apenas o recorte recebido da barra, nunca a área de trabalho ou a janela inteira.
        im=Image.fromarray(rgb).convert('RGB');im.thumbnail((256,600))
        stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
        im.save(self.directory/(stamp+'.png'))
        safe_state=state if state in ('PESCANDO','RESULTADO','PARADO') else 'OTHER'
        safe_stage=stage if stage in ('current','nearby','screen') else 'current'
        data={'version':VERSION,'event':'tracking_lost','state':safe_state,'search_stage':safe_stage,
              'observed_seconds':metrics['observed_seconds'],'valid_percent':metrics['valid_percent'],
              'inside_percent':metrics['inside_percent']}
        (self.directory/(stamp+'.json')).write_text(json.dumps(data,indent=2),encoding='utf-8')
        for old in sorted(self.directory.glob('*.json'))[:-self.limit]:
            old.unlink();old.with_suffix('.png').unlink(missing_ok=True)
        return True

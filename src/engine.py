"""Sequência verificável de pesca. As ações são executadas pela interface."""
from detector import Controller


class Engine:
    def __init__(self, config):
        self.cfg=config
        self.control=Controller()
        self.reset(0)

    def reset(self,now,preserve_counts=False):
        counts=(getattr(self,'cycles',0),getattr(self,'collected',0),getattr(self,'unconfirmed',0))
        self.state='INICIO';self.deadline=now+1
        self.message='Conferindo a tela…'
        self.attempts=0;self.collect_attempts=0
        self.cycles=0;self.collected=0;self.unconfirmed=0
        if preserve_counts:self.cycles,self.collected,self.unconfirmed=counts
        self.loot_seen=False;self.absent_since=None
        self.collect_started=None;self.reward_was_present=False
        self.last_fishing=now;self.track_started=now
        self.last_marker=now;self.positive=0
        self.last_loot=None;self.outcome=None
        self.control.reset()

    def stop(self,message):
        self.state='PARADO';self.message=message
        return [('mouse',False),('t',False),('stop',message)]

    def cast(self,now):
        self.attempts+=1
        self.state='POSICIONANDO';self.deadline=now+.18
        self.message=f'Lançando a vara · tentativa {self.attempts}/{self.cfg["max_cast"]}'
        return [('mouse',False),('aim',self.cfg['cast'])]

    def track(self,now):
        self.state='PESCANDO';self.last_fishing=now;self.track_started=now;self.last_marker=now
        self.attempts=0;self.control.reset();self.message='Pesca confirmada. Acompanhando a barra.'
        return [('mouse',False),('t',False)]

    def prepare_collect(self,now,loot):
        if self.collect_started is None:self.collect_started=now
        self.collect_attempts+=1;self.loot_seen=self.loot_seen or bool(loot);self.absent_since=None
        self.state='MIRANDO_ITEM';self.deadline=now+.25
        if loot:self.last_loot=loot
        self.message=f'Tentativa de coleta {self.collect_attempts}/{self.cfg["max_collect"]}'
        return [('mouse',False)]+([('aim',self.last_loot)] if self.last_loot else [])

    def force_collect(self,now):
        """Coleta sem depender da detecção do texto/item na vara."""
        if self.collect_started is None:self.collect_started=now
        self.collect_attempts+=1
        self.loot_seen=True
        self.state='TECLA_T';self.deadline=now+self.cfg['t_hold']
        self.message=f'Coletando com T · tentativa {self.collect_attempts}/{self.cfg["max_collect"]}'
        return [('mouse',False),('t',True)]

    def finish(self,now,confirmed):
        self.outcome='Coleta confirmada' if confirmed else ('Coleta não confirmada' if self.loot_seen else 'Sem recompensa detectada')
        self.cycles+=1
        if confirmed:self.collected+=1
        else:self.unconfirmed+=1
        self.state='REINICIANDO';self.deadline=now+self.cfg['recast_seconds']
        self.message=self.outcome+'. Próxima pesca…'
        self.attempts=0;self.collect_attempts=0
        self.collect_started=None
        return [('mouse',False),('t',False)]

    def step(self,now,reading,fishing,loot,reward=False):
        if self.state=='PARADO':return []
        reward_new=reward and not self.reward_was_present
        self.reward_was_present=reward
        # O botão Collect pode aparecer enquanto o marcador ainda está visível.
        # Nesse caso a coleta tem prioridade para não deixar o item girando na vara.
        if loot:self.last_loot=loot
        if loot and not (reading is not None and fishing) and self.state in ('PESCANDO','RESULTADO','ESPERANDO','POSICIONANDO'):
            self.collect_attempts=0 if self.state=='PESCANDO' else self.collect_attempts
            return self.prepare_collect(now,loot)
        if self.state=='RESULTADO' and reward_new:return self.finish(now,True)
        if self.state in ('TECLA_T','VERIFICANDO_COLETA','MIRANDO_ITEM'):
            if reward_new and self.collect_attempts>0:return self.finish(now,True)
            if self.collect_started is not None and now-self.collect_started>self.cfg['collect_timeout']:
                return self.finish(now,False)
        active=fishing or reading is not None
        self.positive=self.positive+1 if active else 0
        if self.state in ('RESULTADO','MIRANDO_ITEM','TECLA_T','VERIFICANDO_COLETA') and reading is not None and fishing and self.positive>=2:
            self.collect_attempts=0;self.collect_started=None
            return self.track(now)
        # Um minigame reaparecendo tem prioridade sobre coleta e novos cliques.
        if self.state in ('POSICIONANDO','CLIQUE','ESPERANDO') and self.positive>=2:
            return self.track(now)
        if self.state=='INICIO':
            if self.positive>=2:return self.track(now)
            if loot:
                self.collect_attempts=0
                return self.prepare_collect(now,loot)
            if now>=self.deadline and not active:return self.cast(now)
        elif self.state=='POSICIONANDO':
            if loot:return self.prepare_collect(now,loot)
            if active:return []
            if now>=self.deadline:
                self.state='CLIQUE';self.deadline=now+self.cfg['cast_hold']
                return [('mouse',True)]
        elif self.state=='CLIQUE':
            if now>=self.deadline:
                self.state='ESPERANDO';self.deadline=now+self.cfg['wait_seconds']
                self.message='Aguardando confirmação da pesca…'
                return [('mouse',False)]
        elif self.state=='ESPERANDO':
            if loot:return self.prepare_collect(now,loot)
            if now>=self.deadline and not active:
                if self.attempts>=self.cfg['max_cast']:
                    return self.stop('Pesca não confirmada após 3 lançamentos. Confira vara e ponto na água.')
                return self.cast(now)
        elif self.state=='PESCANDO':
            if active:self.last_fishing=now
            if now-self.track_started>120:return self.stop('Pesca excedeu 120 segundos. Confira a tela.')
            if reading:
                self.last_marker=now
                self.message='Pesca confirmada. Acompanhando a barra.'
                return [('mouse',self.control.step(reading,now,self.cfg['anticipation']))]
            # Uma falha curta não deve derrubar o marcador nem apagar sua velocidade.
            if now-self.last_marker<.15:return []
            self.control.reset()
            if now-self.last_fishing>(3 if self.cfg.get('auto_calibrate') else 1):
                self.state='RESULTADO';self.deadline=now+self.cfg['result_wait']
                self.collect_attempts=0;self.loot_seen=False;self.absent_since=None;self.collect_started=None
                self.message='Verificando se há item para coletar…'
            elif now-self.last_marker>(20 if self.cfg.get('auto_calibrate') else 6):
                return self.stop('Não consegui recuperar a barra. Use F6 para selecionar e F4 para retomar.')
            else:
                self.message='Reencontrando a barra…' if self.cfg.get('auto_calibrate') else 'Aguardando leitura da barra…'
            if now-self.track_started>120:return self.stop('Pesca excedeu 120 segundos. Confira a tela.')
            return [('mouse',False)]
        elif self.state=='RESULTADO':
            if loot:return self.prepare_collect(now,loot)
            if now>=self.deadline:
                # Tentativa de recuperação mesmo se o prompt não for reconhecido.
                return self.prepare_collect(now,None)
        elif self.state=='MIRANDO_ITEM':
            if now>=self.deadline:
                self.state='TECLA_T';self.deadline=now+self.cfg['t_hold']
                return ([('aim',loot)] if loot else [])+[('t',True)]
        elif self.state=='TECLA_T':
            if now>=self.deadline:
                self.state='VERIFICANDO_COLETA';self.deadline=now+1.2;self.absent_since=None
                self.message='Aguardando confirmação da recompensa…'
                return [('t',False)]
        elif self.state=='VERIFICANDO_COLETA':
            if now>=self.deadline:
                if self.collect_attempts>=self.cfg['max_collect']:return self.finish(now,False)
                return self.prepare_collect(now,loot)
            self.message='Aguardando recompensa; ausência do painel não confirma coleta.'
        elif self.state=='REINICIANDO':
            if now>=self.deadline:
                self.last_loot=None;self.loot_seen=False
                return self.cast(now)
        return []

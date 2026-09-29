"""Sequência verificável de pesca. As ações são executadas pela interface."""
from detector import Controller


# Evidências independentes podem atravessar uma curta espera pelo processamento,
# mas nunca uma interrupção longa nem capturas anteriores à recuperação.
OBSERVATION_GAP = 3.0


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
        self.absent_frames=0;self.last_collect_frame=None
        self.collect_started=None;self.reward_was_present=False
        self.reward_pending=False
        self.last_fishing=now;self.track_started=now
        self.last_marker=now;self.positive=0
        self.positive_time=None;self.signal_stamp=None;self.reading_stamp=None
        self.last_loot=None;self.outcome=None
        self.recovery_count=0;self.recovery_frames=0;self.recovery_stamp=None
        self.recovery_received=None
        self.recovery_started=now;self.recovery_requires_marker=False;self.recovery_reason=None
        self.control.reset()

    def stop(self,message):
        self.state='PARADO';self.message=message
        return [('mouse',False),('t',False),('stop',message)]

    def cast(self,now):
        self.reward_pending=False
        self.attempts+=1
        self.state='POSICIONANDO';self.deadline=now+.18
        self.message=f'Lançando a vara · tentativa {self.attempts}/{self.cfg["max_cast"]}'
        return [('mouse',False),('aim',self.cfg['cast'])]

    def track(self,now):
        self.state='PESCANDO';self.last_fishing=now;self.track_started=now;self.last_marker=now
        self.attempts=0;self.control.reset();self.message='Pesca confirmada. Acompanhando a barra.'
        self.recovery_count=0
        return [('mouse',False),('t',False)]

    def recover(self,now,reason='cast_unconfirmed',require_marker=False):
        self.recovery_count+=1
        delay=min(60,15*self.recovery_count)
        self.state='RECUPERANDO';self.deadline=now+delay
        self.recovery_frames=0;self.recovery_stamp=None
        self.recovery_received=None
        self.recovery_started=now;self.recovery_requires_marker=require_marker or reason=='tracking_lost';self.recovery_reason=reason
        self.positive=0;self.positive_time=None
        # O watchdog também pode interromper uma coleta; seu prazo anterior
        # não pode vencer imediatamente quando um novo item reaparece.
        self.collect_started=None;self.collect_attempts=0
        self.absent_since=None;self.absent_frames=0;self.last_collect_frame=None
        self.last_loot=None;self.loot_seen=False
        self.control.reset()
        explanation={'cast_unconfirmed':'Lançamento não confirmado',
                     'tracking_lost':'Marcador não reencontrado por 120 segundos',
                     'vision_unavailable':'Aguardando a recuperação das leituras da tela'}.get(reason,'Conferindo o estado da pesca')
        self.message=f'{explanation}. Conferindo a tela; nova tentativa em {delay}s.'
        return [('mouse',False),('t',False),('recover',self.recovery_count)]

    def observe_activity(self,now,reading,fishing,stamp,scene_valid):
        """Conta capturas de cena, não os ticks que reutilizam seu resultado."""
        usable=scene_valid and 0<=now-stamp<=OBSERVATION_GAP
        usable=usable and (self.signal_stamp is None or stamp>=self.signal_stamp)
        if self.state=='RECUPERANDO':usable=usable and stamp>=self.recovery_started
        new_scene=usable and (self.signal_stamp is None or stamp>self.signal_stamp)
        if new_scene and self.signal_stamp is not None and stamp-self.signal_stamp>OBSERVATION_GAP:
            self.positive=0;self.positive_time=None
        if new_scene:self.signal_stamp=stamp
        fishing=bool(fishing and usable)
        # Após o timeout, o indicador isolado já falhou em confirmar o marcador.
        # Ele não pode reiniciar o mesmo estado indefinidamente.
        marker_required=self.state=='RECUPERANDO' and self.recovery_requires_marker
        if self.positive_time is not None and now-self.positive_time>OBSERVATION_GAP:
            self.positive=0;self.positive_time=None
        if reading is not None:
            if self.reading_stamp is None or now>self.reading_stamp:
                self.positive+=1;self.positive_time=now;self.reading_stamp=now
        elif new_scene:
            if fishing and not marker_required:
                # Expiration between deliveries uses arrival time. Subtracting
                # a capture timestamp from arrival time counts analysis delay
                # twice and can permanently reject two otherwise valid frames.
                self.positive+=1;self.positive_time=now
            else:self.positive=0;self.positive_time=None
        elif usable and not fishing:
            self.positive=0;self.positive_time=None
        return fishing,usable,new_scene

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
        self.state='TECLA_T';self.deadline=now+self.cfg['t_hold']
        self.message=f'Coletando com T · tentativa {self.collect_attempts}/{self.cfg["max_collect"]}'
        return [('mouse',False),('t',True)]

    def finish(self,now,confirmed,reason=None):
        self.reward_pending=False
        self.outcome=reason or ('Coleta confirmada' if confirmed else ('Coleta não confirmada' if self.loot_seen else 'Sem recompensa detectada'))
        self.cycles+=1
        if confirmed:self.collected+=1
        else:self.unconfirmed+=1
        self.state='REINICIANDO';self.deadline=now+self.cfg['recast_seconds']
        self.message=self.outcome+'. Próxima pesca…'
        self.attempts=0;self.collect_attempts=0
        self.collect_started=None
        return [('mouse',False),('t',False)]

    def step(self,now,reading,fishing,loot,reward=False,scene_stamp=None,scene_valid=True):
        if self.state=='PARADO':return []
        stamp=now if scene_stamp is None else scene_stamp
        fishing,scene_usable,new_scene=self.observe_activity(now,reading,fishing,stamp,scene_valid)
        if not scene_usable:loot=None
        reward_new=reward and not self.reward_was_present
        if reward:self.reward_was_present=True
        elif scene_usable and new_scene:self.reward_was_present=False
        # Direct inventory rewards may arrive before RESULTADO or before the
        # minigame's last frame disappears. Keep the event for this round only.
        reward_states=('PESCANDO','RESULTADO','CLIQUE','ESPERANDO','TECLA_T','VERIFICANDO_COLETA','MIRANDO_ITEM')
        if reward_new and self.state in reward_states:self.reward_pending=True
        if self.reward_pending and self.state in reward_states and not (fishing or reading is not None):
            return self.finish(now,True)
        # O botão Collect pode aparecer enquanto o marcador ainda está visível.
        # Nesse caso a coleta tem prioridade para não deixar o item girando na vara.
        if loot:self.last_loot=loot
        if loot and not (reading is not None and fishing) and self.state in ('PESCANDO','RESULTADO','ESPERANDO','POSICIONANDO'):
            self.collect_attempts=0 if self.state=='PESCANDO' else self.collect_attempts
            return self.prepare_collect(now,loot)
        if self.state in ('TECLA_T','VERIFICANDO_COLETA','MIRANDO_ITEM'):
            if loot:self.loot_seen=True
            if self.collect_started is not None and now-self.collect_started>self.cfg['collect_timeout']:
                return self.finish(now,False)
        active=fishing or reading is not None
        if self.state=='RECUPERANDO':
            recovering_activity=reading is not None or (fishing and not self.recovery_requires_marker)
            if recovering_activity and self.positive>=2:return self.track(now)
            if loot and scene_usable:return self.prepare_collect(now,loot)
            if recovering_activity:
                self.recovery_frames=0;self.recovery_stamp=None;self.recovery_received=None
                return []
            expired=self.recovery_received is not None and now-self.recovery_received>OBSERVATION_GAP
            if new_scene and self.recovery_stamp is not None:
                expired=expired or stamp-self.recovery_stamp>OBSERVATION_GAP
            if expired:
                self.recovery_frames=0
            if not scene_usable or not new_scene:
                self.message='Recuperação: aguardando uma leitura recente da tela.'
                return [('mouse',False),('t',False)]
            self.recovery_frames+=1;self.recovery_stamp=stamp;self.recovery_received=now
            if now>=self.deadline and self.recovery_frames>=2:
                self.attempts=0
                return self.cast(now)
            return []
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
                    return self.recover(now)
                return self.cast(now)
        elif self.state=='PESCANDO':
            if active:self.last_fishing=now
            if reading:
                self.last_marker=now
                self.message='Pesca confirmada. Acompanhando a barra.'
                return [('mouse',self.control.step(reading,now,self.cfg['anticipation']))]
            # Uma falha curta não deve derrubar o marcador nem apagar sua velocidade.
            if now-self.last_marker<.15:return []
            self.control.reset()
            if now-self.last_marker>120:
                return self.recover(now,reason='tracking_lost')
            if now-self.last_fishing>(3 if self.cfg.get('auto_calibrate') else 1):
                self.state='RESULTADO';self.deadline=now+self.cfg['result_wait']
                self.collect_attempts=0;self.loot_seen=False;self.absent_since=None;self.collect_started=None
                self.message='Verificando se há item para coletar…'
            else:
                self.message='Reencontrando a barra…' if self.cfg.get('auto_calibrate') else 'Aguardando leitura da barra…'
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
                self.state='VERIFICANDO_COLETA';self.deadline=now+.6;self.absent_since=None
                self.absent_frames=0;self.last_collect_frame=None;self.verification_started=now
                self.message='Aguardando confirmação da recompensa…'
                return [('t',False)]
        elif self.state=='VERIFICANDO_COLETA':
            stamp=now if scene_stamp is None else scene_stamp
            if loot or active:
                self.absent_since=None;self.absent_frames=0
            elif scene_usable and stamp>=self.verification_started and (self.last_collect_frame is None or stamp>self.last_collect_frame):
                # Uma captura envelhecida enquanto a próxima está sendo
                # processada não é evidência de reaparecimento do item.
                # Reinicie só se houve uma lacuna longa entre capturas válidas.
                if self.last_collect_frame is not None and stamp-self.last_collect_frame>3:
                    self.absent_since=None;self.absent_frames=0
                self.last_collect_frame=stamp
                if self.absent_since is None:self.absent_since=stamp
                self.absent_frames+=1
                if self.absent_frames>=2 and stamp-self.absent_since>=.6:
                    if self.loot_seen:
                        return self.finish(now,False,'Item desapareceu após T; recompensa não confirmada')
                    if self.collect_attempts>=2:
                        return self.finish(now,False,'Nenhum item identificado em duas tentativas')
            if now>=self.deadline:
                # Capturas lentas precisam de tempo para formar observações
                # distintas; não gastar outra tentativa enquanto elas chegam.
                if not loot and not active:
                    stable=self.absent_since is not None and self.absent_frames>=2 and stamp-self.absent_since>=.6
                    if not scene_valid or not stable:
                        self.message='Conferindo novas capturas antes de decidir se repete a coleta…'
                        return []
                if self.collect_attempts>=self.cfg['max_collect']:return self.finish(now,False)
                return self.prepare_collect(now,loot)
            self.message='Conferindo recompensa e presença do item após T…'
        elif self.state=='REINICIANDO':
            if now>=self.deadline:
                self.last_loot=None;self.loot_seen=False
                return self.cast(now)
        return []

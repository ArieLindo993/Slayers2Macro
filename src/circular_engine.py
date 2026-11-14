"""November fishing flow. Timers never block capture, shortcuts or key release."""
from engine import Engine
from circular import CircularCommand,KeyPromptCommand


class CircularEngine(Engine):
    def reset(self,now,preserve_counts=False):
        super().reset(now,preserve_counts)
        self.mouse_command=CircularCommand();self.key_command=KeyPromptCommand()
        self.splash_armed_at=float('inf');self.claim_hold_completed=False
        self.confirmation_source=None

    def cast(self,now):
        self.mouse_command.reset();self.key_command.reset()
        self.claim_hold_completed=False
        return [('release_keys',True)]+super().cast(now)

    def recover(self,now,reason='cast_unconfirmed',require_marker=False):
        self.mouse_command.reset();self.key_command.reset()
        return [('release_keys',True)]+super().recover(now,reason,require_marker)

    def track(self,now):
        actions=super().track(now)
        self.mouse_command.reset();self.key_command.reset()
        self.message='Círculo localizado. Lendo mouse e A/D.'
        return actions

    def finish(self,now,confirmed,reason=None):
        # Claim disappearance is only collection evidence after a full hold,
        # multiple fresh frames and persistent absence, never just a name OCR.
        if (not confirmed and reason=='Item desapareceu após T; recompensa não confirmada'
            and self.claim_hold_completed):
            if self.absent_since is None or now-self.absent_since+1e-6<1.2:
                self.message='Conferindo recompensa e presença do item após T…'
                return []
            confirmed=True;reason='Coleta inferida após T e ausência estável do aviso Claim'
            self.confirmation_source='claim_after_hold'
        elif confirmed:self.confirmation_source='reward_notification'
        self.mouse_command.reset();self.key_command.reset()
        return [('release_keys',True)]+super().finish(now,confirmed,reason)

    def step(self,now,reading,fishing=False,loot=None,reward=False,
             scene_stamp=None,scene_valid=True,splash=False):
        if self.state=='PARADO':return []
        fresh=scene_valid and (scene_stamp is None or 0<=now-scene_stamp<.5)
        if not fresh:loot=None;reward=False
        active=reading is not None and not reading.complete
        if active:
            if reward:self.reward_pending=True
            actions=[]
            if self.state!='PESCANDO':actions+=self.track(now)
            self.last_fishing=now;self.last_marker=now
            self.message='Círculo ativo · '+('segurando mouse' if reading.hold is True else 'soltando mouse' if reading.hold is False else 'aguardando próximo aviso')
            actions.append(('mouse',self.mouse_command.step(reading,now)))
            actions.extend(('tap',key) for key in self.key_command.step(reading,now))
            return actions
        if self.state=='PESCANDO':
            mouse=self.mouse_command.step(None,now);self.key_command.step(None,now)
            if reading is not None or now-self.last_fishing>=.85:
                self.state='RESULTADO';self.deadline=now+self.cfg['result_wait']
                self.collect_attempts=0;self.collect_started=None;self.loot_seen=False
                self.message='Verificando se há item para coletar…'
                return [('mouse',False),('release_keys',True)]
            self.message='Reencontrando o círculo…'
            return [('mouse',mouse),('release_keys',True)]
        if self.state=='FISGANDO':
            if now>=self.deadline:
                self.state='AGUARDANDO_CIRCULO';self.deadline=now+4
                self.message='Splash clicado. Aguardando o círculo…'
                return [('mouse',False)]
            return []
        if self.state=='AGUARDANDO_CIRCULO':
            if splash:
                self.state='FISGANDO';self.deadline=now+.09
                return [('mouse',True)]
            if loot:return self.prepare_collect(now,loot)
            if now>=self.deadline:
                self.state='ESPERANDO';self.deadline=now+self.cfg['wait_seconds']
                self.splash_armed_at=now+.4
            return []
        if self.state=='ESPERANDO' and splash and now>=self.splash_armed_at:
            self.state='FISGANDO';self.deadline=now+.09
            self.message='Splash detectado. Fisgando…'
            return [('mouse',True)]
        previous=self.state
        actions=super().step(now,None,False,loot,reward,scene_stamp,scene_valid)
        if previous=='CLIQUE' and self.state=='ESPERANDO':
            self.splash_armed_at=now+.9
            self.message='Linha lançada. Aguardando o splash…'
        if previous=='TECLA_T' and self.state=='VERIFICANDO_COLETA':self.claim_hold_completed=True
        return actions

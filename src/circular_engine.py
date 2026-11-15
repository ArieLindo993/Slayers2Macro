"""November fishing flow. Timers never block capture, shortcuts or key release."""
from engine import Engine
from circular import CircularCommand,KeyPromptCommand


class CircularEngine(Engine):
    def reset(self,now,preserve_counts=False):
        super().reset(now,preserve_counts)
        self.mouse_command=CircularCommand();self.key_command=KeyPromptCommand()
        self.splash_armed_at=float('inf');self.claim_hold_completed=False
        self.confirmation_source=None
        self.cast_released_at=None;self.last_landing_activity=None
        self.splash_ready=True;self.hook_requested_at=None

    def cast(self,now):
        self.mouse_command.reset();self.key_command.reset()
        self.claim_hold_completed=False
        self.cast_released_at=None;self.last_landing_activity=None
        self.splash_ready=False;self.hook_requested_at=None
        return [('right_mouse',False),('release_keys',True)]+super().cast(now)

    @staticmethod
    def mouse_actions(button):
        # Release the opposite button first. Repeated readings do not require
        # releasing and pressing the selected button on every capture.
        if button=='right':return [('mouse',False),('right_mouse',True)]
        if button=='left':return [('right_mouse',False),('mouse',True)]
        return [('mouse',False),('right_mouse',False)]

    def stop(self,message):
        self.mouse_command.reset();self.key_command.reset()
        return [('right_mouse',False),('release_keys',True)]+super().stop(message)

    def prepare_collect(self,now,loot):
        return [('right_mouse',False)]+super().prepare_collect(now,loot)

    def prepare_hook(self,now):
        self.state='PREPARANDO_FISGADA';self.hook_requested_at=now
        self.deadline=now+self.cfg.get('splash_click_delay',.18)
        self.message='Splash confirmado. Aguardando o instante de fisgar…'
        return self.mouse_actions(None)

    def recover(self,now,reason='cast_unconfirmed',require_marker=False):
        self.mouse_command.reset();self.key_command.reset()
        return [('right_mouse',False),('release_keys',True)]+super().recover(now,reason,require_marker)

    def track(self,now):
        actions=super().track(now)
        self.mouse_command.reset();self.key_command.reset()
        self.message='Círculo localizado. Lendo mouse e A/D.'
        return [('right_mouse',False)]+actions

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
        return [('right_mouse',False),('release_keys',True)]+super().finish(now,confirmed,reason)

    def step(self,now,reading,fishing=False,loot=None,reward=False,
             scene_stamp=None,scene_valid=True,splash=False,impact_activity=False):
        if self.state=='PARADO':return []
        fresh=scene_valid and (scene_stamp is None or 0<=now-scene_stamp<.5)
        if not fresh:loot=None;reward=False
        active=reading is not None and not reading.complete
        if active:
            if reward:self.reward_pending=True
            actions=[]
            if self.state!='PESCANDO':actions+=self.track(now)
            self.last_fishing=now;self.last_marker=now
            mouse=self.mouse_command.step(reading,now)
            self.message='Círculo ativo · '+('segurando botão direito' if mouse=='right' else 'segurando botão esquerdo' if mouse=='left' else 'aliviando na borda verde' if self.mouse_command.reason=='green_edge' else 'botões do mouse soltos')
            actions+=self.mouse_actions(mouse)
            actions.extend(('tap',key) for key in self.key_command.step(reading,now))
            return actions
        if self.state=='PESCANDO':
            mouse=self.mouse_command.step(None,now);self.key_command.step(None,now)
            if reading is not None or now-self.last_fishing>=.85:
                self.state='RESULTADO';self.deadline=now+self.cfg['result_wait']
                self.collect_attempts=0;self.collect_started=None;self.loot_seen=False
                self.message='Verificando se há item para coletar…'
                return self.mouse_actions(None)+[('release_keys',True)]
            self.message='Reencontrando o círculo…'
            return self.mouse_actions(mouse)+[('release_keys',True)]
        if self.state=='ASSENTANDO_LINHA':
            if impact_activity:self.last_landing_activity=now
            quiet=self.last_landing_activity is None or now-self.last_landing_activity>=.30
            if now>=self.deadline and (quiet or now>=self.deadline+1.2):
                self.state='ESPERANDO';self.splash_armed_at=now
                self.splash_ready=quiet
                self.deadline=now+self.cfg['wait_seconds']
                self.message='Linha lançada. Aguardando o splash…' if quiet else 'Aguardando estabilização da água antes de fisgar…'
            return [('mouse',False)]
        if self.state=='PREPARANDO_FISGADA':
            if now>self.deadline+.25:
                self.state='ESPERANDO';self.splash_armed_at=now+.3
                self.splash_ready=False;self.last_landing_activity=now
                self.deadline=now+self.cfg['wait_seconds']
                self.message='Janela da fisgada passou. Aguardando novo splash…'
                return [('mouse',False)]
            if now>=self.deadline:
                self.state='FISGANDO';self.deadline=now+.09
                self.message='Fisgando após a confirmação do splash…'
                return [('mouse',True)]
            return []
        if self.state=='FISGANDO':
            if now>=self.deadline:
                self.state='AGUARDANDO_CIRCULO';self.deadline=now+4
                self.message='Splash clicado. Aguardando o círculo…'
                return [('mouse',False)]
            return []
        if self.state=='AGUARDANDO_CIRCULO':
            # One hook click, then wait for confirmation. Further particles
            # must not repeatedly reel the line before the circle can appear.
            if loot:return self.prepare_collect(now,loot)
            if now>=self.deadline:
                if self.attempts>=self.cfg['max_cast']:return self.recover(now)
                return self.cast(now)
            return []
        if self.state=='ESPERANDO':
            if not self.splash_ready:
                if impact_activity:self.last_landing_activity=now
                elif self.last_landing_activity is None or now-self.last_landing_activity>=.30:
                    self.splash_ready=True;self.message='Linha lançada. Aguardando o splash…'
            if splash and self.splash_ready and now>=self.splash_armed_at:return self.prepare_hook(now)
        previous=self.state
        actions=super().step(now,None,False,loot,reward,scene_stamp,scene_valid)
        if previous=='CLIQUE' and self.state=='ESPERANDO':
            # The first landing burst can arrive after the former 1.8 s guard.
            # Keep it disarmed through the configurable settling interval and
            # a short quiet gap. The upper bound prevents zone mist deadlocks.
            self.state='ASSENTANDO_LINHA';self.splash_armed_at=float('inf')
            self.cast_released_at=now;self.last_landing_activity=now
            self.splash_ready=False
            self.deadline=now+self.cfg.get('cast_settle_seconds',3.)
            self.message='Esperando a linha assentar…'
        if previous=='TECLA_T' and self.state=='VERIFICANDO_COLETA':self.claim_hold_completed=True
        return actions

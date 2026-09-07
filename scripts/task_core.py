"""Simulator-independent sequence for a known-target plant mechanics fixture."""
class WeedCycle:
    def __init__(self, now):
        self.phase='work';self.started=now;self.phase_at=now;self.sent=False;self.contact_since=None;self.result=None
    def abort(self,reason,now):
        self.result=dict(success=False,reason=reason,time_s=now-self.started);self.phase='aborted'
    def advance(self,phase,now):
        self.phase=phase;self.phase_at=now;self.sent=False;self.contact_since=None
    def update(self,now,arm_done,plant):
        if self.result:return None
        if now-self.phase_at>40:self.abort('step_timeout',now);return 'hold'
        if not plant.get('available'):self.abort('plant_missing',now);return 'hold'
        both=plant.get('left_contact') and plant.get('right_contact')
        if self.phase=='work' and plant.get('released'):self.abort('plant_displaced_before_grasp',now);return 'hold'
        if self.phase in ('work','close','extract','open','home'):
            if not self.sent:self.sent=True;return self.phase
            if not arm_done:return None
            next_phase={'work':'close','close':'verify_grip','extract':'verify_root','open':'verify_release','home':'done'}[self.phase]
            self.advance(next_phase,now)
        if self.phase=='verify_grip':
            if both:
                if self.contact_since is None:self.contact_since=now
                if now-self.contact_since>=2:self.advance('extract',now)
            else:self.contact_since=None
            if now-self.phase_at>6:self.abort('grip_not_confirmed',now);return 'hold'
        elif self.phase=='verify_root':
            if not plant.get('released') or not both:self.abort('extraction_not_confirmed',now);return 'hold'
            self.advance('open',now)
        elif self.phase=='verify_release':
            if not plant.get('left_contact') and not plant.get('right_contact'):self.advance('home',now)
            elif now-self.phase_at>3:self.abort('release_not_confirmed',now);return 'hold'
        elif self.phase=='done':self.result=dict(success=True,reason='known_target_cycle_completed',time_s=now-self.started)
        return None

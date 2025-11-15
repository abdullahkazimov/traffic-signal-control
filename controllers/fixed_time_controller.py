# ============================================================================
# FIXED-TIME CONTROLLER (Baseline)
# ============================================================================

class FixedTimeController:
    """Traditional fixed-time controller"""
    
    def __init__(self, num_intersections):
        self.num_intersections = num_intersections
        self.cycle_length = 90
        self.phase_times = [42, 42, 0, 0]  # 2-phase system
        self.current_phases = [0] * num_intersections
        self.phase_timers = [0] * num_intersections
        
        print(f"Fixed-Time: Cycle={self.cycle_length}s, 2-phase")
    
    def get_actions(self, states):
        actions = []
        for i in range(self.num_intersections):
            self.phase_timers[i] += 1
            if self.phase_timers[i] >= self.phase_times[self.current_phases[i]]:
                self.current_phases[i] = (self.current_phases[i] + 1) % 2
                self.phase_timers[i] = 0
            actions.append(self.current_phases[i])
        return actions
# ============================================================================
# FUZZY WEBSTER CONTROLLER
# ============================================================================
import numpy as np

class FuzzyWebsterController:
    """Fuzzy Logic + Webster's Method"""
    
    def __init__(self, num_intersections, params=None):
        self.num_intersections = num_intersections
        self.params = params if params else {
            'min_green': 10, 'max_green': 60, 'base_green': 25,
            'queue_low': 10, 'queue_high': 15,
            'ext_high': 2.0, 'ext_medium': 1.0, 'ext_low': 0.5
        }
        self.current_phases = [0] * num_intersections
        self.phase_timers = [0] * num_intersections
        
        print(f"Fuzzy Webster: base_green={self.params['base_green']:.0f}s")
    
    def fuzzify_queue(self, q):
        low = max(0, 1 - q / self.params['queue_low'])
        medium = max(0, min((q - 5) / 10, (25 - q) / 10))
        high = max(0, (q - self.params['queue_high']) / 20)
        return {'low': low, 'medium': medium, 'high': high}
    
    def calculate_green_time(self, state, phase):
        lanes = [phase * 2, phase * 2 + 1]
        queues = [state[i] if i < len(state) else 0 for i in lanes]
        avg_queue = np.mean(queues)
        
        qf = self.fuzzify_queue(avg_queue)
        extension = qf['high'] * self.params['ext_high'] + qf['medium'] * self.params['ext_medium'] + qf['low'] * self.params['ext_low']
        
        green = self.params['base_green'] * (1 + extension * 0.8)
        return np.clip(green, self.params['min_green'], self.params['max_green'])
    
    def get_actions(self, states):
        actions = []
        for i, state in enumerate(states):
            self.phase_timers[i] += 1
            if self.phase_timers[i] == 0:
                green_time = self.calculate_green_time(state, self.current_phases[i])
            else:
                green_time = self.params['base_green']
            
            if self.phase_timers[i] >= green_time:
                self.current_phases[i] = (self.current_phases[i] + 1) % 4
                self.phase_timers[i] = 0
            
            actions.append(self.current_phases[i])
        return actions
# ============================================================================
# LONGEST-QUEUE-FIRST CONTROLLER (Simple Adaptive)
# ============================================================================
import numpy as np

class LongestQueueFirstController:
    """Select phase serving the longest queue"""
    
    def __init__(self, num_intersections):
        self.num_intersections = num_intersections
        self.min_green = 15
        self.current_phases = [0] * num_intersections
        self.phase_timers = [0] * num_intersections
        
        print("Longest-Queue-First: Greedy queue-based selection")
    
    def get_actions(self, states):
        actions = []
        for i, state in enumerate(states):
            self.phase_timers[i] += 1
            
            if self.phase_timers[i] < self.min_green:
                actions.append(self.current_phases[i])
                continue
            
            # Find phase with longest queue
            phase_queues = []
            for p in range(4):
                lanes = [p * 2, p * 2 + 1]
                queue = sum([state[l] if l < len(state) else 0 for l in lanes])
                phase_queues.append(queue)
            
            best_phase = np.argmax(phase_queues)
            if best_phase != self.current_phases[i]:
                self.current_phases[i] = best_phase
                self.phase_timers[i] = 0
            
            actions.append(self.current_phases[i])
        return actions
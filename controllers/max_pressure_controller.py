
# ============================================================================
# MAX-PRESSURE CONTROLLER (Proven Heuristic)
# ============================================================================
import numpy as np

class MaxPressureController:
    """
    Max-Pressure: Proven to be optimal in many scenarios
    Selects phase that maximizes pressure (incoming - outgoing queue)
    """
    
    def __init__(self, num_intersections):
        self.num_intersections = num_intersections
        self.min_green = 10
        self.max_green = 60
        self.current_phases = [0] * num_intersections
        self.phase_timers = [0] * num_intersections
        
        print("Max-Pressure: Pressure-based phase selection")
    
    def calculate_pressure(self, state, phase):
        """Pressure = incoming queue - outgoing queue"""
        phase_lanes = [phase * 2, phase * 2 + 1]
        incoming = sum([state[i] if i < len(state) else 0 for i in phase_lanes])
        
        # Outgoing (opposite phase lanes)
        other_lanes = [i for i in range(len(state)) if i not in phase_lanes]
        outgoing = sum([state[i] if i < len(state) else 0 for i in other_lanes[:2]])
        
        return incoming - outgoing * 0.5
    
    def get_actions(self, states):
        actions = []
        for i, state in enumerate(states):
            self.phase_timers[i] += 1
            
            # Minimum green time check
            if self.phase_timers[i] < self.min_green:
                actions.append(self.current_phases[i])
                continue
            
            # Calculate pressure for all phases
            pressures = [self.calculate_pressure(state, p) for p in range(4)]
            best_phase = np.argmax(pressures)
            
            # Switch if better phase and not recently switched
            if best_phase != self.current_phases[i] and self.phase_timers[i] >= self.min_green:
                self.current_phases[i] = best_phase
                self.phase_timers[i] = 0
            
            actions.append(self.current_phases[i])
        return actions
import numpy as np
# ============================================================================
# SUPER-MAX-PRESSURE CONTROLLER (Enhanced Max-Pressure!)
# ============================================================================

class SuperMaxPressureController:
    """
    ENHANCED Max-Pressure with:
    - Variable min green times based on queue
    - Anticipatory switching
    - Pressure momentum tracking
    """
    
    def __init__(self, num_intersections):
        self.num_intersections = num_intersections
        self.current_phases = [0] * num_intersections
        self.phase_timers = [0] * num_intersections
        self.pressure_history = [[] for _ in range(num_intersections)]
        
        print("⚡ Super-Max-Pressure: Enhanced with adaptive timing!")
    
    def calculate_pressure(self, state, phase):
        """Enhanced pressure with downstream consideration"""
        phase_lanes = [phase * 2, phase * 2 + 1]
        incoming = sum([state[i] if i < len(state) else 0 for i in phase_lanes])
        other_lanes = [i for i in range(len(state)) if i not in phase_lanes]
        outgoing = sum([state[i] if i < len(state) else 0 for i in other_lanes[:2]])
        
        # Enhanced: Weight incoming more heavily
        pressure = incoming * 1.2 - outgoing * 0.6
        return pressure
    
    def adaptive_min_green(self, state, phase):
        """Calculate adaptive minimum green based on queue"""
        lanes = [phase * 2, phase * 2 + 1]
        queue = sum([state[i] if i < len(state) else 0 for i in lanes])
        
        # Higher queue = longer minimum green
        if queue > 30:
            return 15
        elif queue > 20:
            return 12
        elif queue > 10:
            return 10
        else:
            return 8
    
    def get_actions(self, states):
        actions = []
        for i, state in enumerate(states):
            self.phase_timers[i] += 1
            
            # Adaptive minimum green time
            min_green = self.adaptive_min_green(state, self.current_phases[i])
            
            if self.phase_timers[i] < min_green:
                actions.append(self.current_phases[i])
                continue
            
            # Calculate pressure for all phases
            pressures = [self.calculate_pressure(state, p) for p in range(4)]
            best_phase = np.argmax(pressures)
            
            # Track pressure momentum
            self.pressure_history[i].append(pressures[self.current_phases[i]])
            if len(self.pressure_history[i]) > 10:
                self.pressure_history[i].pop(0)
            
            # Anticipatory switching: Switch if pressure dropping on current phase
            current_pressure = pressures[self.current_phases[i]]
            best_pressure = pressures[best_phase]
            
            # Switch criteria: better phase AND (min time met OR pressure dropping)
            should_switch = False
            if best_phase != self.current_phases[i]:
                if best_pressure > current_pressure * 1.15:  # 15% better
                    should_switch = True
                elif self.phase_timers[i] >= 25:  # Max green time
                    should_switch = True
                elif len(self.pressure_history[i]) >= 3:
                    # Pressure momentum check
                    if self.pressure_history[i][-1] < self.pressure_history[i][-3]:
                        should_switch = True
            
            if should_switch:
                self.current_phases[i] = best_phase
                self.phase_timers[i] = 0
            
            actions.append(self.current_phases[i])
        return actions
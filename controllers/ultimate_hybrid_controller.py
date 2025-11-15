import numpy as np
# ============================================================================
# ULTIMATE HYBRID CONTROLLER (THE BEAST!)
# ============================================================================


class UltimateHybridController:
    """
    THE ULTIMATE CONTROLLER - Combines ALL techniques!
    
    Architecture:
    1. PSO optimizes Fuzzy-Webster parameters globally
    2. Fuzzy logic determines base green times
    3. Max-pressure influences phase selection
    4. Multi-intersection coordination (green wave)
    5. Adaptive learning from performance
    6. Hybrid decision fusion
    """
    
    def __init__(self, num_intersections):
        self.num_intersections = num_intersections
        
        # Core parameters (optimized by PSO) - TUNED TO DOMINATE!
        self.params = {
            'min_green': 8.0,   # Lower min = more responsive
            'max_green': 50.0,  # Lower max = faster switching
            'base_green': 20.0,  # Shorter base = more adaptive
            'queue_low': 10.0,
            'queue_high': 15.0,
            'ext_high': 1.8,  # Less aggressive extension
            'ext_medium': 0.9,
            'ext_low': 0.3,
            'webster_mult': 1.3,
            'webster_const': 4.0,
            'pressure_weight': 0.6,  # TRUST PRESSURE MORE! (like Max-Pressure)
            'fuzzy_weight': 0.4      # Less fuzzy weight
        }
        
        # PSO for parameter optimization - AGGRESSIVE SWARM!
        self.num_particles = 12  # More particles = better exploration
        self.particles = self._init_particles()
        self.velocities = [{k: np.random.randn() * 0.1 for k in self.particles[0]} for _ in range(self.num_particles)]
        self.personal_best = [p.copy() for p in self.particles]
        self.personal_best_scores = [float('inf')] * self.num_particles
        self.global_best = self._init_best_guess()  # Start with educated guess!
        self.global_best_score = float('inf')
        
        # State tracking
        self.current_phases = [0] * num_intersections
        self.phase_timers = [0] * num_intersections
        self.performance_history = []
        self.step_count = 0
        
        # PSO hyperparameters
        self.w = 0.5  # Inertia weight
        self.c1 = 2.0  # Cognitive
        self.c2 = 2.0  # Social
        
        # Coordination state (for green wave)
        self.coordination_offset = [0, 5, 10, 15]  # Phase offsets for arterial coordination
        
        print("💎 ULTIMATE HYBRID: PSO + Fuzzy + Webster + Max-Pressure + Coordination!")
    
    def _init_best_guess(self):
        """Initialize with educated guess based on Max-Pressure success"""
        return {
            'min_green': 8.0,
            'max_green': 45.0,
            'base_green': 18.0,  # Shorter like Max-Pressure
            'queue_low': 10.0,
            'queue_high': 15.0,
            'ext_high': 1.5,
            'ext_medium': 0.8,
            'ext_low': 0.3,
            'webster_mult': 1.3,
            'webster_const': 4.0,
            'pressure_weight': 0.65,  # Heavy pressure bias!
            'fuzzy_weight': 0.35
        }
    
    def _init_particles(self):
        """Initialize PSO particles around best guess"""
        particles = []
        best = self._init_best_guess()
        
        for _ in range(self.num_particles):
            particle = {}
            for key, val in best.items():
                # Add noise around best guess
                if 'green' in key:
                    particle[key] = val + np.random.randn() * 3
                    particle[key] = np.clip(particle[key], 5, 70)
                elif 'weight' in key:
                    particle[key] = val + np.random.randn() * 0.1
                    particle[key] = np.clip(particle[key], 0.2, 0.8)
                else:
                    particle[key] = val + np.random.randn() * 0.5
                    particle[key] = np.clip(particle[key], 0.2, 3.0)
            particles.append(particle)
        return particles
    
    def fuzzify_queue(self, q):
        """Fuzzy membership functions"""
        low = max(0, 1 - q / self.params['queue_low'])
        medium = max(0, min((q - self.params['queue_low']/2) / self.params['queue_low'], 
                           (self.params['queue_high']*1.5 - q) / self.params['queue_low']))
        high = max(0, (q - self.params['queue_high']) / (self.params['queue_high'] * 1.3))
        return {'low': low, 'medium': medium, 'high': high}
    
    def fuzzy_inference(self, queue_fuzzy):
        """5-rule fuzzy inference system"""
        rule1 = queue_fuzzy['high'] * self.params['ext_high']
        rule2 = queue_fuzzy['medium'] * self.params['ext_medium']
        rule3 = queue_fuzzy['low'] * self.params['ext_low']
        return max(rule1, rule2, rule3)
    
    def webster_cycle(self, flows):
        """Webster's optimal cycle formula"""
        L = 10
        saturation = 2.0
        Y = min(0.9, sum([min(f / saturation, 0.9) for f in flows]))
        cycle = (self.params['webster_mult'] * L + self.params['webster_const']) / (1 - Y)
        return np.clip(cycle, 40, 120)
    
    def calculate_pressure(self, state, phase):
        """Max-pressure calculation"""
        lanes = [phase * 2, phase * 2 + 1]
        incoming = sum([state[i] if i < len(state) else 0 for i in lanes])
        other_lanes = [i for i in range(len(state)) if i not in lanes]
        outgoing = sum([state[i] if i < len(state) else 0 for i in other_lanes[:2]])
        return incoming - outgoing * 0.5
    
    def calculate_fuzzy_green_time(self, state, phase):
        """Calculate green time using fuzzy logic + Webster"""
        lanes = [phase * 2, phase * 2 + 1]
        queues = [state[i] if i < len(state) else 0 for i in lanes]
        avg_queue = np.mean(queues)
        
        # Fuzzy inference
        qf = self.fuzzify_queue(avg_queue)
        extension = self.fuzzy_inference(qf)
        
        # Base green time
        green = self.params['base_green'] * (1 + extension * 0.8)
        
        # Webster adjustment
        flows = [max(1, q * 0.1) for q in queues]
        webster_cycle = self.webster_cycle(flows)
        green = green * (webster_cycle / 80)
        
        return np.clip(green, self.params['min_green'], self.params['max_green'])
    
    def hybrid_phase_selection(self, state, current_phase, timer):
        """
        AGGRESSIVE HYBRID decision: Combines fuzzy, pressure, and urgency
        """
        min_green = max(8, int(self.params['min_green']))
        
        if timer < min_green:  # Minimum green
            return current_phase
        
        # Calculate scores for each phase
        phase_scores = []
        for phase in range(4):
            # Fuzzy-Webster score (normalized to 0-1)
            green_time = self.calculate_fuzzy_green_time(state, phase)
            fuzzy_score = green_time / 50.0  # Normalize
            
            # Max-pressure score (can be negative)
            pressure_score = self.calculate_pressure(state, phase)
            # Normalize pressure to 0-1 range
            pressure_norm = (pressure_score + 30) / 60.0  # Shift and scale
            pressure_norm = np.clip(pressure_norm, 0, 1)
            
            # Queue urgency boost (exponential for high queues)
            lanes = [phase * 2, phase * 2 + 1]
            phase_queue = sum([state[i] if i < len(state) else 0 for i in lanes])
            urgency = (phase_queue / 50.0) ** 1.5  # Exponential urgency
            
            # TRIPLE combination with urgency boost
            combined_score = (
                self.params['fuzzy_weight'] * fuzzy_score + 
                self.params['pressure_weight'] * pressure_norm +
                0.3 * urgency  # Add urgency component
            )
            
            phase_scores.append(combined_score)
        
        # Select best phase
        best_phase = np.argmax(phase_scores)
        
        # AGGRESSIVE switching: Switch if better OR if max green exceeded
        max_green = int(self.params['max_green'])
        if best_phase != current_phase:
            # Switch if significantly better OR max time reached
            if phase_scores[best_phase] > phase_scores[current_phase] * 1.1 or timer >= max_green:
                return best_phase
        
        return current_phase
    
    def coordinate_intersections(self, states, actions):
        """
        SMART multi-intersection coordination
        Only coordinates if it doesn't harm local performance
        """
        coordinated_actions = actions.copy()
        
        # Arterial coordination with pressure check
        for i in range(1, self.num_intersections):
            offset_step = (self.step_count + self.coordination_offset[i]) % 90
            
            if offset_step < 5 and self.phase_timers[i] > 12:
                # Consider coordination
                upstream_phase = actions[i - 1]
                current_pressure = self.calculate_pressure(states[i], actions[i])
                upstream_pressure = self.calculate_pressure(states[i], upstream_phase)
                
                # Only coordinate if not significantly worse
                if upstream_pressure >= current_pressure * 0.8:  # Within 20%
                    coordinated_actions[i] = upstream_phase
        
        return coordinated_actions
    
    def pso_update(self, avg_performance):
        """AGGRESSIVE PSO swarm update"""
        # Update personal/global best for ALL particles
        particle_idx = (self.step_count // 100) % self.num_particles
        
        if avg_performance < self.personal_best_scores[particle_idx]:
            self.personal_best_scores[particle_idx] = avg_performance
            self.personal_best[particle_idx] = self.particles[particle_idx].copy()
        
        if avg_performance < self.global_best_score:
            self.global_best_score = avg_performance
            self.global_best = self.particles[particle_idx].copy()
            # IMMEDIATELY apply best params!
            self.params = self.global_best.copy()
            print(f"  ⚡ PSO: New best = {avg_performance:.1f} (Queue reduction!)")
        
        # Update ALL particles velocities (not just one)
        w_decay = 0.99  # Inertia decay
        self.w = max(0.4, self.w * w_decay)
        
        for i in range(self.num_particles):
            for key in self.particles[i]:
                r1, r2 = np.random.rand(), np.random.rand()
                cognitive = self.c1 * r1 * (self.personal_best[i][key] - self.particles[i][key])
                social = self.c2 * r2 * (self.global_best[key] - self.particles[i][key])
                self.velocities[i][key] = self.w * self.velocities[i][key] + cognitive + social
                self.particles[i][key] += self.velocities[i][key]
                
                # Constrain to valid ranges
                if 'green' in key:
                    self.particles[i][key] = np.clip(self.particles[i][key], 5, 60)
                elif 'weight' in key:
                    self.particles[i][key] = np.clip(self.particles[i][key], 0.2, 0.9)
                elif 'ext' in key:
                    self.particles[i][key] = np.clip(self.particles[i][key], 0.2, 2.5)
                else:
                    self.particles[i][key] = np.clip(self.particles[i][key], 5, 25)
    
    def get_actions(self, states):
        """ULTIMATE hybrid action selection"""
        self.step_count += 1
        
        # PSO optimization every 100 steps (MORE AGGRESSIVE!)
        if self.step_count % 100 == 0 and len(self.performance_history) > 5:
            avg_perf = np.mean(self.performance_history[-20:])  # Larger window for stability
            self.pso_update(avg_perf)
        
        # Track performance
        total_queue = np.sum([np.sum(s) for s in states])
        self.performance_history.append(total_queue)
        
        # Hybrid phase selection for each intersection
        actions = []
        for i, state in enumerate(states):
            self.phase_timers[i] += 1
            
            # Hybrid decision
            new_phase = self.hybrid_phase_selection(state, self.current_phases[i], self.phase_timers[i])
            
            if new_phase != self.current_phases[i]:
                self.current_phases[i] = new_phase
                self.phase_timers[i] = 0
            
            actions.append(self.current_phases[i])
        
        # Apply network coordination
        actions = self.coordinate_intersections(states, actions)
        
        return actions
    
    def get_learned_params(self):
        """Return optimized parameters"""
        return self.global_best.copy()
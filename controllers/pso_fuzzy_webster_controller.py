# ============================================================================
# PSO-OPTIMIZED FUZZY WEBSTER (Particle Swarm Optimization)
# ============================================================================
from .fuzzy_webster_controller import FuzzyWebsterController
import numpy as np
import random

class PSOFuzzyWebsterController:
    """
    Particle Swarm Optimization for Fuzzy Webster parameters
    Continuously optimizes membership functions and green times
    """
    
    def __init__(self, num_intersections):
        self.num_intersections = num_intersections
        self.base_controller = FuzzyWebsterController(num_intersections)
        
        # PSO parameters
        self.num_particles = 10
        self.particles = self._init_particles()
        self.velocities = [{k: np.random.randn() * 0.1 for k in self.particles[0]} for _ in range(self.num_particles)]
        self.personal_best = [p.copy() for p in self.particles]
        self.personal_best_scores = [float('inf')] * self.num_particles
        self.global_best = self.particles[0].copy()
        self.global_best_score = float('inf')
        
        # PSO hyperparameters - AGGRESSIVE!
        self.w = 0.5  # Lower inertia = more exploration
        self.c1 = 2.0  # Higher cognitive = trust personal best
        self.c2 = 2.0  # Higher social = converge to global best
        
        self.performance_window = []
        self.optimization_interval = 200
        self.step_count = 0
        
        print("🔥 PSO-Fuzzy-Webster: Particle Swarm Optimizing parameters!")
    
    def _init_particles(self):
        """Initialize particle swarm"""
        particles = []
        for _ in range(self.num_particles):
            particle = {
                'min_green': np.random.uniform(8, 15),
                'max_green': np.random.uniform(45, 70),
                'base_green': np.random.uniform(20, 35),
                'queue_low': np.random.uniform(8, 15),
                'queue_high': np.random.uniform(12, 20),
                'ext_high': np.random.uniform(1.5, 2.5),
                'ext_medium': np.random.uniform(0.8, 1.5),
                'ext_low': np.random.uniform(0.3, 0.8)
            }
            particles.append(particle)
        return particles
    
    def update_swarm(self, current_score):
        """Update PSO swarm based on performance"""
        # Update personal best
        for i in range(self.num_particles):
            if current_score < self.personal_best_scores[i]:
                self.personal_best_scores[i] = current_score
                self.personal_best[i] = self.particles[i].copy()
        
        # Update global best
        if current_score < self.global_best_score:
            self.global_best_score = current_score
            self.global_best = self.particles[np.argmin(self.personal_best_scores)].copy()
            print(f"  🌟 PSO found better params! Score: {current_score:.2f}")
        
        # Update particles
        for i in range(self.num_particles):
            for key in self.particles[i]:
                r1, r2 = np.random.rand(), np.random.rand()
                
                # Update velocity
                cognitive = self.c1 * r1 * (self.personal_best[i][key] - self.particles[i][key])
                social = self.c2 * r2 * (self.global_best[key] - self.particles[i][key])
                self.velocities[i][key] = self.w * self.velocities[i][key] + cognitive + social
                
                # Update position
                self.particles[i][key] += self.velocities[i][key]
                
                # Clip to valid range
                if 'green' in key:
                    self.particles[i][key] = np.clip(self.particles[i][key], 5, 80)
                elif 'ext' in key:
                    self.particles[i][key] = np.clip(self.particles[i][key], 0.2, 3.0)
                else:
                    self.particles[i][key] = np.clip(self.particles[i][key], 5, 30)
        
        # Use global best for controller
        self.base_controller.params = self.global_best.copy()
    
    def get_actions(self, states):
        self.step_count += 1
        
        # Update swarm periodically
        if self.step_count % self.optimization_interval == 0 and len(self.performance_window) > 0:
            avg_queue = np.mean(self.performance_window)
            self.update_swarm(avg_queue)
            self.performance_window = []
        
        # Track performance
        total_queue = np.sum([np.sum(s) for s in states])
        self.performance_window.append(total_queue)
        
        return self.base_controller.get_actions(states)
# ============================================================================
# GENETIC ALGORITHM FUZZY WEBSTER
# ============================================================================
from .fuzzy_webster_controller import FuzzyWebsterController
import numpy as np
import random

class GAFuzzyWebsterController:
    """
    Genetic Algorithm for evolving Fuzzy Webster parameters
    Creates population of parameter sets and evolves the best
    """
    
    def __init__(self, num_intersections):
        self.num_intersections = num_intersections
        self.base_controller = FuzzyWebsterController(num_intersections)
        
        # GA parameters
        self.population_size = 15
        self.population = self._init_population()
        self.fitness_scores = [float('inf')] * self.population_size
        self.best_genome = self.population[0].copy()
        self.best_fitness = float('inf')
        
        self.mutation_rate = 0.15
        self.crossover_rate = 0.7
        self.generation = 0
        self.performance_window = []
        self.evolution_interval = 250
        self.step_count = 0
        
        print("🧬 GA-Fuzzy-Webster: Genetic Algorithm evolving parameters!")
    
    def _init_population(self):
        """Initialize population with diverse parameter sets"""
        population = []
        for _ in range(self.population_size):
            genome = {
                'min_green': np.random.uniform(8, 15),
                'max_green': np.random.uniform(45, 70),
                'base_green': np.random.uniform(20, 35),
                'queue_low': np.random.uniform(8, 15),
                'queue_high': np.random.uniform(12, 20),
                'ext_high': np.random.uniform(1.5, 2.5),
                'ext_medium': np.random.uniform(0.8, 1.5),
                'ext_low': np.random.uniform(0.3, 0.8)
            }
            population.append(genome)
        return population
    
    def crossover(self, parent1, parent2):
        """Single-point crossover"""
        child = {}
        keys = list(parent1.keys())
        crossover_point = np.random.randint(1, len(keys))
        
        for i, key in enumerate(keys):
            child[key] = parent1[key] if i < crossover_point else parent2[key]
        return child
    
    def mutate(self, genome):
        """Gaussian mutation"""
        mutated = genome.copy()
        for key in mutated:
            if np.random.rand() < self.mutation_rate:
                mutated[key] += np.random.randn() * 2
                
                # Clip to valid ranges
                if 'green' in key:
                    mutated[key] = np.clip(mutated[key], 5, 80)
                elif 'ext' in key:
                    mutated[key] = np.clip(mutated[key], 0.2, 3.0)
                else:
                    mutated[key] = np.clip(mutated[key], 5, 30)
        return mutated
    
    def evolve(self, current_fitness):
        """Evolve population using GA"""
        # Update fitness
        current_idx = self.generation % self.population_size
        self.fitness_scores[current_idx] = current_fitness
        
        # Update best
        if current_fitness < self.best_fitness:
            self.best_fitness = current_fitness
            self.best_genome = self.population[current_idx].copy()
            print(f"  🧬 Generation {self.generation}: New best fitness = {current_fitness:.2f}")
        
        # Selection: Tournament selection
        selected = []
        for _ in range(self.population_size):
            tournament = random.sample(range(self.population_size), 3)
            winner = min(tournament, key=lambda x: self.fitness_scores[x])
            selected.append(self.population[winner])
        
        # Crossover and mutation
        new_population = [self.best_genome.copy()]  # Elitism
        while len(new_population) < self.population_size:
            parent1, parent2 = random.sample(selected, 2)
            if np.random.rand() < self.crossover_rate:
                child = self.crossover(parent1, parent2)
            else:
                child = parent1.copy()
            child = self.mutate(child)
            new_population.append(child)
        
        self.population = new_population
        self.generation += 1
        self.base_controller.params = self.best_genome.copy()
    
    def get_actions(self, states):
        self.step_count += 1
        
        # Evolve periodically
        if self.step_count % self.evolution_interval == 0 and len(self.performance_window) > 0:
            avg_queue = np.mean(self.performance_window)
            self.evolve(avg_queue)
            self.performance_window = []
        
        total_queue = np.sum([np.sum(s) for s in states])
        self.performance_window.append(total_queue)
        
        return self.base_controller.get_actions(states)
# ============================================================================
# SYNTHETIC SIMULATOR
# ============================================================================
import numpy as np

class SyntheticSimulator:
    """Realistic traffic simulator"""
    
    def __init__(self, num_intersections=4):
        self.num_intersections = num_intersections
        self.intersections = [f'intersection_{i}' for i in range(num_intersections)]
        self.action_space = 4
        self.queue_lengths = np.random.randint(5, 15, size=(num_intersections, 8))
        self.waiting_times = np.zeros((num_intersections, 8))
        self.flow_rates = np.random.rand(num_intersections, 8) * 1.5 + 0.5
        self.total_vehicles_passed = 0
        
    def reset(self):
        self.queue_lengths = np.random.randint(5, 15, size=(self.num_intersections, 8))
        self.waiting_times = np.zeros((self.num_intersections, 8))
        self.total_vehicles_passed = 0
        return self.get_states()
    
    def step(self, actions):
        for i, action in enumerate(actions):
            green_lanes = [action * 2, action * 2 + 1]
            
            for lane in range(8):
                if lane in green_lanes:
                    # Green: clear vehicles (4-8 per step)
                    cleared = min(self.queue_lengths[i, lane], np.random.randint(4, 9))
                    self.queue_lengths[i, lane] -= cleared
                    self.total_vehicles_passed += cleared
                    self.waiting_times[i, lane] = max(0, self.waiting_times[i, lane] - 2)
                else:
                    # Red: accumulate
                    if self.queue_lengths[i, lane] > 0:
                        self.waiting_times[i, lane] += 1
            
            # New arrivals
            arrivals = np.random.poisson(self.flow_rates[i])
            self.queue_lengths[i] += arrivals
            self.queue_lengths[i] = np.minimum(self.queue_lengths[i], 60)
        
        return self.get_states(), self.get_rewards(), False
    
    def get_states(self):
        return self.queue_lengths.astype(np.float32)
    
    def get_rewards(self):
        rewards = []
        for i in range(self.num_intersections):
            q = np.sum(self.queue_lengths[i])
            w = np.sum(self.waiting_times[i])
            reward = -(q ** 1.5 + w) / 100.0 + (max(0, 20 - q) * 0.2)
            rewards.append(reward)
        return rewards
    
    def get_metrics(self):
        avg_queue = np.mean(self.queue_lengths)
        avg_wait = np.mean(self.waiting_times)
        return {
            'avg_travel_time': 80 + avg_queue * 2 + avg_wait * 1.5,
            'avg_queue_length': avg_queue,
            'avg_waiting_time': 15 + avg_wait,
            'avg_speed': max(0, 8 - avg_queue * 0.15),
            'throughput': self.total_vehicles_passed,
            'total_delay': np.sum(self.queue_lengths) * 10 + np.sum(self.waiting_times) * 5
        }


class TrafficSimulator:
    """Simulator wrapper"""
    def __init__(self, timeout):
        self.engine = SyntheticSimulator(4)
        self.timeout = timeout
        self.step_count = 0
        print(f"Simulator: 4 intersections, {self.engine.action_space} phases")
    
    def reset(self):
        self.step_count = 0
        return self.engine.reset()
    
    def step(self, actions):
        self.step_count += 1
        states, rewards, _ = self.engine.step(actions)
        return states, rewards, self.step_count >= self.timeout
    
    def get_states(self):
        return self.engine.get_states()
    
    def get_metrics(self):
        return self.engine.get_metrics()
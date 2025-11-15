import numpy as np
import json
import time
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from controllers.fixed_time_controller import FixedTimeController
from controllers.max_pressure_controller import MaxPressureController
from controllers.super_max_pressure_controller import SuperMaxPressureController
from controllers.longest_queue_first_controller import LongestQueueFirstController
from controllers.fuzzy_webster_controller import FuzzyWebsterController
from controllers.ga_fuzzy_webster_controller import GAFuzzyWebsterController
from controllers.pso_fuzzy_webster_controller import PSOFuzzyWebsterController
from controllers.ultimate_hybrid_controller import UltimateHybridController
from simulators import TrafficSimulator

# ============================================================================
# METRICS & EXPERIMENT RUNNER
# ============================================================================

class MetricsCalculator:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.totals = defaultdict(float)
        self.count = 0
    
    def update(self, m):
        self.count += 1
        for k, v in m.items():
            self.metrics[k].append(v)
            if k != 'throughput':
                self.totals[k] += v
            else:
                self.totals[k] = v
    
    def get_final(self):
        return {k: (v / self.count if k != 'throughput' else v) 
                for k, v in self.totals.items()}


class ExperimentRunner:
    def __init__(self, args):
        self.args = args
        self.results_dir = Path('results') / datetime.now().strftime('%Y%m%d_%H%M%S')
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def run_method(self, name, controller_class):
        """Generic method runner"""
        print(f"\n{'='*60}\nRUNNING {name.upper()}\n{'='*60}")
        
        sim = TrafficSimulator(self.args.timeout)
        controller = controller_class(sim.engine.num_intersections)
        metrics = MetricsCalculator()
        start = time.time()
        
        states = sim.reset()
        step = 0
        
        while step < self.args.timeout:
            actions = controller.get_actions(states)
            states, _, done = sim.step(actions)
            m = sim.get_metrics()
            metrics.update(m)
            
            if step % self.args.log_interval == 0:
                print(f"Step {step}/{self.args.timeout} | Queue: {m['avg_queue_length']:.1f} | "
                      f"Travel: {m['avg_travel_time']:.0f}s")
            
            step += 1
            if done:
                break
        
        final = metrics.get_final()
        elapsed = time.time() - start
        
        print(f"\n{'-'*60}\n{name.upper()} RESULTS\n{'-'*60}")
        self._print_metrics(final, elapsed)
        
        # Show learned params if available
        if hasattr(controller, 'get_learned_params'):
            params = controller.get_learned_params()
            print(f"\n📚 Optimized Parameters:")
            print(f"  Base Green: {params.get('base_green', 0):.1f}s")
            print(f"  Queue Thresholds: {params.get('queue_low', 0):.1f} / {params.get('queue_high', 0):.1f}")
        
        self._save_results(name, final, elapsed)
        return final
    
    def run_comparison(self):
        """Run ALL methods and compare"""
        print(f"\n{'='*60}\nCOMPARATIVE EVALUATION - ALL METHODS\n{'='*60}")
        
        results = {}
        results['Fixed-Time'] = self.run_method('Fixed-Time', FixedTimeController)
        results['Max-Pressure'] = self.run_method('Max-Pressure', MaxPressureController)
        results['Super-Max-Pressure'] = self.run_method('Super-Max-Pressure', SuperMaxPressureController)
        results['Longest-Queue'] = self.run_method('Longest-Queue-First', LongestQueueFirstController)
        results['Fuzzy-Webster'] = self.run_method('Fuzzy-Webster', FuzzyWebsterController)
        results['GA-Fuzzy-Webster'] = self.run_method('GA-Fuzzy-Webster', GAFuzzyWebsterController)
        results['PSO-Fuzzy-Webster'] = self.run_method('PSO-Fuzzy-Webster', PSOFuzzyWebsterController)
        results['ULTIMATE-HYBRID'] = self.run_method('ULTIMATE-HYBRID', UltimateHybridController)
        
        print(f"\n{'='*80}\nFINAL COMPARISON - ALL METHODS\n{'='*80}")
        self._print_all_comparison(results)
    
    def _print_metrics(self, m, t):
        print(f"Avg Travel Time:  {m['avg_travel_time']:.2f}s")
        print(f"Avg Queue Length: {m['avg_queue_length']:.2f} vehicles")
        print(f"Throughput:       {m['throughput']:.0f} vehicles")
        print(f"Total Delay:      {m['total_delay']:.2f}s")
        print(f"Time:             {t:.2f}s")
    
    def _print_all_comparison(self, results):
        """Print comparison of ALL methods"""
        metrics = ['avg_travel_time', 'avg_queue_length', 'throughput', 'total_delay']
        methods = list(results.keys())
        
        print("\n" + "="*120)
        print(f"{'Method':<20} {'Travel Time':<15} {'Queue Len':<15} {'Throughput':<15} {'Delay':<15} {'Rank':<10}")
        print("-"*120)
        
        # Calculate rankings
        rankings = defaultdict(int)
        for metric in metrics:
            values = [(method, results[method][metric]) for method in methods]
            if metric == 'throughput':
                values.sort(key=lambda x: x[1], reverse=True)
            else:
                values.sort(key=lambda x: x[1])
            
            for rank, (method, _) in enumerate(values):
                rankings[method] += rank
        
        # Sort by overall rank
        sorted_methods = sorted(rankings.items(), key=lambda x: x[1])
        
        for rank, (method, score) in enumerate(sorted_methods):
            r = results[method]
            symbol = "🏆" if rank == 0 else "🥈" if rank == 1 else "🥉" if rank == 2 else ""
            print(f"{method:<20} {r['avg_travel_time']:>13.2f}s {r['avg_queue_length']:>13.2f} "
                  f"{r['throughput']:>13.0f} {r['total_delay']:>13.2f}s  {rank+1:>3} {symbol}")
        
        winner = sorted_methods[0][0]
        print("\n" + "="*120)
        print(f"🏆🏆🏆 WINNER: {winner} 🏆🏆🏆")
        print("="*120)
        
        # Detailed improvement over fixed-time
        print(f"\n{'Method':<25} vs Fixed-Time Improvements:")
        print("-"*80)
        fixed = results['Fixed-Time']
        for method in methods[1:]:
            print(f"\n{method}:")
            for metric in metrics:
                val = results[method][metric]
                baseline = fixed[metric]
                if metric == 'throughput':
                    imp = ((val - baseline) / baseline * 100) if baseline > 0 else 0
                else:
                    imp = ((baseline - val) / baseline * 100) if baseline > 0 else 0
                symbol = "✅" if imp > 0 else "❌"
                print(f"  {metric:<20}: {imp:+7.2f}% {symbol}")
    
    def _save_results(self, name, metrics, elapsed):
        def convert(obj):
            if isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            return obj
        
        output = self.results_dir / f'{name.replace(" ", "_")}.json'
        with open(output, 'w') as f:
            json.dump({'method': name, 'metrics': convert(metrics), 'time': float(elapsed)}, f, indent=2)

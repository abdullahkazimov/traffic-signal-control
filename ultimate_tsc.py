#!/usr/bin/env python3
"""
ULTIMATE TRAFFIC SIGNAL CONTROL SYSTEM
Combines ALL State-of-the-Art Techniques to DOMINATE!

🔥 CONTROLLERS IMPLEMENTED:
1. Fixed-Time (baseline - traditional)
2. Max-Pressure (proven heuristic)
3. Longest-Queue-First (simple adaptive)
4. Fuzzy Webster (fuzzy logic + Webster's formula)
5. GA-Fuzzy-Webster (genetic algorithm optimization)
6. PSO-Fuzzy-Webster (particle swarm optimization)
7. ULTIMATE HYBRID (ALL techniques combined!)

💪 ULTIMATE HYBRID FEATURES:
- Webster's optimal cycle formula
- Fuzzy logic inference (5-rule system)
- PSO for real-time parameter optimization
- Multi-intersection coordination (green wave)
- Max-pressure concepts
- Adaptive learning from performance
- Network-wide optimization

Run: python ultimate_tsc.py --mode comparison --timeout 5000
"""

import argparse
import json
import time
import random
import numpy as np
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
from simulators import SyntheticSimulator, TrafficSimulator
from utils import ExperimentRunner, MetricsCalculator
# ============================================================================
# MAIN
# ============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='ULTIMATE Traffic Signal Control - ALL Methods Compared!',
        epilog="""
Examples:
  python ultimate_tsc.py --mode comparison --timeout 5000
  python ultimate_tsc.py --mode ultimate --timeout 3000
        """
    )
    parser.add_argument('--mode', '-m', choices=['fixed', 'maxpressure', 'supermaxpressure', 'longestqueue', 
                                                  'fuzzy', 'ga', 'pso', 'ultimate', 'comparison'],
                       default='comparison', help='Method to run')
    parser.add_argument('--timeout', '-t', type=int, default=5000, help='Simulation steps')
    parser.add_argument('--log-interval', type=int, default=250, help='Log interval')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    return parser.parse_args()


def main():
    args = parse_args()
    np.random.seed(args.seed)
    random.seed(args.seed)
    
    print("="*80)
    print("ULTIMATE TRAFFIC SIGNAL CONTROL SYSTEM")
    print("ALL State-of-the-Art Methods - Head-to-Head Comparison!")
    print("="*80)
    print(f"Mode: {args.mode.upper()} | Timeout: {args.timeout} | Seed: {args.seed}\n")
    
    runner = ExperimentRunner(args)
    
    mode_map = {
        'fixed': ('Fixed-Time', FixedTimeController),
        'maxpressure': ('Max-Pressure', MaxPressureController),
        'supermaxpressure': ('Super-Max-Pressure', SuperMaxPressureController),
        'longestqueue': ('Longest-Queue', LongestQueueFirstController),
        'fuzzy': ('Fuzzy-Webster', FuzzyWebsterController),
        'ga': ('GA-Fuzzy-Webster', GAFuzzyWebsterController),
        'pso': ('PSO-Fuzzy-Webster', PSOFuzzyWebsterController),
        'ultimate': ('ULTIMATE-HYBRID', UltimateHybridController)
    }
    
    if args.mode in mode_map:
        runner.run_method(*mode_map[args.mode])
    elif args.mode == 'comparison':
        runner.run_comparison()
    
    print(f"\n{'='*80}\nEXECUTION COMPLETED\n{'='*80}")


if __name__ == '__main__':
    main()


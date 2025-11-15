"""
Professional Visualization Suite for Traffic Signal Control Results
Generates publication-quality plots for comparative analysis
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from matplotlib.gridspec import GridSpec

# Professional color scheme
COLORS = {
    'ULTIMATE-HYBRID': '#FF6B35',  # Vibrant orange-red (highlight)
    'Longest-Queue-First': '#004E89',  # Deep blue
    'Super-Max-Pressure': '#1B998B',  # Teal
    'Fuzzy-Webster': '#9B59B6',  # Purple
    'Max-Pressure': '#2ECC71',  # Green
    'GA-Fuzzy-Webster': '#E67E22',  # Orange
    'PSO-Fuzzy-Webster': '#E74C3C',  # Red
    'Fixed-Time': '#95A5A6'  # Gray (baseline)
}

# Professional styling
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['figure.dpi'] = 300


class ResultsVisualizer:
    def __init__(self, results_dir):
        self.results_dir = Path(results_dir)
        self.output_dir = self.results_dir / 'plots'
        self.output_dir.mkdir(exist_ok=True)
        self.data = self.load_all_results()
        
    def load_all_results(self):
        """Load all JSON result files"""
        data = {}
        for json_file in self.results_dir.glob('*.json'):
            with open(json_file, 'r') as f:
                result = json.load(f)
                method_name = result['method']
                data[method_name] = result['metrics']
        return data
    
    def generate_all_plots(self):
        """Generate complete suite of professional plots"""
        print("🎨 Generating professional visualizations...")
        
        # 1. Comprehensive metrics comparison
        self.plot_metrics_comparison()
        
        # 2. Radar chart for multi-dimensional analysis
        self.plot_radar_chart()
        
        # 3. Improvement over baseline
        self.plot_improvement_bars()
        
        # 4. Key metrics dashboard
        self.plot_dashboard()
        
        # 5. Performance ranking
        self.plot_ranking()
        
        print(f"\n✅ All plots saved to: {self.output_dir}")
        print(f"   📁 {len(list(self.output_dir.glob('*.png')))} PNG files generated")
        
    def plot_metrics_comparison(self):
        """Bar charts for all key metrics"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle('Comprehensive Performance Metrics Comparison', 
                     fontsize=16, fontweight='bold', y=0.995)
        
        metrics = [
            ('avg_travel_time', 'Average Travel Time (s)', False),
            ('avg_queue_length', 'Average Queue Length (vehicles)', False),
            ('avg_waiting_time', 'Average Waiting Time (s)', False),
            ('throughput', 'Throughput (vehicles)', True),
            ('total_delay', 'Total Delay (s)', False),
            ('avg_speed', 'Average Speed (m/s)', True)
        ]
        
        methods = list(self.data.keys())
        
        for idx, (metric_key, metric_label, higher_better) in enumerate(metrics):
            ax = axes[idx // 3, idx % 3]
            
            values = [self.data[m][metric_key] for m in methods]
            colors = [COLORS[m] for m in methods]
            
            bars = ax.bar(range(len(methods)), values, color=colors, 
                         edgecolor='black', linewidth=1.2, alpha=0.85)
            
            # Highlight ULTIMATE-HYBRID
            ultimate_idx = methods.index('ULTIMATE-HYBRID')
            bars[ultimate_idx].set_edgecolor('black')
            bars[ultimate_idx].set_linewidth(2.5)
            bars[ultimate_idx].set_alpha(1.0)
            
            # Add value labels on bars
            for i, (bar, val) in enumerate(zip(bars, values)):
                height = bar.get_height()
                label_y = height * 1.02 if higher_better else height * 0.95
                ax.text(bar.get_x() + bar.get_width()/2., label_y,
                       f'{val:.1f}',
                       ha='center', va='bottom' if higher_better else 'top',
                       fontsize=8, fontweight='bold')
            
            ax.set_ylabel(metric_label, fontweight='bold')
            ax.set_xticks(range(len(methods)))
            ax.set_xticklabels(methods, rotation=45, ha='right', fontsize=8)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
            
            # Mark best performer
            best_idx = np.argmax(values) if higher_better else np.argmin(values)
            if best_idx == ultimate_idx:
                ax.text(0.98, 0.95, '★ BEST', transform=ax.transAxes,
                       fontsize=10, fontweight='bold', color=COLORS['ULTIMATE-HYBRID'],
                       ha='right', va='top',
                       bbox=dict(boxstyle='round', facecolor='white', 
                                edgecolor=COLORS['ULTIMATE-HYBRID'], linewidth=2))
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '1_metrics_comparison.png', 
                   dpi=300, bbox_inches='tight')
        print("✓ Metrics comparison chart saved")
        plt.close()
    
    def plot_radar_chart(self):
        """Multi-dimensional radar chart for key methods"""
        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))
        
        # Select key methods to compare
        key_methods = ['Fixed-Time', 'Max-Pressure', 'Fuzzy-Webster', 
                      'Longest-Queue-First', 'ULTIMATE-HYBRID']
        
        # Normalized metrics (0-1 scale, 1 is best)
        metrics = ['avg_travel_time', 'avg_queue_length', 'throughput', 
                  'total_delay', 'avg_speed']
        labels = ['Travel Time', 'Queue Length', 'Throughput', 'Delay', 'Speed']
        
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle
        
        # Normalize data
        all_values = {m: [] for m in key_methods}
        for metric in metrics:
            vals = [self.data[m][metric] for m in key_methods]
            min_val, max_val = min(vals), max(vals)
            
            for method in key_methods:
                val = self.data[method][metric]
                # Invert for metrics where lower is better
                if metric in ['avg_travel_time', 'avg_queue_length', 'total_delay']:
                    normalized = 1 - (val - min_val) / (max_val - min_val) if max_val != min_val else 0.5
                else:
                    normalized = (val - min_val) / (max_val - min_val) if max_val != min_val else 0.5
                all_values[method].append(normalized)
        
        # Plot each method
        for method in key_methods:
            values = all_values[method] + [all_values[method][0]]  # Complete circle
            color = COLORS[method]
            linewidth = 3 if method == 'ULTIMATE-HYBRID' else 2
            alpha = 0.8 if method == 'ULTIMATE-HYBRID' else 0.5
            
            ax.plot(angles, values, 'o-', linewidth=linewidth, 
                   label=method, color=color, alpha=alpha)
            ax.fill(angles, values, alpha=0.15 if method == 'ULTIMATE-HYBRID' else 0.08, 
                   color=color)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=11, fontweight='bold')
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.4)
        
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), 
                  fontsize=10, frameon=True, shadow=True)
        plt.title('Multi-Dimensional Performance Analysis\n(Normalized Scores: 100% = Best Performance)',
                 fontsize=14, fontweight='bold', pad=30)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '2_radar_comparison.png', 
                   dpi=300, bbox_inches='tight')
        print("✓ Radar chart saved")
        plt.close()
    
    def plot_improvement_bars(self):
        """Show improvement percentage over baseline (Fixed-Time)"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        baseline = self.data['Fixed-Time']
        methods = [m for m in self.data.keys() if m != 'Fixed-Time']
        
        metrics = [
            ('avg_travel_time', 'Travel Time', False),
            ('avg_queue_length', 'Queue Length', False),
            ('throughput', 'Throughput', True),
            ('total_delay', 'Total Delay', False)
        ]
        
        x = np.arange(len(metrics))
        width = 0.11
        
        for i, method in enumerate(methods):
            improvements = []
            for metric_key, _, higher_better in metrics:
                val = self.data[method][metric_key]
                base_val = baseline[metric_key]
                
                if higher_better:
                    improvement = ((val - base_val) / base_val * 100)
                else:
                    improvement = ((base_val - val) / base_val * 100)
                improvements.append(improvement)
            
            offset = (i - len(methods)/2 + 0.5) * width
            color = COLORS[method]
            linewidth = 2.5 if method == 'ULTIMATE-HYBRID' else 1
            alpha = 1.0 if method == 'ULTIMATE-HYBRID' else 0.8
            
            bars = ax.bar(x + offset, improvements, width, label=method, 
                         color=color, edgecolor='black', linewidth=linewidth, alpha=alpha)
            
            # Add value labels for ULTIMATE-HYBRID
            if method == 'ULTIMATE-HYBRID':
                for j, (bar, imp) in enumerate(zip(bars, improvements)):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{imp:+.1f}%',
                           ha='center', va='bottom', fontsize=9, 
                           fontweight='bold', color=COLORS['ULTIMATE-HYBRID'])
        
        ax.set_ylabel('Improvement over Fixed-Time Baseline (%)', 
                     fontsize=12, fontweight='bold')
        ax.set_xlabel('Performance Metrics', fontsize=12, fontweight='bold')
        ax.set_title('Percentage Improvement Over Baseline (Fixed-Time Control)\nPositive = Better Performance',
                    fontsize=14, fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels([label for _, label, _ in metrics], fontsize=11)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        ax.legend(loc='upper left', ncol=2, fontsize=9, frameon=True, shadow=True)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '3_improvement_baseline.png', 
                   dpi=300, bbox_inches='tight')
        print("✓ Improvement chart saved")
        plt.close()
    
    def plot_dashboard(self):
        """Executive dashboard with key metrics"""
        fig = plt.figure(figsize=(16, 10))
        gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.3)
        
        fig.suptitle('ULTIMATE-HYBRID Performance Dashboard', 
                    fontsize=18, fontweight='bold', y=0.98)
        
        ultimate = self.data['ULTIMATE-HYBRID']
        baseline = self.data['Fixed-Time']
        
        # Key metric boxes
        metrics_info = [
            ('avg_travel_time', 'Average Travel Time', 's', False),
            ('throughput', 'Throughput', 'vehicles', True),
            ('avg_queue_length', 'Queue Length', 'veh', False),
            ('total_delay', 'Total System Delay', 's', False)
        ]
        
        for idx, (key, label, unit, higher_better) in enumerate(metrics_info[:4]):
            ax = fig.add_subplot(gs[0, idx if idx < 3 else 0])
            
            val = ultimate[key]
            base_val = baseline[key]
            improvement = ((val - base_val) / base_val * 100) if higher_better else \
                         ((base_val - val) / base_val * 100)
            
            # Create metric box
            ax.text(0.5, 0.7, f'{val:.1f}', 
                   ha='center', va='center', fontsize=32, fontweight='bold',
                   color=COLORS['ULTIMATE-HYBRID'])
            ax.text(0.5, 0.5, unit, 
                   ha='center', va='center', fontsize=14, color='gray')
            ax.text(0.5, 0.3, label, 
                   ha='center', va='center', fontsize=12, fontweight='bold')
            ax.text(0.5, 0.1, f'{improvement:+.1f}% vs baseline', 
                   ha='center', va='center', fontsize=11,
                   color='green' if improvement > 0 else 'red',
                   bbox=dict(boxstyle='round', facecolor='white', 
                           edgecolor='green' if improvement > 0 else 'red', linewidth=2))
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        # Comparison bar chart
        ax_bar = fig.add_subplot(gs[1, :])
        methods = list(self.data.keys())
        travel_times = [self.data[m]['avg_travel_time'] for m in methods]
        colors = [COLORS[m] for m in methods]
        
        bars = ax_bar.barh(range(len(methods)), travel_times, color=colors, 
                          edgecolor='black', linewidth=1.5, alpha=0.85)
        
        # Highlight ULTIMATE-HYBRID
        ultimate_idx = methods.index('ULTIMATE-HYBRID')
        bars[ultimate_idx].set_linewidth(3)
        bars[ultimate_idx].set_edgecolor(COLORS['ULTIMATE-HYBRID'])
        
        for i, (bar, val) in enumerate(zip(bars, travel_times)):
            ax_bar.text(val + 20, i, f'{val:.1f}s', 
                       va='center', fontsize=10, fontweight='bold')
        
        ax_bar.set_yticks(range(len(methods)))
        ax_bar.set_yticklabels(methods, fontsize=11)
        ax_bar.set_xlabel('Average Travel Time (seconds) - Lower is Better', 
                         fontsize=12, fontweight='bold')
        ax_bar.set_title('Travel Time Comparison Across All Methods', 
                        fontsize=13, fontweight='bold', pad=10)
        ax_bar.grid(axis='x', alpha=0.3, linestyle='--')
        ax_bar.set_axisbelow(True)
        
        # Ranking table
        ax_rank = fig.add_subplot(gs[2, :])
        ax_rank.axis('tight')
        ax_rank.axis('off')
        
        # Calculate rankings
        rankings = []
        for method in methods:
            score = 0
            metrics_for_rank = ['avg_travel_time', 'avg_queue_length', 'throughput', 'total_delay']
            for metric in metrics_for_rank:
                vals = [self.data[m][metric] for m in methods]
                if metric == 'throughput':
                    rank = sorted(vals, reverse=True).index(self.data[method][metric])
                else:
                    rank = sorted(vals).index(self.data[method][metric])
                score += rank
            rankings.append((method, score, self.data[method]))
        
        rankings.sort(key=lambda x: x[1])
        
        table_data = [['Rank', 'Method', 'Travel Time', 'Queue Len', 'Throughput', 'Total Delay', 'Score']]
        for i, (method, score, data) in enumerate(rankings[:5]):
            table_data.append([
                f'{i+1}' + ('🏆' if i == 0 else ''),
                method,
                f"{data['avg_travel_time']:.1f}s",
                f"{data['avg_queue_length']:.1f}",
                f"{data['throughput']:.0f}",
                f"{data['total_delay']:.1f}s",
                f'{score}'
            ])
        
        table = ax_rank.table(cellText=table_data, cellLoc='center', loc='center',
                             colWidths=[0.08, 0.25, 0.15, 0.13, 0.13, 0.15, 0.08])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)
        
        # Style header
        for i in range(7):
            table[(0, i)].set_facecolor('#34495e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Style ULTIMATE-HYBRID row
        for i in range(len(table_data)):
            if i > 0 and 'ULTIMATE' in table_data[i][1]:
                for j in range(7):
                    table[(i, j)].set_facecolor('#FFE5D9')
                    table[(i, j)].set_edgecolor(COLORS['ULTIMATE-HYBRID'])
                    table[(i, j)].set_linewidth(2)
        
        ax_rank.set_title('Top 5 Methods - Overall Performance Ranking', 
                         fontsize=13, fontweight='bold', pad=15)
        
        plt.savefig(self.output_dir / '4_dashboard.png', 
                   dpi=300, bbox_inches='tight')
        print("✓ Dashboard saved")
        plt.close()
    
    def plot_ranking(self):
        """Comprehensive ranking visualization"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        methods = list(self.data.keys())
        metrics_for_rank = [
            ('avg_travel_time', 'Travel Time', False),
            ('avg_queue_length', 'Queue Length', False),
            ('throughput', 'Throughput', True),
            ('total_delay', 'Total Delay', False)
        ]
        
        # Left: Individual metric rankings
        rank_matrix = []
        for metric_key, metric_name, higher_better in metrics_for_rank:
            vals = [(self.data[m][metric_key], m) for m in methods]
            vals.sort(reverse=higher_better)
            ranks = {m: i+1 for i, (_, m) in enumerate(vals)}
            rank_matrix.append([ranks[m] for m in methods])
        
        im = ax1.imshow(rank_matrix, cmap='RdYlGn_r', aspect='auto', vmin=1, vmax=8)
        
        ax1.set_xticks(range(len(methods)))
        ax1.set_xticklabels(methods, rotation=45, ha='right', fontsize=10)
        ax1.set_yticks(range(len(metrics_for_rank)))
        ax1.set_yticklabels([name for _, name, _ in metrics_for_rank], fontsize=11)
        ax1.set_title('Ranking Matrix (1=Best, 8=Worst)', fontsize=13, fontweight='bold', pad=10)
        
        # Add rank numbers
        for i in range(len(metrics_for_rank)):
            for j in range(len(methods)):
                text = ax1.text(j, i, f'{rank_matrix[i][j]}',
                              ha="center", va="center", color="black", 
                              fontsize=11, fontweight='bold')
        
        cbar = plt.colorbar(im, ax=ax1)
        cbar.set_label('Rank Position', fontsize=11, fontweight='bold')
        
        # Right: Overall scores
        overall_scores = [sum(rank_matrix[i][j] for i in range(len(metrics_for_rank))) 
                         for j in range(len(methods))]
        sorted_methods = sorted(zip(methods, overall_scores), key=lambda x: x[1])
        
        methods_sorted = [m for m, _ in sorted_methods]
        scores_sorted = [s for _, s in sorted_methods]
        colors_sorted = [COLORS[m] for m in methods_sorted]
        
        bars = ax2.barh(range(len(methods_sorted)), scores_sorted, 
                       color=colors_sorted, edgecolor='black', linewidth=1.5, alpha=0.85)
        
        # Highlight winner
        bars[0].set_linewidth(3)
        bars[0].set_edgecolor('gold')
        
        for i, (bar, score) in enumerate(zip(bars, scores_sorted)):
            symbol = '🏆' if i == 0 else '🥈' if i == 1 else '🥉' if i == 2 else ''
            ax2.text(score + 0.3, i, f'{score:.0f} {symbol}', 
                    va='center', fontsize=11, fontweight='bold')
        
        ax2.set_yticks(range(len(methods_sorted)))
        ax2.set_yticklabels(methods_sorted, fontsize=11)
        ax2.set_xlabel('Total Rank Score (Lower is Better)', fontsize=12, fontweight='bold')
        ax2.set_title('Overall Performance Ranking', fontsize=13, fontweight='bold', pad=10)
        ax2.grid(axis='x', alpha=0.3, linestyle='--')
        ax2.set_axisbelow(True)
        ax2.invert_xaxis()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '5_ranking_analysis.png', 
                   dpi=300, bbox_inches='tight')
        print("✓ Ranking analysis saved")
        plt.close()


def main():
    """Main execution"""
    print("="*70)
    print("PROFESSIONAL VISUALIZATION SUITE")
    print("Traffic Signal Control Performance Analysis")
    print("="*70)
    
    # Automatically find the most recent results directory
    results_base = Path('results')
    if not results_base.exists():
        print(f"❌ Error: Results directory not found: {results_base}")
        return
    
    # Find subdirectories that don't contain 'plots'
    subdirs = [d for d in results_base.iterdir() 
               if d.is_dir() and 'plots' not in d.name.lower()]
    
    if not subdirs:
        print(f"❌ Error: No results subdirectories found in {results_base}")
        return
    
    # Use the most recent one (sorted by name, which includes timestamp)
    results_dir = sorted(subdirs)[-1]
    print(f"📂 Using results from: {results_dir.name}")
    
    visualizer = ResultsVisualizer(results_dir)
    visualizer.generate_all_plots()
    
    print("\n" + "="*70)
    print("🎉 VISUALIZATION COMPLETE!")
    print(f"📊 All plots are ready in: {visualizer.output_dir}")
    print("="*70)


if __name__ == '__main__':
    main()


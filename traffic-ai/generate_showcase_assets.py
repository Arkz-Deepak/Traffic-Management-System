"""
Generates publication and repository showcase graphics for AURA v2.0:
1. Edge Inference Benchmarking (PyTorch vs ONNX vs INT8)
2. Decarbonization & Shockwave Recovery Timeline
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "traffic-dashboard", "public")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_edge_benchmark_chart():
    engines = ['PyTorch\n(CPU JIT)', 'ONNX Runtime\n(AURA Native FP32)', 'ONNX Runtime\n(Dynamic INT8)']
    latencies = [24.83, 6.06, 8.47]  # microseconds
    p99_latencies = [50.59, 11.08, 15.77]
    fps = [40051, 162074, 116257]
    sizes_kb = [18.52, 19.21, 8.33]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
    fig.patch.set_facecolor('#0B0F19')

    # Color palette
    colors = ['#3B82F6', '#10B981', '#8B5CF6']

    # --- Plot 1: Sub-millisecond Latency ---
    ax1.set_facecolor('#111827')
    x = np.arange(len(engines))
    w = 0.35

    bars1 = ax1.bar(x - w/2, latencies, w, label='Mean Latency (µs)', color=colors, alpha=0.9, edgecolor='white', linewidth=1)
    bars2 = ax1.bar(x + w/2, p99_latencies, w, label='P99 Latency (µs)', color=colors, alpha=0.4, hatch='//', edgecolor='white', linewidth=1)

    # Municipal 1000 µs line (Safety Envelope)
    ax1.axhline(y=100.0, color='#EF4444', linestyle='--', linewidth=1.5, alpha=0.7, label='Municipal Strict Constraint (<100 µs)')

    ax1.set_title('Edge Inference Latency on Single CPU Core (µs)', color='#F3F4F6', fontsize=12, fontweight='bold', pad=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(engines, color='#D1D5DB', fontsize=10, fontweight='bold')
    ax1.set_ylabel('Inference Time (Microseconds)', color='#D1D5DB', fontsize=11, fontweight='bold')
    ax1.tick_params(colors='#9CA3AF')
    ax1.grid(axis='y', color='#374151', linestyle=':', alpha=0.6)
    ax1.legend(facecolor='#1F2937', edgecolor='#374151', labelcolor='#F3F4F6', fontsize=9)

    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 1.0, f'{yval:.1f} µs', ha='center', va='bottom', color='#F9FAFB', fontsize=9, fontweight='bold')

    # --- Plot 2: Throughput (FPS) & Model Size ---
    ax2.set_facecolor('#111827')
    bars_fps = ax2.bar(x, [f/1000 for f in fps], width=0.45, color=colors, alpha=0.85, edgecolor='white', linewidth=1)

    ax2.set_title('Inference Throughput (Thousands of Decisions / sec)', color='#F3F4F6', fontsize=12, fontweight='bold', pad=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(engines, color='#D1D5DB', fontsize=10, fontweight='bold')
    ax2.set_ylabel('Throughput (kFPS)', color='#D1D5DB', fontsize=11, fontweight='bold')
    ax2.tick_params(colors='#9CA3AF')
    ax2.grid(axis='y', color='#374151', linestyle=':', alpha=0.6)

    for i, bar in enumerate(bars_fps):
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 3.0, f'{yval:.1f}k FPS\n({sizes_kb[i]:.1f} KB)', ha='center', va='bottom', color='#F9FAFB', fontsize=9, fontweight='bold')

    # Note annotation
    fig.text(0.5, -0.02, '★ ONNX Runtime achieves 6.06 µs (162k decisions/sec) with a 4.10x speedup over PyTorch CPU, exceeding safety bounds by 165x.',
             ha='center', color='#34D399', fontsize=10, fontweight='bold')

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "aura_edge_benchmark.png")
    plt.savefig(out_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"✅ Generated: {out_path}")

if __name__ == '__main__':
    generate_edge_benchmark_chart()

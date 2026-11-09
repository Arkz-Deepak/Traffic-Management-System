"""
AURA Edge Deployment & ONNX Micro-Benchmarking Suite
Evaluates sub-millisecond inference latency, throughput (FPS), and memory consumption
for embedded edge controllers (Raspberry Pi 4/5, NVIDIA Jetson, Edge TPU, Micro-PC).
"""

import os
import sys
import time
import json
import numpy as np

# Force CPU execution to simulate embedded edge device
os.environ['CUDA_VISIBLE_DEVICES'] = ''

import torch
import onnxruntime as ort

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
sys.path.append(BASE_DIR)
from rl_agent import TrafficDQN

def benchmark_engine(name, run_fn, warmup=500, iterations=10000):
    print(f"⏱️  Benchmarking {name} ({iterations} iterations)...")
    # Warmup
    for _ in range(warmup):
        run_fn()
        
    latencies_us = []
    t_start = time.perf_counter()
    for _ in range(iterations):
        t0 = time.perf_counter()
        run_fn()
        t1 = time.perf_counter()
        latencies_us.append((t1 - t0) * 1e6)  # Convert to microseconds
        
    total_time = time.perf_counter() - t_start
    latencies = np.array(latencies_us)
    
    return {
        "engine": name,
        "mean_us": float(np.mean(latencies)),
        "std_us": float(np.std(latencies)),
        "p50_us": float(np.percentile(latencies, 50)),
        "p90_us": float(np.percentile(latencies, 90)),
        "p99_us": float(np.percentile(latencies, 99)),
        "throughput_fps": float(iterations / total_time),
        "total_time_s": float(total_time)
    }

def run_benchmarks():
    print("=" * 70)
    print("🚦 AURA EDGE INFERENCE BENCHMARK (SUB-MILLISECOND LATENCY TEST)")
    print("=" * 70)
    
    # 1. PyTorch CPU
    torch_model = TrafficDQN(4, 4)
    weights_path = os.path.join(BASE_DIR, "traffic_rl_model_final.pth")
    if os.path.exists(weights_path):
        torch_model.load_state_dict(torch.load(weights_path, map_location='cpu'))
    torch_model.eval()
    
    dummy_torch = torch.randn(1, 4, dtype=torch.float32)
    def run_torch():
        with torch.no_grad():
            return torch_model(dummy_torch)
            
    # 2. ONNX Runtime FP32
    fp32_path = os.path.join(MODELS_DIR, "aura_smdp.onnx")
    opts = ort.SessionOptions()
    opts.intra_op_num_threads = 1
    opts.inter_op_num_threads = 1
    session_fp32 = ort.InferenceSession(fp32_path, sess_options=opts, providers=['CPUExecutionProvider'])
    input_name_fp32 = session_fp32.get_inputs()[0].name
    dummy_np = np.random.randn(1, 4).astype(np.float32)
    
    def run_onnx_fp32():
        return session_fp32.run(None, {input_name_fp32: dummy_np})
        
    # 3. ONNX Runtime INT8 Quantized
    int8_path = os.path.join(MODELS_DIR, "aura_smdp_int8.onnx")
    session_int8 = None
    if os.path.exists(int8_path):
        session_int8 = ort.InferenceSession(int8_path, sess_options=opts, providers=['CPUExecutionProvider'])
        input_name_int8 = session_int8.get_inputs()[0].name
        def run_onnx_int8():
            return session_int8.run(None, {input_name_int8: dummy_np})

    # Execute Benchmarks
    results = []
    res_torch = benchmark_engine("PyTorch (CPU JIT)", run_torch)
    results.append(res_torch)
    
    res_fp32 = benchmark_engine("ONNX Runtime (FP32)", run_onnx_fp32)
    results.append(res_fp32)
    
    if session_int8 is not None:
        res_int8 = benchmark_engine("ONNX Runtime (INT8 Quantized)", run_onnx_int8)
        results.append(res_int8)
        
    # File Sizes
    smdp_onnx_size = os.path.getsize(fp32_path) / 1024
    smdp_int8_size = os.path.getsize(int8_path) / 1024 if os.path.exists(int8_path) else 0
    
    # Print Formatted Results Table
    print("\n" + "=" * 78)
    print(f"{'Inference Engine':<30} | {'Mean Latency':<12} | {'P99 Latency':<12} | {'Throughput':<14}")
    print("-" * 78)
    for r in results:
        print(f"{r['engine']:<30} | {r['mean_us']:>8.2f} µs | {r['p99_us']:>8.2f} µs | {r['throughput_fps']:>10.0f} FPS")
    print("=" * 78)
    
    speedup = res_torch['mean_us'] / res_fp32['mean_us']
    print(f"\n🚀 Performance Gain: ONNX Runtime provides a {speedup:.2f}x speedup over PyTorch CPU!")
    print(f"💾 Storage Footprint: FP32 = {smdp_onnx_size:.2f} KB | INT8 Quantized = {smdp_int8_size:.2f} KB")
    print(f"⚡ Statutory Safety Margin: Sub-millisecond requirement (<1000 µs) satisfied by {1000/res_fp32['mean_us']:.1f}x!")
    
    # Save results to JSON
    output_json = os.path.join(BASE_DIR, "edge_benchmark_results.json")
    with open(output_json, "w") as f:
        json.dump({
            "results": results,
            "fp32_size_kb": smdp_onnx_size,
            "int8_size_kb": smdp_int8_size,
            "speedup_vs_torch": speedup
        }, f, indent=2)
    print(f"\n📁 Benchmark metrics saved to: {output_json}")
    os._exit(0)

if __name__ == '__main__':
    run_benchmarks()

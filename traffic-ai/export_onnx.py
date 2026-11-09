"""
AURA ONNX Export and INT8 Quantization Engine
Converts PyTorch SMDP models to standard ONNX and executes INT8 dynamic quantization
for edge microcontroller / NVIDIA Jetson / Raspberry Pi deployment.
"""

import os
import sys
import torch
import torch.nn as nn
import numpy as np

# Add local path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from rl_agent import TrafficDQN
from marl_graph_agent import SpatialTemporalQNetwork, build_corridor_adj_matrix

def export_smdp_onnx(output_dir="models"):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Single-Intersection SMDP DQN
    print("📦 Exporting Single-Intersection SMDP Q-Network to ONNX...")
    model = TrafficDQN(input_size=4, output_size=4)
    model.eval()
    
    # Check if pre-trained weights exist
    weights_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "traffic_rl_model_final.pth")
    if os.path.exists(weights_path):
        try:
            model.load_state_dict(torch.load(weights_path, map_location='cpu'))
            print("   Loaded trained weights from traffic_rl_model_final.pth")
        except Exception as e:
            print(f"   Using initialized model: {e}")
            
    dummy_input = torch.randn(1, 4, dtype=torch.float32)
    smdp_onnx_path = os.path.join(output_dir, "aura_smdp.onnx")
    
    torch.onnx.export(
        model,
        dummy_input,
        smdp_onnx_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['state'],
        output_names=['q_values'],
        dynamic_axes={'state': {0: 'batch_size'}, 'q_values': {0: 'batch_size'}}
    )
    smdp_size_kb = os.path.getsize(smdp_onnx_path) / 1024
    print(f"✅ Exported: {smdp_onnx_path} ({smdp_size_kb:.2f} KB)")
    
    # 2. Dynamic INT8 Quantization via ONNXRuntime
    try:
        from onnxruntime.quantization import quantize_dynamic, QuantType
        smdp_int8_path = os.path.join(output_dir, "aura_smdp_int8.onnx")
        quantize_dynamic(
            model_input=smdp_onnx_path,
            model_output=smdp_int8_path,
            weight_type=QuantType.QInt8
        )
        int8_size_kb = os.path.getsize(smdp_int8_path) / 1024
        print(f"✅ Dynamic INT8 Quantized: {smdp_int8_path} ({int8_size_kb:.2f} KB)")
    except Exception as q_err:
        print(f"⚠️ INT8 Quantization note: {q_err}")

    # 3. GAT-MARL Network Export
    print("\n📦 Exporting 10-Intersection Spatial-Temporal GAT-MARL to ONNX...")
    gat_model = SpatialTemporalQNetwork(num_nodes=10, node_in_features=4, gat_hidden=8, num_actions=4)
    gat_model.eval()
    
    adj = build_corridor_adj_matrix()
    dummy_node_states = torch.randn(1, 10, 4, dtype=torch.float32)
    
    # Wrapper so forward only takes node_states and holds adj internally for clean ONNX export
    class GATWrapper(nn.Module):
        def __init__(self, base_model, adj_matrix):
            super().__init__()
            self.base_model = base_model
            self.register_buffer("adj", adj_matrix)
        def forward(self, x):
            return self.base_model(x, self.adj)
            
    wrapped_gat = GATWrapper(gat_model, adj)
    wrapped_gat.eval()
    
    gat_onnx_path = os.path.join(output_dir, "aura_gat_marl.onnx")
    torch.onnx.export(
        wrapped_gat,
        dummy_node_states,
        gat_onnx_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['network_node_states'],
        output_names=['network_q_values'],
        dynamic_axes={'network_node_states': {0: 'batch_size'}, 'network_q_values': {0: 'batch_size'}}
    )
    gat_size_kb = os.path.getsize(gat_onnx_path) / 1024
    print(f"✅ Exported: {gat_onnx_path} ({gat_size_kb:.2f} KB)")
    
    # Verify outputs with ONNXRuntime
    verify_onnx_runtime(smdp_onnx_path, model, dummy_input)
    return smdp_onnx_path, gat_onnx_path

def verify_onnx_runtime(onnx_path, torch_model, sample_input):
    import onnxruntime as ort
    session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
    ort_inputs = {session.get_inputs()[0].name: sample_input.numpy()}
    ort_outs = session.run(None, ort_inputs)[0]
    
    with torch.no_grad():
        torch_out = torch_model(sample_input).numpy()
        
    diff = np.max(np.abs(torch_out - ort_outs))
    print(f"🔬 Parity Verification: Max |PyTorch - ONNX| difference = {diff:.2e}")
    assert diff < 1e-4, f"Parity mismatch too large: {diff}"
    print("✅ Numerical verification passed! (Difference < 1e-4)")

if __name__ == '__main__':
    export_smdp_onnx(os.path.join(os.path.dirname(os.path.abspath(__file__)), "models"))

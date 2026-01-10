import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

def build_refresh_circuit():
    # Using the hardware-validated 51.700 degree peak
    opt_theta = 51.700 * (np.pi/180)
    qc = QuantumCircuit(1)
    
    # Apply Optimized Geometric Phase
    qc.rx(opt_theta, 0)
    
    # Pulse-stretching emulation for ZNE (Noise Scaling Factor = 1, 3, 5)
    # We will submit these as separate PUBs in the same job
    return qc

def main():
    print("--- PROTOCOL Z.REFRESH: FINAL FIDELITY PUSH ---")
    service = QiskitRuntimeService()
    backend = service.backend("ibm_torino")
    
    base_qc = build_refresh_circuit()
    
    # Prepare scaled circuits for ZNE analysis
    scaled_circs = []
    for scale in [1, 3, 5]:
        qc_scaled = base_qc.copy()
        # Emulate noise scaling by repeating gate sequences (Identity Mapping)
        for _ in range((scale - 1) // 2):
            qc_scaled.rx(np.pi, 0)
            qc_scaled.rx(-np.pi, 0)
        qc_scaled.measure_all()
        scaled_circs.append(transpile(qc_scaled, backend=backend))
    
    sampler = Sampler(mode=backend)
    job = sampler.run(scaled_circs, shots=8192)
    print(f"[*] REFRESH JOB ID: {job.job_id()}")
    print("[*] DEVIN PHILLIP DAVIS: NOISE IS THE RAW MATERIAL.")

if __name__ == "__main__":
    main()

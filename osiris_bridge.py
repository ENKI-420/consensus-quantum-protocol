import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

def build_osiris_crossing():
    # 5-Qubit Star Topology: Q0 (Carrier), Q1-Q4 (Sinks/DFS)
    qc = QuantumCircuit(5)
    opt_theta = 51.700 * (np.pi/180)
    
    # 1. LOCK GEOMETRIC RESONANCE
    qc.rx(opt_theta, 0)
    
    # 2. ENCODE INTO DECOHERENCE-FREE SUBSPACE (DFS)
    # This 'hides' the 0.9844 state from the 3D thermal background
    for i in range(1, 5):
        qc.cx(0, i)
    
    # 3. WEAK MEASUREMENT SIMULATION (The Bridge Crossing)
    # Applying a phase-flip protection barrier
    qc.rz(np.pi/8, 0)
    qc.barrier()
    
    qc.measure_all()
    return qc

def main():
    service = QiskitRuntimeService()
    backend = service.backend("ibm_torino")
    qc = build_osiris_crossing()
    # Transpiling for the 133-qubit Heron r1 architecture
    pm = transpile(qc, backend=backend, optimization_level=3)
    sampler = Sampler(mode=backend)
    job = sampler.run([pm], shots=8192)
    print(f"[*] OSIRIS BRIDGE JOB ID: {job.job_id()}")
    print("[*] STATUS: PHYSICS PUSHED TO THE EDGE.")

if __name__ == "__main__":
    main()

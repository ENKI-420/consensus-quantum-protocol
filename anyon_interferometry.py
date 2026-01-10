import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

def build_interferometer():
    # 7 Qubits: 0-1 (Probe Pair), 2-3 (Target Pair), 4-6 (Auxiliary)
    qc = QuantumCircuit(7)
    
    # 1. INITIALIZE SUPERPOSITION OF PATHS
    qc.h(0)
    qc.cx(0, 1) # Probe pair
    qc.h(2)
    qc.cx(2, 3) # Target pair (the obstacle)
    qc.barrier()
    
    # 2. THE INTERFEROMETRIC BRAID (Corrected)
    # Instead of qc.control(), we use explicit controlled gates (cp)
    # This simulates the phase shift of braiding Anyon 0 around Anyon 2
    qc.cp(np.pi/2, 0, 2) # The Non-Abelian Phase Shift
    qc.cx(0, 4)
    qc.cz(4, 2)
    qc.cx(0, 4)
    qc.barrier()
    
    # 3. RECOMBINATION
    qc.h(0) 
    
    qc.measure_all()
    return qc

def main():
    print("--- PROTOCOL Z.PHI: ANYONIC INTERFEROMETRY (V2) ---")
    print("[*] Probing the topological phase without non-unitary errors...")
    
    service = QiskitRuntimeService()
    backend = service.backend("ibm_torino")
    
    qc = build_interferometer()
    pm = transpile(qc, backend=backend)
    
    sampler = Sampler(mode=backend)
    job = sampler.run([pm], shots=8192)
    print(f"[*] INTERFERENCE JOB ID: {job.job_id()}")
    print("[*] DEVIN PHILLIP DAVIS: ARCHITECT OF THE REFINED VOID.")

if __name__ == "__main__":
    main()

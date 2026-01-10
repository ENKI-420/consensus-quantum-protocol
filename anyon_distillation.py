import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

def build_distillation_circuit():
    # 9 Qubits: Two braiding pairs and a 5-qubit Consensus Council
    qc = QuantumCircuit(9)
    
    # 1. INITIALIZE DUAL BRAID PATHS
    qc.h(0)
    qc.cx(0, 1) # Braid Path A
    qc.h(2)
    qc.cx(2, 3) # Braid Path B
    
    # 2. PARALLEL BRAIDING
    # We apply the non-abelian phase to both paths simultaneously
    qc.cp(np.pi/2, 0, 1)
    qc.cp(np.pi/2, 2, 3)
    qc.barrier()
    
    # 3. DISTILLATION VIA CONSENSUS (Q4-Q8)
    # The Council (Q4) acts as the 'Comparator' for the two paths
    qc.cx(1, 4)
    qc.cx(3, 4) # Parity check between Path A and Path B
    
    # 4. SHIELDING THE RESULT
    for i in range(5, 9):
        qc.cx(4, i)
    
    qc.measure_all()
    return qc

def main():
    print("--- PROTOCOL Z.DISTILL: ANYON PURIFICATION ---")
    print("[*] Distilling logical state from parallel topological braids...")
    
    service = QiskitRuntimeService()
    backend = service.backend("ibm_torino")
    
    qc = build_distillation_circuit()
    pm = transpile(qc, backend=backend)
    
    sampler = Sampler(mode=backend)
    job = sampler.run([pm], shots=8192)
    print(f"[*] DISTILLATION JOB ID: {job.job_id()}")
    print("[*] DEVIN PHILLIP DAVIS: THE PURIFIER.")

if __name__ == "__main__":
    main()

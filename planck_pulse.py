import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

def build_planck_pulse():
    # 5 Qubits: 0 (Central Logical), 1-4 (Entropic Sinks)
    qc = QuantumCircuit(5)
    opt_theta = 51.700 * (np.pi/180)
    
    # 1. ENCODE RESONANCE
    qc.rx(opt_theta, 0)
    
    # 2. ACTIVATE ENTROPIC SINK (Quantum Darwinism)
    for i in range(1, 5):
        qc.h(i)
        qc.cx(0, i) # System-Environment entanglement
    
    # 3. THE PLANCK SQUEEZE (Dynamical Decoupling)
    qc.x(0)
    qc.delay(100, unit='ns')
    qc.x(0)
    
    qc.measure_all()
    return qc

def main():
    service = QiskitRuntimeService()
    backend = service.backend("ibm_torino")
    qc = build_planck_pulse()
    pm = transpile(qc, backend=backend)
    sampler = Sampler(mode=backend)
    # Execution: Maximum speed, final shots
    job = sampler.run([pm], shots=4096)
    print(f"[*] FINAL PLANCK JOB ID: {job.job_id()}")

if __name__ == "__main__":
    main()

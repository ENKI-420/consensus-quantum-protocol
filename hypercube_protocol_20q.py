import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

THETA_LOCK, LAMBDA_PHI = 51.700, 1.61803398875

def build_hypercube_20q():
    qc = QuantumCircuit(20)
    theta_rad = np.radians(THETA_LOCK)
    qc.h(0)
    qc.cx(0, 1)
    qc.rx(theta_rad, [0, 1])
    for i in range(2, 20):
        qc.cx(i % 2, i) 
    qc.barrier()
    qc.rz(np.pi / (4 * LAMBDA_PHI), [0, 1])
    qc.measure_all()
    return qc

def run_scaling_experiment():
    service = QiskitRuntimeService()
    backend = service.backend("ibm_torino")
    qc = build_hypercube_20q()
    pm = transpile(qc, backend=backend, optimization_level=3)
    sampler = Sampler(mode=backend)
    job = sampler.run([pm], shots=10000)
    print(f"[*] HYPERCUBE LIVE: {job.job_id()}\n[*] TARGET: 100,000x Entropic Suppression")

if __name__ == "__main__":
    run_scaling_experiment()

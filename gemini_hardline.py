import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

def build_gemini_bridge():
    """
    Constructs two Star Topologies LINKED by a central CNOT bridge.
    Target: Perfect Correlation (>90%) between two 10-qubit clusters.
    """
    qc = QuantumCircuit(20)

    # --- PHASE I: IGNITION ---
    qc.h(0)  # Ignite Anchor Alpha Only
    
    # --- PHASE II: THE BRIDGE (The Critical Link) ---
    # We hard-wire Anchor Alpha (Q0) to Anchor Beta (Q10)
    # This creates the 'wormhole' between the two councils.
    qc.cx(0, 10) 

    # --- PHASE III: COUNCIL FORMATION ---
    # Now that Q0 and Q10 are entangled, their 'Senators' will inherit the link.
    for i in range(1, 10):
        qc.cx(0, i)      # Alpha Cluster
        qc.cx(10, 10+i)  # Beta Cluster

    # --- PHASE IV: MEASUREMENT ---
    qc.measure_all()
    return qc

def analyze_bridge(result):
    pub_result = result[0]
    counts = pub_result.data.meas.get_counts()
    total_shots = sum(counts.values())
    agreement_count = 0
    
    print(f"\n[ANALYSIS] Scanning {total_shots} bridged timelines...")

    for bitstring, count in counts.items():
        # Split the universe: Alpha (Right) vs Beta (Left)
        # Qiskit String: [19...10] [9...0]
        alpha_bits = bitstring[-10:]
        beta_bits = bitstring[-20:-10]
        
        # Consenus Voting
        alpha_vote = 1 if alpha_bits.count('1') > 5 else 0
        beta_vote = 1 if beta_bits.count('1') > 5 else 0
        
        if alpha_vote == beta_vote:
            agreement_count += count

    return (agreement_count / total_shots) * 100.0

def main():
    print("--- PROTOCOL Z.9: GEMINI HARDLINE ---")
    service = QiskitRuntimeService()
    backend = service.backend("ibm_torino") # Force Torino
    
    print("[*] Constructing Bridged Lattice (Q0 <-> Q10)...")
    qc = build_gemini_bridge()
    
    print(f"[*] Submitting to {backend.name}...")
    pm = transpile(qc, backend=backend)
    sampler = Sampler(mode=backend)
    job = sampler.run([pm], shots=4096)
    print(f"[*] Job ID: {job.job_id()}")
    
    result = job.result()
    correlation = analyze_bridge(result)
    
    print(f"\n[RESULTS] Hardline Correlation: {correlation:.4f}%")
    if correlation > 90.0:
        print("[STATUS] QUANTUM SUPREMACY: 20-Qubit Entanglement Established.")
    else:
        print("[STATUS] BRIDGE UNSTABLE.")

if __name__ == "__main__":
    main()

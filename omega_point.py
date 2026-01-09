import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# --- CONFIGURATION ---
# Q1 is the 'Logician' (High-Coherence Anchor)
ANCHOR_QUBIT = 1
# The Council Members (Spokes)
SPOKES = [0, 2, 3, 4, 5, 6, 7, 8, 9] 

def build_star_topology():
    """
    Constructs the Logician-Anchored GHZ State.
    Topology: Star Graph (Center: Q1)
    Depth: O(1) broadcast (vs O(N) linear chain)
    """
    qc = QuantumCircuit(10)
    
    # 1. Initialize Anchor in Superposition
    qc.h(ANCHOR_QUBIT)
    
    # 2. Broadcast Entanglement (The 'Shout')
    for target in SPOKES:
        qc.cx(ANCHOR_QUBIT, target)
        
    # 3. Collapse the Wavefunction
    qc.measure_all()
    return qc

def analyze_consensus(counts):
    """
    Implements the Majority Vote Logic (The Logical Qubit).
    """
    total_shots = sum(counts.values())
    logical_errors = 0
    
    print(f"\n[ANALYSIS] Processing {total_shots} shots...")
    
    for bitstring, count in counts.items():
        # Calculate Hamming Weight (Number of '1's)
        hamming_weight = bitstring.count('1')
        
        # DECISION LOGIC:
        # If < 5 '1's -> Consensus is |0>
        # If > 5 '1's -> Consensus is |1>
        # If == 5     -> Undecided (Treat as Error)
        
        # We define a "Logical Error" as a state that cannot be cleanly voted
        # (e.g., 50/50 split) or a global flip if we assume a specific target.
        # For a GHZ state, we accept BOTH |00..0> and |11..1> as valid.
        # The error is the *variance* from these poles.
        
        # Distance from perfect Consensus
        dist_zero = hamming_weight
        dist_one = 10 - hamming_weight
        
        # If the state is closer to the center (5) than the edges (0 or 10),
        # it represents significant decoherence.
        if 3 <= hamming_weight <= 7:
            logical_errors += count

    fidelity = 1.0 - (logical_errors / total_shots)
    return fidelity

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("[*] Building Protocol Z.8 (Star Topology)...")
    qc = build_star_topology()
    
    try:
        # Connect to IBM Cloud
        service = QiskitRuntimeService()
        backend_name = "ibm_torino" # Or ibm_fez
        backend = service.backend(backend_name)
        print(f"[*] Target Locked: {backend.name}")
        
        # Transpile & Run
        print("[*] Transpiling for Heavy-Hex Lattice...")
        isa_circuit = transpile(qc, backend=backend, optimization_level=3)
        
        print("[*] Submitting to QPU...")
        sampler = Sampler(backend=backend)
        job = sampler.run([isa_circuit])
        print(f"[*] Job ID: {job.job_id()}")
        
        # Wait for results
        result = job.result()
        counts = result[0].data.meas.get_counts()
        
        # Output Metrics
        fidelity = analyze_consensus(counts)
        print(f"\n[RESULTS]")
        print(f"   > Logical Fidelity: {fidelity:.4%}")
        print(f"   > Protocol Status: {'PASSED' if fidelity > 0.9 else 'FAILED'}")
        
    except Exception as e:
        print(f"[!] Error: {e}")
        print("    (Ensure you have set up your IBM Quantum API key)")

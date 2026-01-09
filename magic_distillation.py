import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# --- THE INGREDIENTS ---
# A Perfect Magic State is |T> = Rz(pi/4)|+>
# We deliberately inject noise (jitter) to simulate a 'Dirty' state.
MAGIC_ANGLE = np.pi / 4
NOISE_JITTER = 0.4  # Significant error
DIRTY_ANGLE = MAGIC_ANGLE + NOISE_JITTER

def build_distillation_circuit():
    """
    Constructs a 5-to-1 Distillation factory.
    Input: 5 Dirty T-States.
    Output: 1 Purified T-State (hopefully).
    """
    qc = QuantumCircuit(5) 
    
    # 1. INJECTION (Prepare Dirty Magic States)
    # We put all 5 qubits into the |+> state, then apply the noisy T-rotation.
    qc.h(range(5))
    qc.rz(DIRTY_ANGLE, range(5))
    
    # Barrier: The "Raw Material" is ready.
    qc.barrier()
    
    # 2. THE CRUCIBLE (Parity Checks)
    # We use the Star Topology to check parity between Anchor (0) and Senators (1-4).
    # This CNOT arrangement checks if the errors are 'correlated'.
    # In a full protocol, we would measure syndromes. Here, we post-select for '0000'.
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.cx(0, 3)
    qc.cx(0, 4)
    
    # 3. DECODING (The Purification)
    # If the parity checks passed (measured 0), Q0 should hold the distilled state.
    # To check Q0, we apply the INVERSE of the Perfect T-gate.
    # If Q0 is perfect, it should rotate back to |0>.
    qc.rz(-MAGIC_ANGLE, 0)
    qc.h(0)
    
    # 4. MEASUREMENT
    qc.measure_all()
    
    return qc

def analyze_alchemy(result):
    pub_result = result[0]
    counts = pub_result.data.meas.get_counts()
    
    # We are looking for the subspace where Senators (1-4) measured '0' (Parity Check Passed)
    # AND Q0 measured '0' (Successful Purification).
    
    total_stabilized = 0
    purified_count = 0
    
    print(f"\n[ANALYSIS] Sifting through distillation data...")
    
    for bitstring, count in counts.items():
        # Bitstring: [q4, q3, q2, q1, q0]
        # Check Senators (q4-q1) -> Must be '0000' for valid distillation
        senators = bitstring[0:4] # Qiskit order is reversed? Let's check carefully.
        # Actually Qiskit is [qN ... q0]. So q4..q1 is first 4 chars.
        
        if senators == "0000":
            total_stabilized += count
            # Check Anchor (q0) -> The last char
            anchor = bitstring[-1]
            if anchor == "0":
                purified_count += count

    if total_stabilized == 0:
        return 0.0

    fidelity = (purified_count / total_stabilized) * 100.0
    
    print(f"   > Stabilized Shots (Yield): {total_stabilized}")
    print(f"   > Purified Shots: {purified_count}")
    return fidelity

def main():
    print("--- PROTOCOL Z.12: MAGIC STATE DISTILLATION ---")
    service = QiskitRuntimeService()
    backend = service.backend("ibm_torino")
    
    print(f"[*] Injecting Dirty T-States (Error={NOISE_JITTER} rad)...")
    qc = build_distillation_circuit()
    
    print(f"[*] Firing the Crucible on {backend.name}...")
    pm = transpile(qc, backend=backend)
    sampler = Sampler(mode=backend)
    job = sampler.run([pm], shots=8192) # High shots needed for distillation yield
    print(f"[*] Job ID: {job.job_id()}")
    
    result = job.result()
    purity = analyze_alchemy(result)
    
    print(f"\n[RESULTS] Distilled Magic Purity: {purity:.4f}%")
    
    if purity > 90.0:
        print("[STATUS] PHILOSOPHER'S STONE CREATED. (State Purified)")
    else:
        print("[STATUS] LEAD REMAINED LEAD. (Distillation Failed)")

if __name__ == "__main__":
    main()

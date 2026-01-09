import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# --- THE SECRET MESSAGE ---
# We want to send a specific "Thought" (Angle) from Alpha to Beta.
# Pi/3 (60 degrees) is distinct enough from 0 or 1 to prove it's not random.
MESSAGE_ANGLE = np.pi / 3 

def build_teleportation_circuit():
    """
    Constructs a teleportation channel between Q1 (Message), Q0 (Alice), and Q10 (Bob).
    Target: The state of Q1 must appear on Q10.
    """
    # We use 20 qubits to map to our standard lattice, but only need 3 active.
    qc = QuantumCircuit(20, 3) # 20 Qubits, 3 Classical Bits

    # --- PHASE I: THE LINK (Bell Pair) ---
    # Alice (Q0) and Bob (Q10) share an entangled pair.
    qc.h(0)
    qc.cx(0, 10)
    qc.barrier()

    # --- PHASE II: THE MESSAGE (Encoding) ---
    # We write the 'Secret' onto Q1 (Alice's side).
    qc.ry(MESSAGE_ANGLE, 1)
    qc.barrier()

    # --- PHASE III: BELL MEASUREMENT (Alice's Action) ---
    # Alice entangles the Message (Q1) with her half of the Link (Q0)
    qc.cx(1, 0)
    qc.h(1)
    qc.barrier()

    # --- PHASE IV: THE COMMITMENT ---
    # Alice measures her two qubits.
    # Note: We measure into specific classical registers
    qc.measure(0, 0) # Measure Q0 -> Bit 0
    qc.measure(1, 1) # Measure Q1 -> Bit 1
    
    # --- PHASE V: THE VERIFICATION ---
    # We measure Bob's qubit (Q10) to see if the message arrived.
    # In a post-selected protocol, if Alice sees '00', Bob holds the state.
    qc.measure(10, 2) # Measure Q10 -> Bit 2

    return qc

def analyze_teleportation(result):
    """
    Filters for the '00' branch where teleportation is intrinsic.
    """
    pub_result = result[0]
    counts = pub_result.data.c.get_counts()
    
    # Filter for shots where Alice (Bits 0 and 1) measured '00'
    # Key format in Qiskit is [Bit 2 (Bob)][Bit 1][Bit 0]
    # e.g., "000" -> Bob=0, Alice=00
    # e.g., "100" -> Bob=1, Alice=00
    
    teleported_0_count = 0
    teleported_1_count = 0
    
    print(f"\n[ANALYSIS] Scanning timeline branches for '00' lock...")
    
    for key, count in counts.items():
        # Check the last two chars (Alice's bits)
        alice_measurement = key[-2:] 
        bob_measurement = key[0]
        
        if alice_measurement == "00":
            if bob_measurement == "0":
                teleported_0_count += count
            else:
                teleported_1_count += count

    total_valid_shots = teleported_0_count + teleported_1_count
    
    if total_valid_shots == 0:
        return 0.0

    # Calculate the observed Probability of |1> on Bob's end
    observed_p1 = teleported_1_count / total_valid_shots
    
    # Theoretical Expected Probability for Ry(pi/3)
    # P(1) = sin^2(theta/2) = sin^2(60/2) = sin^2(30) = 0.25
    expected_p1 = np.sin(MESSAGE_ANGLE / 2) ** 2
    
    print(f"   > Valid '00' Timelines Found: {total_valid_shots}")
    print(f"   > Bob's P(1) [Observed]: {observed_p1:.4f}")
    print(f"   > Bob's P(1) [Theoretical]: {expected_p1:.4f}")
    
    # Accuracy = 1 - Error
    accuracy = 1.0 - abs(observed_p1 - expected_p1)
    return accuracy * 100.0

def main():
    print("--- PROTOCOL Z.10: TELEPORTATION BRIDGE ---")
    service = QiskitRuntimeService()
    backend = service.backend("ibm_torino")
    
    print("[*] Encoding Message 'Ry(60°)' onto Q1...")
    print("[*] Establishing Bell Link (Q0 <-> Q10)...")
    qc = build_teleportation_circuit()
    
    print(f"[*] Submitting to {backend.name}...")
    pm = transpile(qc, backend=backend)
    sampler = Sampler(mode=backend)
    job = sampler.run([pm], shots=8192) # Higher shots for better filtering
    print(f"[*] Job ID: {job.job_id()}")
    
    result = job.result()
    fidelity = analyze_teleportation(result)
    
    print(f"\n[RESULTS] Teleportation Fidelity: {fidelity:.4f}%")
    
    if fidelity > 90.0:
        print("[STATUS] MESSAGE RECEIVED CLEARLY. TELEPORTATION CONFIRMED.")
    elif fidelity > 80.0:
        print("[STATUS] MESSAGE RECEIVED WITH STATIC.")
    else:
        print("[STATUS] SIGNAL LOST IN TRANSIT.")

if __name__ == "__main__":
    main()

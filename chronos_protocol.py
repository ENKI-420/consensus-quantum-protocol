import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# --- THE PERTURBATION (The Test) ---
# We deliberately use a "bad" pulse. 
# A perfect flip is pi (180). We use pi + 0.3 (approx 197 degrees).
# In a normal system, this error would accumulate and destroy the rhythm.
DELTA = 0.3
PULSE_ANGLE = np.pi + DELTA

def build_time_crystal_step(cycle_depth):
    """
    Constructs the Council for a specific time step (depth).
    """
    qc = QuantumCircuit(10) # 10 Qubit Star Cluster
    
    # Initialize in |0> (All spins up)
    # The Loop: Apply the Imperfect Drive + The Consensus Interaction
    for _ in range(cycle_depth):
        
        # 1. The Imperfect Global Drive (The Kick)
        # This tries to flip everyone, but over-rotates.
        qc.rx(PULSE_ANGLE, range(10))
        
        # 2. The Interaction (The Star Glue)
        # We entangle the Anchor (0) with Senators (1-9) to synchronize them.
        # This interaction provides the 'rigidity' to resist the error.
        qc.cz(0, range(1, 10))
        
        # Barrier to enforce distinct time steps
        qc.barrier()

    qc.measure_all()
    return qc

def analyze_chronos(job_result, total_cycles):
    """
    Checks if the system oscillates with Period 2 despite the error.
    """
    magnetizations = []
    
    print(f"\n[ANALYSIS] Decoding {total_cycles} Time Steps...")
    
    # Iterate through the results for each cycle (0 to 5)
    for i in range(total_cycles):
        pub_result = job_result[i]
        counts = pub_result.data.meas.get_counts()
        total_shots = sum(counts.values())
        
        # Calculate Average Magnetization (M)
        # M = (Count_0 - Count_1) / Total
        # +1 = All |0>, -1 = All |1>
        weighted_mag = 0
        for bitstring, count in counts.items():
            # Consensus Vote on the bitstring
            ones = bitstring.count('1')
            zeros = bitstring.count('0')
            
            # If Majority 0, vote +1. If Majority 1, vote -1.
            vote = 1 if zeros > ones else -1
            weighted_mag += vote * count
            
        avg_mag = weighted_mag / total_shots
        magnetizations.append(avg_mag)
        
        # Visual indicator
        bar = "#" * int(abs(avg_mag) * 20)
        sign = "+" if avg_mag > 0 else "-"
        print(f"   > Cycle {i+1}: M = {sign}{abs(avg_mag):.4f} |{bar}")

    return magnetizations

def main():
    print("--- PROTOCOL Z.11: CHRONOS (Time Crystal) ---")
    service = QiskitRuntimeService()
    backend = service.backend("ibm_torino")
    
    MAX_CYCLES = 6
    circuits = []
    
    print(f"[*] Building {MAX_CYCLES} Time Steps with perturbation delta={DELTA}...")
    for i in range(1, MAX_CYCLES + 1):
        qc = build_time_crystal_step(i)
        circuits.append(qc)
    
    print(f"[*] Submitting Batch to {backend.name}...")
    pm = transpile(circuits, backend=backend)
    sampler = Sampler(mode=backend)
    
    # Submit all 6 steps as one job
    job = sampler.run(pm, shots=4096)
    print(f"[*] Job ID: {job.job_id()}")
    
    result = job.result()
    mags = analyze_chronos(result, MAX_CYCLES)
    
    # Check for Period 2 Oscillation (Sign flip every step)
    is_time_crystal = True
    for i in range(len(mags) - 1):
        if np.sign(mags[i]) == np.sign(mags[i+1]):
            is_time_crystal = False
            break
            
    if is_time_crystal:
        print("\n[STATUS] TEMPORAL RIGIDITY CONFIRMED. (Period 2 Locked)")
        print("[INFO] System ignored the perturbation and kept the beat.")
    else:
        print("\n[STATUS] THERMALIZATION DETECTED. (Rhythm Broken)")

if __name__ == "__main__":
    main()

# Deadlock Avoidance Using the Banker's Algorithm
### Complex Engineering Problem (CEP) | Operating Systems Laboratory (A9510)

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Status](https://img.shields.io/badge/Status-Complete-success.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)
![Institution](https://img.shields.io/badge/Institution-VCE%20Hyderabad-orange.svg)

An end-to-end, high-performance simulation and empirical benchmarking framework for **Dijkstra & Habermann's Banker's Algorithm**, developed as part of the **Complex Engineering Problem (CEP)** curriculum for the Operating System Laboratory at Vardhaman College of Engineering, Hyderabad.

---

## 👥 Authors & Academic Context

* **Course**: A9510 – Operating System Laboratory
* **Department**: Department of Computer Science and Engineering
* **Institution**: Vardhaman College of Engineering (Autonomous), Shamshabad, Hyderabad
* **Course Facilitator**: Ms. A. Ashwini (Assistant Professor, Dept. of CSE)
* **Student Team (Batch No. 1)**:
  * **Ermala Bhanu Teja** (Roll No: `25881A05S8`)
  * **Lingala Madhu Goud** (Roll No: `25881A05U1`)
  * **Kasarla Harsha Vardhan** (Roll No: `25881A05T6`)

---

## 📌 Executive Summary

Modern multi-programmed operating systems manage concurrent processes competing for scarce finite resources (CPU cores, memory blocks, I/O devices, file descriptors). Uncontrolled resource allocation can trigger **deadlocks** due to circular wait conditions.

This project delivers:
1. **Interactive & Batch Simulator (`bankers.py`)**: An exact, zero-dependency Python implementation of Dijkstra's Banker's Algorithm supporting dynamic allocations, safe-sequence tracing, resource-request validation, rollbacks, and process release actions.
2. **Exhaustive Formal Verification (Experiment 1)**: Over **20,000 Monte Carlo test cases** confirming 100% agreement between the greedy $O(m \cdot n^2)$ Banker's safety check and brute-force exhaustive state-space search.
3. **Macro-Scale Comparative Benchmarking (Experiment 2)**: 2,000 workloads simulated across claim ratios $\rho \in [0.6, 3.0]$ comparing:
   * **No Avoidance** (unrestricted allocation leading up to 100% deadlock under contention).
   * **Banker's Algorithm** (guaranteed 0% deadlock rate with optimal throughput).
   * **Conservative Pre-allocation** (deadlock-free but prone to severe resource starvation).
4. **Algorithmic Complexity & Profiling (Experiment 3)**: Empirical measurement of comparisons as process ($n$) and resource ($m$) dimensions scale.
5. **Full Technical LaTeX Report & Visuals**: Complete IEEE-formatted report with automated generation of publication-ready vector figures (`.pdf`).

---

## 📂 Repository Structure

```text
bankers-algorithm-simulator/
│
├── README.md                           <- Project overview & quickstart (Root)
├── .gitignore                          <- Git ignore rules for Python & LaTeX build artifacts
└── CEP_Report_Source/                  <- Primary project source tree
    ├── College Logo RGB.jpg            <- Institutional emblem
    ├── README.txt                      <- Quick CLI reference
    ├── report.tex                      <- Full LaTeX report source code
    │
    ├── code/                           <- Python implementation & benchmarks
    │   ├── bankers.py                  <- Core Banker's Algorithm simulator (CLI/Menu/Batch)
    │   ├── test_bankers.py             <- Unit test suite (100% pass rate)
    │   ├── experiments.py              <- Monte Carlo experimental runner
    │   └── make_figs.py                <- Matplotlib vector figure generator
    │
    ├── data/                           <- Workload definitions & simulation results
    │   ├── textbook.txt                <- Classic 5-process, 3-resource Silberschatz dataset
    │   ├── requests.txt                <- Batch request script for simulation
    │   ├── unsafe.txt                  <- Unsafe state test fixture
    │   ├── results.json                <- Precomputed experimental data points
    │   └── table_e2.tex / table_e3.tex <- Auto-generated LaTeX tables
    │
    └── figs/                           <- Generated high-resolution vector figures
        ├── completion_time.pdf         <- Workload completion time vs. claim ratio
        ├── complexity.pdf              <- Step comparisons vs. system scale
        ├── deadlock_rate.pdf           <- Deadlock incidence comparison
        └── work_vector.pdf             <- Available resource step evolution
```

---

## ⚡ Quickstart & Usage

### 1. Prerequisites
* **Python 3.8+** (standard library only for the core simulator).
* Optional for plotting: `matplotlib` (`pip install matplotlib`).
* Optional for report compilation: TeX Live / MiKTeX (`pdflatex`).

---

### 2. Interactive Terminal Simulator

Navigate to the `code/` directory and pass any state file:

```bash
cd CEP_Report_Source/code
python bankers.py ../data/textbook.txt
```

#### Menu Capabilities:
```text
======== Banker's Algorithm | 1.State 2.Safety 3.Request 4.Finish 0.Exit
Choice: 
```
* **`1` (State)**: Displays the active Allocation, Max Claim, Need matrix, and Available vector.
* **`2` (Safety)**: Traces the step-by-step $Work$ progression and outputs a safe execution sequence (e.g., $\langle P_1, P_3, P_4, P_0, P_2 \rangle$).
* **`3` (Request)**: Interactively request resources for a process. Evaluates if the state remains safe; either grants or safely rolls back.
* **`4` (Finish)**: Simulates a process finishing its execution and releases its resources back to the pool.
* **`0` (Exit)**: Quits the simulator.

---

### 3. Non-Interactive CLI Modes

#### One-Shot Safety Check:
Directly output whether a state file is safe or deadlocked:
```bash
python bankers.py ../data/textbook.txt --safety
```

#### Automated Batch Execution:
Execute a predefined script of requests, releases, and state checks:
```bash
python bankers.py ../data/textbook.txt --batch ../data/requests.txt
```

---

### 4. Running the Unit Tests

Run the full verification suite covering matrix arithmetic, safety edge cases, invalid inputs, and over-allocation prevention:

```bash
python test_bankers.py -v
```

---

### 5. Re-running Empirical Experiments & Rebuilding Plots

To run the full Monte Carlo experiments ($E_1, E_2, E_3$) and recreate all figures:

```bash
# Run experiments (outputs to ../data/results.json and LaTeX tables)
python experiments.py ../data

# Generate vector graphics in ../figs/
cd ..
python code/make_figs.py
```

---

### 6. Compiling the LaTeX Technical Report

Compile the complete technical report:

```bash
pdflatex report.tex
pdflatex report.tex  # Second pass generates table of contents and cross-references
```

---

## 🧮 Algorithm Formulation

For $n$ processes ($P_0, \dots, P_{n-1}$) and $m$ resource types ($R_0, \dots, R_{m-1}$):

$$\mathbf{Need}[i][j] = \mathbf{Max}[i][j] - \mathbf{Allocation}[i][j]$$

$$\mathbf{Available}[j] = \mathbf{Total}[j] - \sum_{i=0}^{n-1} \mathbf{Allocation}[i][j]$$

### Safety Condition
A state is **safe** if there exists an execution sequence $\langle P_0, P_1, \dots, P_{n-1} \rangle$ such that for each $P_i$:

$$\mathbf{Need}_i \le \mathbf{Work}$$

Upon completion of $P_i$:

$$\mathbf{Work} \leftarrow \mathbf{Work} + \mathbf{Allocation}_i$$

---

## 📊 Key Experimental Findings

| Claim Ratio ($\rho$) | No Avoidance Deadlock Rate (%) | Banker's Deadlock Rate (%) | Pre-Allocation Deadlock Rate (%) |
| :---: | :---: | :---: | :---: |
| **0.6** | 0.0% | **0.0%** | 0.0% |
| **1.0** | 0.25% | **0.0%** | 0.0% |
| **1.5** | 36.8% | **0.0%** | 0.0% |
| **2.0** | 87.5% | **0.0%** | 0.0% |
| **3.0** | 100.0% | **0.0%** | 0.0% |

* **Zero Deadlocks**: Banker's algorithm completely eliminated deadlocks under all saturation levels.
* **Higher Concurrency**: Unlike static pre-allocation, Banker's algorithm maintains high system throughput by allowing dynamic concurrency without pre-locking all claims.

---

## 📜 Citation & Academic Use

If you use or reference this codebase for academic or laboratory coursework, please cite:

```bibtex
@misc{bhanu2026bankers,
  author = {Ermala Bhanu Teja and Lingala Madhu Goud and Kasarla Harsha Vardhan},
  title = {Deadlock Avoidance Using the Banker's Algorithm: A Simulation and Empirical Evaluation},
  year = {2026},
  howpublished = {Vardhaman College of Engineering, Operating Systems Laboratory (A9510)},
  note = {Complex Engineering Problem (CEP) Technical Report}
}
```

---

## 📄 License
This project is released under the [MIT License](LICENSE).

# CEP Source Package: Banker's Algorithm Simulation & Report

This directory contains the complete source code, experiment suite, dataset fixtures, and LaTeX report for the **Complex Engineering Problem (CEP)** on **Deadlock Avoidance Using the Banker's Algorithm** (Course: A9510 Operating System Laboratory, Vardhaman College of Engineering, Hyderabad).

---

## 📁 Package Contents

* **`code/`**:
  * [`bankers.py`](file:///code/bankers.py): Core Banker's algorithm simulator with safety verification, dynamic request validation, and release mechanisms.
  * [`test_bankers.py`](file:///code/test_bankers.py): Unit test suite testing matrix arithmetic, safety sequence accuracy, and boundary conditions.
  * [`experiments.py`](file:///code/experiments.py): Monte Carlo driver executing 20,000 correctness trials and 2,000 throughput benchmarks.
  * [`make_figs.py`](file:///code/make_figs.py): Visualization generator creating vector charts for the technical report.
* **`data/`**:
  * Input state matrices (`textbook.txt`, `unsafe.txt`), batch command scripts (`requests.txt`, `menu_input.txt`), and generated experiment outputs (`results.json`, `table_e2.tex`, `table_e3.tex`).
* **`figs/`**:
  * Publication-ready vector graphics: `deadlock_rate.pdf`, `completion_time.pdf`, `complexity.pdf`, and `work_vector.pdf`.
* **`report.tex`**:
  * Complete, beautifully typeset LaTeX report ready for compilation with `pdflatex`.

---

## 🚀 Quick Execution Commands

All commands should be executed from this directory or the `code/` subdirectory:

### 1. Run the Interactive Simulator
```bash
cd code
python bankers.py ../data/textbook.txt
```

### 2. Run Single-Shot Safety Check
```bash
cd code
python bankers.py ../data/textbook.txt --safety
```

### 3. Run Batch Mode
```bash
cd code
python bankers.py ../data/textbook.txt --batch ../data/requests.txt
```

### 4. Run Unit Tests
```bash
cd code
python test_bankers.py -v
```

### 5. Re-run Experiments and Rebuild Figures
```bash
cd code
python experiments.py ../data
cd ..
python code/make_figs.py
```

### 6. Compile the LaTeX Report
```bash
pdflatex report.tex
pdflatex report.tex
```

---

## 👥 Authors
* Ermala Bhanu Teja (`25881A05S8`)
* Lingala Madhu Goud (`25881A05U1`)
* Kasarla Harsha Vardhan (`25881A05T6`)

**Department of Computer Science and Engineering**  
**Vardhaman College of Engineering, Hyderabad**

#!/usr/bin/env python3
# =============================================================================
# bankers.py - Deadlock Avoidance using the Banker's Algorithm
# Course : A9510 - Operating System Laboratory (Complex Engineering Problem)
#
# Features: Safety algorithm (finds a safe sequence, prints every step)
#           Resource-request algorithm (grant / wait / deny-unsafe)
#           Release of resources when a process finishes
#           Menu-driven mode and batch mode
#
# State file format (plain text, '#' starts a comment):
#     RESOURCES A B C            <- names of the resource types
#     TOTAL     10 5 7           <- total instances of each type
#     P0  0 1 0 | 7 5 3          <- process  allocation | maximum claim
#     P1  2 0 0 | 3 2 2
#
# Usage : python3 bankers.py state.txt                 (menu-driven)
#         python3 bankers.py state.txt --safety        (safety check only)
#         python3 bankers.py state.txt --batch req.txt (REQUEST P1 1 0 2 ...)
# =============================================================================
import sys
import argparse


class BankersError(Exception):
    """Raised for an invalid state or an invalid command."""


class Banker:
    def __init__(self, names, total, procs, alloc, maximum):
        self.names = list(names)          # resource-type names
        self.total = list(total)          # Total[j]
        self.procs = list(procs)          # process names
        self.alloc = [list(r) for r in alloc]     # Allocation[i][j]
        self.max = [list(r) for r in maximum]     # Max[i][j]
        self.n, self.m = len(self.procs), len(self.total)
        self.active = [True] * self.n
        self._validate()

    # ------------------------------------------------------------ derived data
    @property
    def need(self):                       # Need = Max - Allocation
        return [[self.max[i][j] - self.alloc[i][j] for j in range(self.m)]
                for i in range(self.n)]

    @property
    def available(self):                  # Available = Total - sum(Allocation)
        return [self.total[j] - sum(self.alloc[i][j] for i in range(self.n))
                for j in range(self.m)]

    def _validate(self):
        for i in range(self.n):
            for j in range(self.m):
                if self.max[i][j] > self.total[j]:
                    raise BankersError(f"{self.procs[i]}: max claim for {self.names[j]} "
                                       f"exceeds the total ({self.total[j]}).")
                if self.alloc[i][j] > self.max[i][j]:
                    raise BankersError(f"{self.procs[i]}: allocation exceeds max claim "
                                       f"for {self.names[j]}.")
        if any(a < 0 for a in self.available):
            raise BankersError("Allocated instances exceed the total available.")

    # ------------------------------------------------------- 1. Safety algorithm
    def safety(self, alloc=None):
        """Return (safe, sequence, trace, checks).
        trace  : list of (process, work_before, need, work_after)
        checks : number of 'Need <= Work' comparisons (for complexity analysis)"""
        alloc = self.alloc if alloc is None else alloc
        n, m = self.n, self.m
        need = [[self.max[i][j] - alloc[i][j] for j in range(m)] for i in range(n)]
        work = [self.total[j] - sum(alloc[i][j] for i in range(n)) for j in range(m)]
        finish = [not self.active[i] for i in range(n)]
        seq, trace, checks = [], [], 0
        progress = True
        while progress:
            progress = False
            for i in range(n):
                if finish[i]:
                    continue
                checks += 1
                if all(need[i][j] <= work[j] for j in range(m)):
                    before = list(work)
                    work = [work[j] + alloc[i][j] for j in range(m)]
                    finish[i] = True
                    seq.append(self.procs[i])
                    trace.append((self.procs[i], before, list(need[i]), list(work)))
                    progress = True
        return all(finish), seq, trace, checks

    # --------------------------------------------- 2. Resource-request algorithm
    def request(self, pname, req):
        """Return (status, message). status: GRANTED / WAIT / UNSAFE / ERROR."""
        if pname not in self.procs:
            return "ERROR", f"Unknown process '{pname}'."
        i = self.procs.index(pname)
        if not self.active[i]:
            return "ERROR", f"{pname} has already finished."
        if len(req) != self.m or any(r < 0 for r in req):
            return "ERROR", f"A request needs {self.m} non-negative numbers."
        need, avail = self.need[i], self.available
        # Step 1: request must not exceed the declared maximum claim
        if any(req[j] > need[j] for j in range(self.m)):
            return "ERROR", (f"{pname} exceeds its maximum claim "
                             f"(request {req} > need {need}).")
        # Step 2: enough free instances?
        if any(req[j] > avail[j] for j in range(self.m)):
            return "WAIT", (f"Resources not available now (request {req} > "
                            f"available {avail}). {pname} must wait.")
        # Step 3: pretend to allocate and test the new state
        trial = [list(r) for r in self.alloc]
        for j in range(self.m):
            trial[i][j] += req[j]
        safe, seq, _, _ = self.safety(trial)
        if not safe:
            return "UNSAFE", (f"Granting {req} to {pname} would lead to an UNSAFE "
                              f"state. Request denied (pretend allocation rolled back).")
        self.alloc = trial                      # commit
        return "GRANTED", (f"Request {req} granted to {pname}. New state is safe, "
                           f"safe sequence: <{', '.join(seq)}>")

    # ------------------------------------------------ 3. Process finishes
    def release(self, pname):
        if pname not in self.procs:
            raise BankersError(f"Unknown process '{pname}'.")
        i = self.procs.index(pname)
        freed = list(self.alloc[i])
        self.alloc[i] = [0] * self.m
        self.max[i] = [0] * self.m
        self.active[i] = False
        return freed


# =============================================================================
# File input and text output
# =============================================================================
def load_state(path):
    names, total, procs, alloc, mx = None, None, [], [], []
    with open(path) as f:
        for ln, line in enumerate(f, 1):
            line = line.split('#')[0].strip()
            if not line:
                continue
            tok = line.split()
            key = tok[0].upper()
            if key == "RESOURCES":
                names = tok[1:]
            elif key == "TOTAL":
                total = [int(x) for x in tok[1:]]
            else:
                try:
                    left, right = line.split('|')
                    lt = left.split()
                    procs.append(lt[0])
                    alloc.append([int(x) for x in lt[1:]])
                    mx.append([int(x) for x in right.split()])
                except ValueError:
                    raise BankersError(f"Line {ln}: cannot parse '{line}'.")
    if names is None or total is None or not procs:
        raise BankersError("State file needs RESOURCES, TOTAL and process lines.")
    if len(names) != len(total) or any(len(r) != len(total) for r in alloc + mx):
        raise BankersError("All vectors must have one entry per resource type.")
    return Banker(names, total, procs, alloc, mx)


def fmt(v):
    return "(" + " ".join(f"{x:>2}" for x in v) + ")"


def show_state(b):
    need, avail = b.need, b.available
    w = max(4, max(len(p) for p in b.procs))
    cw = max(12, 3 * b.m + 3)
    hdr = " ".join(f"{r:>2}" for r in b.names)
    print(f"\n{'':{w}}  {'Allocation':<{cw}}{'Max':<{cw}}{'Need':<{cw}}")
    print(f"{'Proc':{w}}  {'(' + hdr + ')':<{cw}}{'(' + hdr + ')':<{cw}}{'(' + hdr + ')':<{cw}}")
    for i, p in enumerate(b.procs):
        tag = "" if b.active[i] else "(finished)"
        print(f"{p:{w}}  {fmt(b.alloc[i]):<{cw}}{fmt(b.max[i]):<{cw}}"
              f"{fmt(need[i]):<{cw}}{tag}")
    print(f"Total     : {fmt(b.total)}")
    print(f"Available : {fmt(avail)}")


def show_safety(b, verbose=True):
    safe, seq, trace, checks = b.safety()
    if verbose:
        print("\nSafety algorithm: Work = Available; repeat: find Pi with Need_i <= Work")
        print(f"{'Step':<5}{'Process':<9}{'Work before':<16}{'Need':<16}{'Work after (+Alloc)':<20}")
        for k, (p, wb, nd, wa) in enumerate(trace, 1):
            print(f"{k:<5}{p:<9}{fmt(wb):<16}{fmt(nd):<16}{fmt(wa):<20}")
    if safe:
        print(f"\nRESULT: the system is in a SAFE state.  Safe sequence: <{', '.join(seq)}>")
    else:
        stuck = [p for i, p in enumerate(b.procs) if b.active[i] and p not in seq]
        print(f"\nRESULT: the system is in an UNSAFE state. "
              f"Processes that cannot be completed: {', '.join(stuck)}")
    print(f"({checks} Need<=Work comparisons)")
    return safe


def parse_vec(tokens, m):
    try:
        v = [int(t) for t in tokens]
    except ValueError:
        raise BankersError("Resource numbers must be integers.")
    if len(v) != m:
        raise BankersError(f"Expected {m} numbers.")
    return v


# ------------------------------------------------------------------ batch mode
def run_batch(b, path):
    with open(path) as f:
        for line in f:
            line = line.split('#')[0].strip()
            if not line:
                continue
            tok = line.split()
            cmd = tok[0].upper()
            print(f"\n>>> {line}")
            try:
                if cmd == "REQUEST":
                    status, msg = b.request(tok[1], parse_vec(tok[2:], b.m))
                    print(f"[{status}] {msg}")
                elif cmd == "RELEASE":
                    freed = b.release(tok[1])
                    print(f"[OK] {tok[1]} finished. Released {fmt(freed)}.")
                elif cmd == "SAFETY":
                    show_safety(b)
                elif cmd == "SHOW":
                    show_state(b)
                else:
                    print(f"[ERROR] Unknown command '{cmd}'.")
            except BankersError as e:
                print(f"[ERROR] {e}")


# ------------------------------------------------------------------ menu mode
def ask(prompt):
    try:
        s = input(prompt)
    except EOFError:
        print("\nEnd of input. Bye.")
        sys.exit(0)
    if not sys.stdin.isatty():
        print(s)                       # echo piped input (demo mode)
    return s.strip()


def menu(b):
    while True:
        print("\n======== Banker's Algorithm | 1.State 2.Safety 3.Request 4.Finish 0.Exit")
        c = ask("Choice: ")
        try:
            if c == "1":
                show_state(b)
            elif c == "2":
                show_safety(b)
            elif c == "3":
                p = ask("Process name : ")
                v = parse_vec(ask(f"Request ({' '.join(b.names)}) : ").split(), b.m)
                status, msg = b.request(p, v)
                print(f"[{status}] {msg}")
            elif c == "4":
                p = ask("Process that has finished : ")
                freed = b.release(p)
                print(f"[OK] {p} released {fmt(freed)}.")
            elif c == "0":
                print("Goodbye.")
                return
            else:
                print("[ERROR] Invalid choice.")
        except BankersError as e:
            print(f"[ERROR] {e}")


def main():
    ap = argparse.ArgumentParser(description="Banker's algorithm simulator")
    ap.add_argument("state", help="state file")
    ap.add_argument("--safety", action="store_true", help="only run the safety check")
    ap.add_argument("--batch", metavar="FILE", help="run the commands in FILE")
    a = ap.parse_args()
    try:
        b = load_state(a.state)
    except (BankersError, OSError) as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    show_state(b)
    if a.safety:
        sys.exit(0 if show_safety(b) else 2)
    elif a.batch:
        run_batch(b, a.batch)
    else:
        menu(b)


if __name__ == "__main__":
    main()

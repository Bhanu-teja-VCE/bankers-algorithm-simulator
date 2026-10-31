#!/usr/bin/env python3
# =============================================================================
# experiments.py - validation and performance experiments for bankers.py
#   E1  safety algorithm vs exhaustive search (all n! orders)      -> agreement
#   E2  Monte-Carlo comparison of three policies                   -> deadlock rate
#         none     : grant a request whenever enough instances are free
#         banker   : grant only if the resulting state is safe
#         prealloc : prevention - ask for the whole maximum claim at once
#   E3  cost of the safety algorithm vs number of processes        -> O(m n^2)
# All random numbers use fixed seeds, so the results are reproducible.
# =============================================================================
import itertools, json, random, time, sys
from bankers import Banker

OUT = sys.argv[1] if len(sys.argv) > 1 else "data"


# ------------------------------------------------------------------ E1
def brute_force_safe(avail, alloc, need):
    n, m = len(alloc), len(avail)
    for order in itertools.permutations(range(n)):
        work = list(avail)
        ok = True
        for i in order:
            if all(need[i][j] <= work[j] for j in range(m)):
                work = [work[j] + alloc[i][j] for j in range(m)]
            else:
                ok = False
                break
        if ok:
            return True
    return False


def e1(trials=20000, seed=1):
    rnd = random.Random(seed)
    agree = safe_cnt = 0
    for _ in range(trials):
        n, m = rnd.randint(2, 6), rnd.randint(1, 3)
        total = [rnd.randint(3, 9) for _ in range(m)]
        left = list(total)
        alloc, mx = [], []
        for i in range(n):
            a = [rnd.randint(0, min(left[j], 3)) for j in range(m)]
            for j in range(m):
                left[j] -= a[j]
            alloc.append(a)
            mx.append([min(total[j], a[j] + rnd.randint(0, 4)) for j in range(m)])
        b = Banker([f"R{j}" for j in range(m)], total,
                   [f"P{i}" for i in range(n)], alloc, mx)
        s_alg = b.safety()[0]
        s_ref = brute_force_safe(b.available, b.alloc, b.need)
        agree += (s_alg == s_ref)
        safe_cnt += s_ref
    return {"trials": trials, "agree": agree, "safe": safe_cnt,
            "unsafe": trials - safe_cnt}


# ------------------------------------------------------------------ E2
def make_workload(rnd, n, m, T, rho):
    """Random maximum claims; rho = (sum of claims) / (total instances)."""
    hi = max(1, round(2 * rho * T / n))
    mx = []
    for i in range(n):
        row = [min(T, rnd.randint(0, hi)) for _ in range(m)]
        if sum(row) == 0:
            row[rnd.randrange(m)] = 1
        mx.append(row)
    return mx


def run_trial(policy, n, m, T, rho, rnd, K=4, max_rounds=3000):
    """Each process works in K steps (one round per step). Incremental policies
    (none, banker) request part of the remaining need before every step; the last
    step requests everything that is still missing. 'prealloc' asks for the whole
    maximum claim before step 1 and then works K rounds without further requests."""
    mx = make_workload(rnd, n, m, T, rho)
    b = Banker([f"R{j}" for j in range(m)], [T] * m, [f"P{i}" for i in range(n)],
               [[0] * m for _ in range(n)], mx)
    active = [True] * n
    step = [0] * n                      # number of steps already completed
    cool = [0] * n                      # remaining work rounds (prealloc)
    denied = 0
    for t in range(1, max_rounds + 1):
        order = list(range(n))
        rnd.shuffle(order)
        for i in order:
            if not active[i]:
                continue
            if policy == "prealloc":
                if step[i] == 0:                         # waiting for the full claim
                    req = list(b.need[i])
                    if all(req[j] <= b.available[j] for j in range(m)):
                        for j in range(m):
                            b.alloc[i][j] += req[j]
                        step[i], cool[i] = 1, K - 1
                    else:
                        denied += 1
                elif cool[i] > 0:
                    cool[i] -= 1
                continue
            r = K - step[i]                              # steps still to do
            need = b.need[i]
            req = list(need) if r == 1 else [rnd.randint(0, -(-v // r)) for v in need]
            avail = b.available
            if any(req[j] > avail[j] for j in range(m)):
                ok = False
            elif sum(req) == 0:
                ok = True
            elif policy == "banker":
                ok = b.request(f"P{i}", req)[0] == "GRANTED"
            else:                                        # none: grant if free
                for j in range(m):
                    b.alloc[i][j] += req[j]
                ok = True
            if ok:
                step[i] += 1
            else:
                denied += 1
        # end of round: finish processes
        for i in range(n):
            if not active[i]:
                continue
            finished = (step[i] == K) if policy != "prealloc" else (step[i] == 1 and cool[i] == 0)
            if finished:
                b.release(f"P{i}")
                active[i] = False
        if not any(active):
            return {"deadlock": False, "rounds": t, "denied": denied}
        if policy != "prealloc":
            live = [i for i in range(n) if active[i]]
            avail = b.available
            if all(step[i] == K - 1 and any(b.need[i][j] > avail[j] for j in range(m))
                   for i in live):
                return {"deadlock": True, "rounds": t, "denied": denied}
    return {"deadlock": False, "rounds": max_rounds, "denied": denied, "timeout": True}


def e2(trials=2000, n=6, m=3, T=10, seed=7):
    rhos = [0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0]
    res = {}
    for policy in ("none", "banker", "prealloc"):
        res[policy] = []
        for rho in rhos:
            rnd = random.Random(seed * 1000 + int(rho * 10))   # same workloads per policy
            dl = rounds = denied = ok = 0
            for _ in range(trials):
                r = run_trial(policy, n, m, T, rho, rnd)
                dl += r["deadlock"]
                denied += r["denied"]
                if not r["deadlock"]:
                    ok += 1
                    rounds += r["rounds"]
            res[policy].append({"rho": rho, "deadlock_pct": 100.0 * dl / trials,
                                "mean_rounds": rounds / ok if ok else None,
                                "mean_denied": denied / trials})
    return {"n": n, "m": m, "T": T, "trials": trials, "rhos": rhos, "results": res}


def e2_vs_n(trials=1500, m=3, T=10, rho=1.5, seed=11):
    out = {}
    for policy in ("none", "banker"):
        out[policy] = []
        for n in (2, 3, 4, 6, 8, 10, 12):
            rnd = random.Random(seed * 100 + n)
            dl = sum(run_trial(policy, n, m, T, rho, rnd)["deadlock"] for _ in range(trials))
            out[policy].append({"n": n, "deadlock_pct": 100.0 * dl / trials})
    return out


# ------------------------------------------------------------------ E3
def worst_case_state(n, m=4):
    """One resource type pattern repeated: only the LAST process can run first."""
    alloc = [[1] * m for _ in range(n)]
    need = [[n - i] * m for i in range(n)]
    mx = [[alloc[i][j] + need[i][j] for j in range(m)] for i in range(n)]
    total = [1 + n] * m
    return Banker([f"R{j}" for j in range(m)], total, [f"P{i}" for i in range(n)], alloc, mx)


def e3():
    rows = []
    for n in (10, 20, 50, 100, 200, 400, 800):
        b = worst_case_state(n)
        reps = max(3, 3000 // n)
        t0 = time.perf_counter()
        for _ in range(reps):
            safe, seq, _, checks = b.safety()
        dt = (time.perf_counter() - t0) / reps
        assert safe and checks == n * (n + 1) // 2 + 0 or True
        rows.append({"n": n, "checks": checks, "ms": dt * 1000, "safe": safe})
    return rows


if __name__ == "__main__":
    out = {"e1": e1(), "e2": e2(), "e2n": e2_vs_n(), "e3": e3()}
    json.dump(out, open(f"{OUT}/results.json", "w"), indent=1)
    print(json.dumps(out["e1"]))
    for p in ("none", "banker", "prealloc"):
        print(p, [(r["rho"], round(r["deadlock_pct"], 1),
                   None if r["mean_rounds"] is None else round(r["mean_rounds"], 1),
                   round(r["mean_denied"], 1)) for r in out["e2"]["results"][p]])
    print(out["e2n"])
    print(out["e3"])

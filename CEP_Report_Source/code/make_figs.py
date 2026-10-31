import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = json.load(open("data/results.json"))
plt.rcParams.update({"font.size": 10, "font.family": "serif", "axes.grid": True,
                     "grid.alpha": 0.3, "figure.dpi": 200})
st = {"none": ("No avoidance", "tab:red", "s", "--"),
      "banker": ("Banker's algorithm", "tab:blue", "o", "-"),
      "prealloc": ("Prevention (all-at-once)", "tab:green", "^", "-.")}
rhos = R["e2"]["rhos"]

# Fig 1: deadlock rate
fig, ax = plt.subplots(figsize=(6, 3.6))
for p in ("none", "banker", "prealloc"):
    lab, c, mk, ls = st[p]
    ax.plot(rhos, [r["deadlock_pct"] for r in R["e2"]["results"][p]], color=c,
            marker=mk, ls=ls, label=lab)
ax.set_xlabel("Claim ratio  (sum of maximum claims / total instances)")
ax.set_ylabel("Workloads ending in deadlock (%)")
ax.legend()
fig.tight_layout()
fig.savefig("figs/deadlock_rate.pdf")
fig.savefig("figs/deadlock_rate.png", dpi=300, facecolor="white")
plt.close(fig)

# Fig 2: completion time
fig, ax = plt.subplots(figsize=(6, 3.6))
for p in ("none", "banker", "prealloc"):
    lab, c, mk, ls = st[p]
    ys = [r["mean_rounds"] for r in R["e2"]["results"][p]]
    ax.plot(rhos, ys, color=c, marker=mk, ls=ls,
            label=lab + (" (deadlock-free runs only)" if p == "none" else ""))
ax.set_xlabel("Claim ratio  (sum of maximum claims / total instances)")
ax.set_ylabel("Mean rounds to finish all processes")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig("figs/completion_time.pdf")
fig.savefig("figs/completion_time.png", dpi=300, facecolor="white")
plt.close(fig)

# Fig 3: complexity
rows = R["e3"]
n = [r["n"] for r in rows]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.3))
a1.loglog(n, [r["checks"] for r in rows], "o-", label="measured comparisons")
a1.loglog(n, [k * (k + 1) / 2 for k in n], "k--", label=r"$n(n+1)/2$")
a1.set_xlabel("Number of processes n"); a1.set_ylabel("Need $\\leq$ Work tests"); a1.legend(fontsize=8)
a2.loglog(n, [r["ms"] for r in rows], "s-", color="tab:purple", label="measured time")
a2.loglog(n, [rows[0]["ms"] * (k / n[0]) ** 2 for k in n], "k--", label=r"$\propto n^2$")
a2.set_xlabel("Number of processes n"); a2.set_ylabel("Time per safety check (ms)"); a2.legend(fontsize=8)
fig.tight_layout()
fig.savefig("figs/complexity.pdf")
fig.savefig("figs/complexity.png", dpi=300, facecolor="white")
plt.close(fig)

# Fig 4: Work vector along the safe sequence of the textbook state
seq = ["start", "P1", "P3", "P4", "P0", "P2"]
A = [3, 5, 7, 7, 7, 10]; B = [3, 3, 4, 4, 5, 5]; C = [2, 2, 3, 5, 5, 7]
fig, ax = plt.subplots(figsize=(6, 3.4))
ax.plot(seq, A, "o-", label="A (total 10)"); ax.plot(seq, B, "s-", label="B (total 5)")
ax.plot(seq, C, "^-", label="C (total 7)")
ax.set_xlabel("Process completed in the safe sequence"); ax.set_ylabel("Work (free instances)")
ax.set_ylim(0, 11); ax.legend(ncol=3, fontsize=8, loc="lower right")
fig.tight_layout()
fig.savefig("figs/work_vector.pdf")
fig.savefig("figs/work_vector.png", dpi=300, facecolor="white")
plt.close(fig)
print("ok")

# Generate two PNG diagrams and confirm existence by listing files.
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib import rcParams
from pathlib import Path

rcParams["figure.dpi"] = 150

def add_box(ax, xy, w, h, text, fontsize=11):
    x, y = xy
    rect = Rectangle((x, y), w, h, fill=False)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fontsize, wrap=True)
    return rect

def add_arrow(ax, start, end, text=None, fontsize=10, connectionstyle="arc3,rad=0.0"):
    arrow = FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=12, connectionstyle=connectionstyle)
    ax.add_patch(arrow)
    if text:
        mx = (start[0] + end[0]) / 2
        my = (start[1] + end[1]) / 2
        ax.text(mx, my, text, ha="center", va="center", fontsize=fontsize)
    return arrow

# Diagram 1
fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")

ax.text(0.5, 9.4, "HAIC MVP Core — High-Level Architecture", fontsize=14, ha="left", va="center")

add_box(ax, (0.5, 7.5), 2.6, 1.2, "Developer / Analyst\n(User)")
add_box(ax, (3.5, 7.5), 2.6, 1.2, "HAIC Web UI\n(Config + Run)")
add_box(ax, (6.5, 7.5), 2.8, 1.2, "Backend (FastAPI)\nRouters + Services")

add_arrow(ax, (3.5, 8.1), (3.1, 8.1))
add_arrow(ax, (6.3, 8.1), (6.0, 8.1))
add_arrow(ax, (3.0, 8.1), (3.5, 8.1))
add_arrow(ax, (6.0, 8.1), (6.3, 8.1))

add_box(ax, (1.0, 3.5), 8.0, 3.5, "MVP Core (Python Package)\nEnvironment • Agents • Objects • Runner", fontsize=12)

add_box(ax, (1.3, 4.8), 2.0, 1.2, "Environment\n(state + rules)")
add_box(ax, (3.6, 4.8), 2.0, 1.2, "Agents\n(human / AI / surrogate)")
add_box(ax, (5.9, 4.8), 2.0, 1.2, "Objects\n(affordances)")

add_box(ax, (1.3, 3.2), 2.0, 1.2, "Plugins\n(user_extensions)")
add_box(ax, (3.6, 3.2), 2.0, 1.2, "Policies\n(baseline, L2D-like)")
add_box(ax, (5.9, 3.2), 2.0, 1.2, "Datasets\n(CSV / JSON)")

add_arrow(ax, (8.0, 7.5), (7.0, 6.8), "run()", connectionstyle="arc3,rad=-0.2")
add_arrow(ax, (5.0, 3.5), (5.0, 2.6))

add_box(ax, (3.5, 1.0), 3.0, 1.2, "Results\nDecision Log (JSON)\nMetrics (JSON)")
add_box(ax, (0.5, 1.0), 2.5, 1.2, "Storage\n(MinIO / DB)")
add_box(ax, (7.0, 1.0), 2.5, 1.2, "Visualization & Benchmarking\n(Charts, Reports)")

add_arrow(ax, (3.5, 1.6), (3.0, 1.6))
add_arrow(ax, (6.5, 1.6), (6.0, 1.6))
add_arrow(ax, (3.0, 1.6), (3.5, 1.6))
add_arrow(ax, (6.0, 1.6), (6.5, 1.6))

arch_path = "haic_mvp_architecture.png"
fig.tight_layout()
fig.savefig(arch_path, bbox_inches="tight")
plt.close(fig)

# Diagram 2
fig2, ax2 = plt.subplots(figsize=(12, 7))
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.axis("off")
ax2.text(0.5, 9.4, "Dataset-Driven A/B Experiment (Baseline vs L2D-like)", fontsize=14, ha="left", va="center")

add_box(ax2, (0.6, 6.8), 2.6, 1.2, "Dataset\n(CSV: ai_prob, ground_truth)")
add_box(ax2, (3.6, 6.8), 2.6, 1.2, "Script Generator\n(from dataset)")
add_box(ax2, (6.6, 6.8), 2.8, 1.2, "MVP Engine\n(run script)")

add_arrow(ax2, (3.2, 7.4), (3.6, 7.4))
add_arrow(ax2, (6.2, 7.4), (6.6, 7.4))

add_box(ax2, (3.0, 4.6), 3.0, 1.2, "Baseline Policy\n(Threshold)")
add_box(ax2, (6.0, 4.6), 3.0, 1.2, "L2D-like Policy\n(Defer if uncertain)")

add_arrow(ax2, (5.0, 6.8), (4.5, 5.8), "mode=baseline", connectionstyle="arc3,rad=0.2")
add_arrow(ax2, (6.8, 6.8), (7.5, 5.8), "mode=l2d", connectionstyle="arc3,rad=-0.2")

add_box(ax2, (1.0, 2.6), 3.0, 1.2, "AI Step\npredict(ai_prob)")
add_box(ax2, (4.4, 2.6), 1.2, 1.2, "Defer?")
add_box(ax2, (6.2, 2.6), 3.0, 1.2, "Human Step\nclassify()")

add_arrow(ax2, (2.5, 4.6), (2.5, 3.8))
add_arrow(ax2, (5.5, 4.6), (5.0, 3.8))

add_arrow(ax2, (2.5, 2.6), (4.4, 2.6))
add_arrow(ax2, (5.6, 2.6), (6.2, 2.6), "Yes")
add_arrow(ax2, (4.4, 2.6), (3.2, 2.6), "No", connectionstyle="arc3,rad=0.2")

add_box(ax2, (3.6, 0.8), 2.8, 1.2, "Logs + Metrics\naccuracy, defer_rate,\nAI/Human accuracy, latency")
add_arrow(ax2, (5.0, 2.6), (5.0, 2.0))

exp_path = "haic_mvp_experiment.png"
fig2.tight_layout()
fig2.savefig(exp_path, bbox_inches="tight")
plt.close(fig2)

# Confirm files
sorted([str(p) for p in Path(".").glob("haic_mvp_*.png")])

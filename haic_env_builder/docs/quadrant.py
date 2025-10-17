# Create 2x2 quadrant visuals for key metric combinations using matplotlib (no seaborn, no custom colors)
import matplotlib.pyplot as plt
import os

def make_quadrant(ax, x_label, y_label, q11, q12, q21, q22, title):
    # Draw axes crossing at 0
    ax.axhline(0, linewidth=1)
    ax.axvline(0, linewidth=1)
    # Set labels and title
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    # Remove ticks and set fixed limits
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    # Annotate quadrants
    # Q1: x>0, y>0 (top-right)
    ax.text(0.5, 0.5, q11, ha='center', va='center', fontsize=10, wrap=True)
    # Q2: x<0, y>0 (top-left)
    ax.text(-0.5, 0.5, q12, ha='center', va='center', fontsize=10, wrap=True)
    # Q3: x<0, y<0 (bottom-left)
    ax.text(-0.5, -0.5, q22, ha='center', va='center', fontsize=10, wrap=True)
    # Q4: x>0, y<0 (bottom-right)
    ax.text(0.5, -0.5, q21, ha='center', va='center', fontsize=10, wrap=True)
    # Add +/- guides on axes ends
    ax.text(0.95, -0.1, '+', ha='right', va='center')
    ax.text(-0.95, -0.1, '-', ha='left', va='center')
    ax.text(-0.1, 0.95, '+', ha='center', va='top')
    ax.text(-0.1, -0.95, '-', ha='center', va='bottom')

plots = []

# 1) EL (x, lower is better so invert sign) vs Tr (y, higher is better)
fig, ax = plt.subplots(figsize=(6,6))
make_quadrant(
    ax,
    x_label="Effort Loss (EL)  ↓ better",
    y_label="Trust (Tr)  ↑ better",
    q11="Ideal collaboration:\nfast completion\nand accepted AI support.",
    q12="Trusted but inefficient:\nAI is relied on, but\nprocess has delays/bottlenecks.",
    q21="Efficient but untrusted:\nsystem saves time,\nbut humans resist\nor override AI input.",
    q22="Breakdown:\nneither efficient\nnor trusted — redesign needed.",
    title="EL × Tr Diagnostic Quadrant"
)
path1 = "quadrant_EL_Tr.png"
fig.tight_layout()
fig.savefig(path1, dpi=180)
plt.close(fig)
plots.append(path1)

# 2) F vs HCL
fig, ax = plt.subplots(figsize=(6,6))
make_quadrant(
    ax,
    x_label="Interaction Frequency (F)  ↑ more",
    y_label="Human-Centeredness (HCL)  ↑ easier",
         q11="Smooth collaboration:\nfrequent interactions\nhandled with ease.",
    q12="Minimal but effective:\nsystem works with few,\neffortless interactions.",
    q21="Overload:\ntoo many interactions\ncreate strain despite\nactive collaboration.",
    q22="Disengaged or strained:\nlittle interaction,\nand the few that\noccur feel burdensome.",

    title="F × HCL Diagnostic Quadrant"
)
path2 = "quadrant_F_HCL.png"
fig.tight_layout()
fig.savefig(path2, dpi=180)
plt.close(fig)
plots.append(path2)

# 3) A vs Tr
fig, ax = plt.subplots(figsize=(6,6))
make_quadrant(
    ax,
    x_label="Adaptability (A)  ↑ improves",
    y_label="Trust (Tr)  ↑ better",
    q11="Mutual learning:\ncollaboration improves, \ntrust reinforced.",
    q12="Trust despite decline:\nusers still trust AI,\nbut results worsen —\nblind reliance risk.",
    q21="AI improves but untrusted:\nAI adapts,\nbut humans don’t rely on it.",
    q22="Failure to adapt:\ndeclining performance\n and eroding trust.",
    title="A × Tr Diagnostic Quadrant"
)
path3 = "quadrant_A_Tr.png"
fig.tight_layout()
fig.savefig(path3, dpi=180)
plt.close(fig)
plots.append(path3)

# 4) EL vs HCL
fig, ax = plt.subplots(figsize=(6,6))
make_quadrant(
    ax,
    x_label="Effort Loss (EL)  ↓ better",
    y_label="Human-Centeredness (HCL)  ↑ easier",
    q11="Sustainable performance:\nfast, efficient, and user-friendly.",
    q12="Comfortable but slow:\ncollaboration is easy\nbut time-consuming.",
    q21="Unsustainable pressure:\nefficiency achieved at the cost\nof user overload.",
    q22="Ineffective and tiring:\nneither efficient\n nor user-friendly.",
    title="EL × HCL Diagnostic Quadrant"
)
path4 = "quadrant_EL_HCL.png"
fig.tight_layout()
fig.savefig(path4, dpi=180)
plt.close(fig)
plots.append(path4)

# 5) S vs A
fig, ax = plt.subplots(figsize=(6,6))
make_quadrant(
    ax,
    x_label="Similarity (S)  ↑ faithful surrogate",
    y_label="Adaptability (A)  ↑ improves",
    q11="Reliable surrogate:\nsurrogates behave like humans,\n and learning occurs.",
    q12="Unreliable surrogate learning:\nAI adapts, but surrogate\n does not reflect real users.",
    q21="Faithful but stagnant:\nsurrogates mimic humans,\nbut neither improves.",
    q22="Misleading results:\n poor surrogate fidelity and\n no adaptation.",
    title="S × A Diagnostic Quadrant"
)
path5 = "quadrant_S_A.png"
fig.tight_layout()
fig.savefig(path5, dpi=180)
plt.close(fig)
plots.append(path5)

plots

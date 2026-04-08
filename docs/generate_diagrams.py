from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


def box(ax, x, y, w, h, text, fc="#F8FAFC", ec="#334155", tc="#0F172A", fs=11, rounded=0.08):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.02,rounding_size={rounded}",
        linewidth=1.4,
        facecolor=fc,
        edgecolor=ec,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc, fontweight="semibold")


def arrow(ax, p1, p2, color="#334155", lw=1.6, style="-|>", ls="-"):
    ax.add_patch(
        FancyArrowPatch(
            p1,
            p2,
            arrowstyle=style,
            mutation_scale=12,
            linewidth=lw,
            color=color,
            linestyle=ls,
            shrinkA=4,
            shrinkB=4,
        )
    )


def generate_architecture(path: Path):
    fig, ax = plt.subplots(figsize=(14, 8), dpi=200)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    box(ax, 5.0, 6.6, 4.0, 0.9, "User Interface (CLI / GUI)", fc="#E2E8F0")
    box(ax, 4.7, 4.9, 4.6, 1.0, "Core Management Engine", fc="#DBEAFE", ec="#1D4ED8")
    box(ax, 1.0, 4.9, 3.2, 1.0, "Dependency Checker", fc="#DCFCE7", ec="#15803D")
    box(ax, 9.8, 4.9, 3.2, 1.0, "Environment Manager", fc="#DCFCE7", ec="#15803D")
    box(ax, 4.8, 3.2, 4.4, 1.0, "Package Bridge (apt / brew / choco)", fc="#F5F3FF", ec="#6D28D9")
    box(ax, 0.8, 1.1, 3.6, 1.0, "Action Logs", fc="#FEF2F2", ec="#B91C1C")
    box(ax, 5.1, 1.1, 3.8, 1.0, "Tools Registry", fc="#EFF6FF", ec="#1D4ED8")
    box(ax, 9.6, 1.1, 3.6, 1.0, "User Config", fc="#F8FAFC", ec="#334155")

    arrow(ax, (7.0, 6.6), (7.0, 5.9))
    arrow(ax, (7.0, 5.9), (7.0, 6.6))
    arrow(ax, (4.7, 5.4), (4.2, 5.4))
    arrow(ax, (4.2, 5.4), (4.7, 5.4))
    arrow(ax, (9.3, 5.4), (9.8, 5.4))
    arrow(ax, (9.8, 5.4), (9.3, 5.4))
    arrow(ax, (7.0, 4.9), (7.0, 4.2))
    arrow(ax, (7.0, 4.2), (7.0, 4.9))
    arrow(ax, (2.6, 4.9), (2.6, 2.1))
    arrow(ax, (11.4, 4.9), (11.4, 2.1))
    arrow(ax, (7.0, 3.2), (7.0, 2.1))
    arrow(ax, (7.0, 2.1), (7.0, 3.2))

    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def generate_workflow(path: Path):
    fig, ax = plt.subplots(figsize=(14, 8), dpi=200)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    box(ax, 2.2, 6.8, 4.3, 0.8, "User Query Input", fc="#E2E8F0")
    box(ax, 2.2, 5.6, 4.3, 0.8, "Dependency Validation", fc="#EEF2FF", ec="#4338CA")
    box(ax, 2.2, 4.4, 4.3, 0.8, "Installation / Update Logic", fc="#FFEDD5", ec="#C2410C")
    box(ax, 2.2, 3.2, 4.3, 0.8, "Environment Configuration", fc="#EEF2FF", ec="#4338CA")
    box(ax, 2.2, 2.0, 4.3, 0.8, "Verification & Logging", fc="#EEF2FF", ec="#4338CA")
    box(ax, 2.2, 0.8, 4.3, 0.8, "Response to User", fc="#E2E8F0")

    box(ax, 8.0, 4.4, 4.0, 0.9, "Tools Registry", fc="#EFF6FF", ec="#1D4ED8")
    box(ax, 8.0, 2.7, 4.0, 0.9, "System PATH / Environment", fc="#F8FAFC", ec="#334155")

    arrow(ax, (4.35, 6.8), (4.35, 6.4))
    arrow(ax, (4.35, 5.6), (4.35, 5.2))
    arrow(ax, (4.35, 4.4), (4.35, 4.0))
    arrow(ax, (4.35, 3.2), (4.35, 2.8))
    arrow(ax, (4.35, 2.0), (4.35, 1.6))

    arrow(ax, (6.5, 4.8), (8.0, 4.8))
    arrow(ax, (8.0, 4.8), (6.5, 4.8))
    arrow(ax, (6.5, 3.6), (8.0, 3.15))

    arrow(ax, (6.5, 5.95), (7.4, 5.95), color="#DC2626", lw=1.5, style="-", ls="--")
    arrow(ax, (7.4, 5.95), (7.4, 1.2), color="#DC2626", lw=1.5, style="-", ls="--")
    arrow(ax, (7.4, 1.2), (6.5, 1.2), color="#DC2626", lw=1.5, style="-|>", ls="--")
    ax.text(7.55, 3.6, "Abort on Error", color="#B91C1C", fontsize=10, rotation=90, va="center")

    arrow(ax, (2.2, 2.4), (1.2, 2.4), color="#DC2626", lw=1.5, style="-", ls="--")
    arrow(ax, (1.2, 2.4), (1.2, 1.2), color="#DC2626", lw=1.5, style="-", ls="--")
    arrow(ax, (1.2, 1.2), (2.2, 1.2), color="#DC2626", lw=1.5, style="-|>", ls="--")
    ax.text(0.35, 1.8, "Error Logs", color="#B91C1C", fontsize=10, va="center")

    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def generate_eda_landscape(path: Path):
    fig, ax = plt.subplots(figsize=(14, 8), dpi=200)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    box(ax, 5.0, 6.6, 4.0, 0.9, "eSim Platform", fc="#DBEAFE", ec="#1D4ED8", fs=12)
    
    y_mid = 4.3
    w = 2.4
    h = 1.0
    fs_small = 10
    box(ax, 0.4, y_mid, w, h, "KiCad\n(PCB +\nSchematic)", fc="#F8FAFC", fs=fs_small)
    box(ax, 3.1, y_mid, w, h, "Ngspice\n(Simulation)", fc="#F8FAFC", fs=fs_small)
    box(ax, 5.8, y_mid, w, h, "OpenROAD\n(Digital Flow)", fc="#F8FAFC", fs=fs_small)
    box(ax, 8.5, y_mid, w, h, "OpenModelica\n(Modeling)", fc="#F8FAFC", fs=fs_small)
    box(ax, 11.2, y_mid, w, h, "Qucs / Other\n(Niche)", fc="#F8FAFC", fs=fs_small)
    
    box(ax, 1.0, 1.6, 12.0, 1.2, "Integration Challenge:\nVersioning, Dependencies, Environment Setup", fc="#FEF3C7", ec="#B45309", fs=13)

    centers_x = [1.6, 4.3, 7.0, 9.7, 12.4]
    for cx in centers_x:
        arrow(ax, (7.0, 6.6), (cx, y_mid + h))
        arrow(ax, (cx, y_mid), (cx, 2.8))

    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def generate_stack_rationale(path: Path):
    fig, ax = plt.subplots(figsize=(14, 8), dpi=200)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    box(ax, 5.3, 6.9, 3.4, 0.8, "Technology Choices", fc="#E2E8F0", fs=12)
    box(ax, 1.0, 5.4, 3.8, 0.9, "Python\nCross-platform core", fc="#DBEAFE", ec="#1D4ED8")
    box(ax, 5.1, 5.4, 3.8, 0.9, "Typer + Rich\nCLI UX + Commands", fc="#DCFCE7", ec="#15803D")
    box(ax, 9.2, 5.4, 3.8, 0.9, "CustomTkinter\nModern GUI", fc="#F5F3FF", ec="#6D28D9")

    box(ax, 0.9, 3.8, 3.9, 0.85, "Alternative: Go / Rust\nHigh speed, slower iteration", fc="#F8FAFC")
    box(ax, 5.0, 3.8, 4.0, 0.85, "Alternative: Click/Argparse\nLess typed structure", fc="#F8FAFC")
    box(ax, 9.1, 3.8, 3.9, 0.85, "Alternative: PyQt / wxPython\nHeavier setup footprint", fc="#F8FAFC")

    box(ax, 2.0, 1.9, 10.0, 1.2, "Decision Outcome:\nFast delivery, maintainable modules, strong CLI+GUI parity", fc="#FEF3C7", ec="#B45309", fs=12)

    arrow(ax, (7.0, 6.9), (2.9, 6.3))
    arrow(ax, (7.0, 6.9), (7.0, 6.3))
    arrow(ax, (7.0, 6.9), (11.1, 6.3))
    arrow(ax, (2.9, 5.4), (2.9, 4.65), color="#1D4ED8")
    arrow(ax, (7.0, 5.4), (7.0, 4.65), color="#15803D")
    arrow(ax, (11.1, 5.4), (11.1, 4.65), color="#6D28D9")
    arrow(ax, (2.9, 3.8), (5.0, 3.1))
    arrow(ax, (7.0, 3.8), (7.0, 3.1))
    arrow(ax, (11.1, 3.8), (9.0, 3.1))

    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def generate_use_case(path: Path):
    fig, ax = plt.subplots(figsize=(14, 8), dpi=200)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    box(ax, 0.9, 3.4, 2.0, 1.1, "User", fc="#F8FAFC", ec="#334155", fs=13)
    box(ax, 4.2, 5.9, 3.4, 0.9, "Install Tool", fc="#EFF6FF", ec="#1D4ED8")
    box(ax, 4.2, 4.5, 3.4, 0.9, "Update Tool", fc="#EFF6FF", ec="#1D4ED8")
    box(ax, 4.2, 3.1, 3.4, 0.9, "List Tools", fc="#EFF6FF", ec="#1D4ED8")
    box(ax, 4.2, 1.7, 3.4, 0.9, "View Logs", fc="#EFF6FF", ec="#1D4ED8")
    box(ax, 8.6, 5.2, 4.0, 0.9, "Check Dependencies", fc="#F5F3FF", ec="#6D28D9")
    box(ax, 8.6, 3.8, 4.0, 0.9, "Verify Installation", fc="#F5F3FF", ec="#6D28D9")

    arrow(ax, (2.9, 3.95), (4.2, 6.35))
    arrow(ax, (2.9, 3.95), (4.2, 4.95))
    arrow(ax, (2.9, 3.95), (4.2, 3.55))
    arrow(ax, (2.9, 3.95), (4.2, 2.15))
    arrow(ax, (2.9, 3.95), (8.6, 5.65))
    arrow(ax, (2.9, 3.95), (8.6, 4.25))
    arrow(ax, (7.6, 6.35), (8.6, 5.65), color="#475569")
    arrow(ax, (7.6, 4.95), (8.6, 4.25), color="#475569")

    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def generate_cli_hierarchy(path: Path):
    fig, ax = plt.subplots(figsize=(14, 8), dpi=220)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    box(ax, 3.1, 6.8, 7.8, 0.8, "esim-tool <command> [options]", fc="#E2E8F0", ec="#334155", fs=12)

    box(ax, 1.1, 5.2, 3.0, 0.75, "install", fc="#EFF6FF", ec="#1D4ED8")
    box(ax, 5.5, 5.2, 3.0, 0.75, "update", fc="#EFF6FF", ec="#1D4ED8")
    box(ax, 9.9, 5.2, 3.0, 0.75, "list", fc="#EFF6FF", ec="#1D4ED8")

    box(ax, 1.1, 3.7, 3.0, 0.75, "check-updates", fc="#F8FAFC")
    box(ax, 5.5, 3.7, 3.0, 0.75, "verify", fc="#F8FAFC")
    box(ax, 9.9, 3.7, 3.0, 0.75, "check-deps", fc="#F8FAFC")

    box(ax, 1.1, 2.2, 3.0, 0.75, "logs", fc="#F8FAFC")
    box(ax, 5.5, 2.2, 3.0, 0.75, "uninstall", fc="#F8FAFC")
    box(ax, 9.9, 2.2, 3.0, 0.75, "config-show", fc="#F8FAFC")

    roots = [(4.2, 6.8), (7.0, 6.8), (9.8, 6.8)]
    targets = [(2.6, 5.95), (7.0, 5.95), (11.4, 5.95),
               (2.6, 4.45), (7.0, 4.45), (11.4, 4.45),
               (2.6, 2.95), (7.0, 2.95), (11.4, 2.95)]
    for i, target in enumerate(targets):
        root = roots[i % len(roots)]
        arrow(ax, root, target, color="#334155", lw=1.2)

    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    out_dir = Path(__file__).resolve().parent / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    generate_architecture(out_dir / "architecture_clean.png")
    generate_workflow(out_dir / "workflow_clean.png")
    generate_eda_landscape(out_dir / "eda_landscape.png")
    generate_stack_rationale(out_dir / "stack_rationale.png")
    generate_use_case(out_dir / "use_case_clean.png")
    generate_cli_hierarchy(out_dir / "cli_hierarchy_clean.png")


if __name__ == "__main__":
    main()

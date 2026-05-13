"""Generate the final conference-style PDF report with embedded figures."""
import os
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image,
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

OUTPUT = os.path.join(os.path.dirname(__file__), "..", "final_report.pdf")

GA_COLOR = "#2166AC"
RS_COLOR = "#D6604D"


# ── Chart figure generators ───────────────────────────────────────────────────

def fig_convergence():
    gens  = list(range(15))
    means = [0.204,0.472,0.510,0.528,0.541,0.553,0.558,0.564,
             0.551,0.547,0.539,0.532,0.498,0.481,0.465]
    bests = [0.661,0.659,0.659,0.655,0.660,0.663,0.669,0.668,
             0.668,0.667,0.666,0.666,0.665,0.665,0.665]

    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    ax.plot(gens, bests, "o-", color=GA_COLOR, linewidth=2,
            markersize=5, label="Best (elite)")
    ax.plot(gens, means, "s--", color=GA_COLOR, alpha=0.6,
            linewidth=1.8, markersize=4, label="Population mean")
    ax.axhline(np.mean(bests), color=GA_COLOR, linewidth=0.8,
               linestyle=":", alpha=0.4,
               label=f"Avg best ({np.mean(bests):.4f})")
    ax.set_xlabel("Generation", fontsize=10)
    ax.set_ylabel("Blended fitness", fontsize=10)
    ax.set_title("GA Convergence - Trial 0", fontsize=11, fontweight="bold")
    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(0.0, 0.75)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.tick_params(labelsize=9)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def fig_ga_vs_rs():
    labels = ["blended", "rouge_l", "cosine\ncalib."]
    train_ga,  train_rs  = [0.6763,0.3319,0.8239], [0.6642,0.3205,0.8115]
    train_gsd, train_rsd = [0.0261,0.0390,0.0272], [0.0256,0.0382,0.0261]
    held_ga,   held_rs   = [0.6228,0.3058,0.7586], [0.6301,0.3086,0.7680]
    held_gsd,  held_rsd  = [0.0254,0.0200,0.0280], [0.0487,0.0274,0.0587]

    x, w = np.arange(3), 0.18
    eprops = dict(elinewidth=1.2, capsize=3, capthick=1.2)
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.4))

    for ax, gv, rv, gs, rs_, title in [
        (axes[0], train_ga, train_rs, train_gsd, train_rsd, "Training Subset"),
        (axes[1], held_ga,  held_rs,  held_gsd,  held_rsd,  "Held-Out Test Set"),
    ]:
        ax.bar(x-w/2, gv, w*0.9, color=GA_COLOR, alpha=0.85,
               label="GA", yerr=gs, error_kw=eprops)
        ax.bar(x+w/2, rv, w*0.9, color=RS_COLOR, alpha=0.85,
               label="RS", yerr=rs_, error_kw=eprops)
        ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_ylabel("Mean score (+/- 1 SD)", fontsize=9)
        ax.legend(fontsize=8)
        ax.grid(True, axis="y", linestyle="--", alpha=0.35)
        ax.tick_params(labelsize=9)
        all_v = gv + rv
        ax.set_ylim(max(0, min(all_v)-0.08), max(all_v)+0.08)

    fig.suptitle("GA vs. Random Search: Configuration Quality by Metric",
                 fontsize=11, fontweight="bold", y=1.01)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def fig_cliffs_delta():
    labels  = ["Blended", "ROUGE-L", "Cosine (raw)", "Cosine (cal.)"]
    train_d = [+0.46, +0.16, +0.32, +0.32]
    held_d  = [-0.32, -0.20, -0.34, -0.34]
    thresholds = [(0.147,), (0.33,), (0.474,)]

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0), sharey=True)
    y = np.arange(len(labels))

    for ax, deltas, title in [
        (axes[0], train_d, "Training Subset"),
        (axes[1], held_d,  "Held-Out Test Set"),
    ]:
        bar_colors = [GA_COLOR if d >= 0 else RS_COLOR for d in deltas]
        bars = ax.barh(y, deltas, color=bar_colors, alpha=0.80, height=0.55)
        for (thresh,) in thresholds:
            ax.axvline( thresh, color="gray", linewidth=0.7, linestyle=":")
            ax.axvline(-thresh, color="gray", linewidth=0.7, linestyle=":")
        ax.axvline(0, color="black", linewidth=1.0)
        ax.set_xlim(-0.65, 0.65)
        ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel("Cliff's delta  (+ = GA better)", fontsize=9)
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.grid(True, axis="x", linestyle="--", alpha=0.3)
        ax.tick_params(labelsize=9)
        for bar, d in zip(bars, deltas):
            xpos = d + (0.03 if d >= 0 else -0.03)
            ax.text(xpos, bar.get_y()+bar.get_height()/2,
                    f"{d:+.2f}", va="center",
                    ha="left" if d >= 0 else "right", fontsize=8)

    ga_p = mpatches.Patch(color=GA_COLOR, alpha=0.8, label="GA favoured (+)")
    rs_p = mpatches.Patch(color=RS_COLOR, alpha=0.8, label="RS favoured (-)")
    fig.legend(handles=[ga_p, rs_p], loc="lower center",
               ncol=2, fontsize=8, bbox_to_anchor=(0.5, -0.08))
    fig.suptitle("Effect Size (Cliff's delta) by Metric and Evaluation Context",
                 fontsize=11, fontweight="bold")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


# ── Styles ────────────────────────────────────────────────────────────────────

def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("ReportTitle", parent=base["Normal"],
            fontSize=16, leading=20, spaceAfter=6,
            alignment=TA_CENTER, fontName="Times-Bold"),
        "author": ParagraphStyle("Author", parent=base["Normal"],
            fontSize=11, leading=14, spaceAfter=4,
            alignment=TA_CENTER, fontName="Times-Italic"),
        "affil": ParagraphStyle("Affil", parent=base["Normal"],
            fontSize=10, leading=12, spaceAfter=12,
            alignment=TA_CENTER, fontName="Times-Roman"),
        "abstract_heading": ParagraphStyle("AbstractHeading", parent=base["Normal"],
            fontSize=10, leading=12, spaceBefore=6, spaceAfter=3,
            alignment=TA_CENTER, fontName="Times-Bold"),
        "abstract": ParagraphStyle("Abstract", parent=base["Normal"],
            fontSize=9.5, leading=13, spaceAfter=10,
            leftIndent=36, rightIndent=36,
            alignment=TA_JUSTIFY, fontName="Times-Roman"),
        "h1": ParagraphStyle("H1", parent=base["Normal"],
            fontSize=11, leading=14, spaceBefore=10, spaceAfter=4,
            fontName="Times-Bold"),
        "h2": ParagraphStyle("H2", parent=base["Normal"],
            fontSize=10.5, leading=13, spaceBefore=6, spaceAfter=3,
            fontName="Times-Bold"),
        "body": ParagraphStyle("Body", parent=base["Normal"],
            fontSize=10, leading=14, spaceAfter=6,
            alignment=TA_JUSTIFY, fontName="Times-Roman"),
        "body_indent": ParagraphStyle("BodyIndent", parent=base["Normal"],
            fontSize=10, leading=14, spaceAfter=4, leftIndent=18,
            alignment=TA_JUSTIFY, fontName="Times-Roman"),
        "math": ParagraphStyle("Math", parent=base["Normal"],
            fontSize=9.5, leading=14, spaceAfter=2,
            leftIndent=36, fontName="Courier"),
        "caption": ParagraphStyle("Caption", parent=base["Normal"],
            fontSize=9, leading=11, spaceAfter=6,
            alignment=TA_CENTER, fontName="Times-Italic"),
        "ref": ParagraphStyle("Ref", parent=base["Normal"],
            fontSize=9, leading=12, spaceAfter=3,
            leftIndent=18, firstLineIndent=-18, fontName="Times-Roman"),
    }


def results_table(data, col_widths, extra_cmds=None):
    t = Table(data, colWidths=col_widths)
    cmds = [
        ("FONTNAME",    (0,0),(-1,0),  "Times-Bold"),
        ("FONTSIZE",    (0,0),(-1,-1), 8.5),
        ("LEADING",     (0,0),(-1,-1), 11),
        ("BACKGROUND",  (0,0),(-1,0),  colors.HexColor("#DDDDDD")),
        ("GRID",        (0,0),(-1,-1), 0.4, colors.grey),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F7F7F7")]),
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 3),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ("RIGHTPADDING",  (0,0),(-1,-1), 5),
        ("ALIGN",(1,0),(-1,-1),"CENTER"),
        ("ALIGN",(0,0),(0,-1),"LEFT"),
    ]
    if extra_cmds:
        cmds += extra_cmds
    t.setStyle(TableStyle(cmds))
    return t


def buf_to_image(buf, width):
    img = Image(buf, width=width, height=None)
    img.drawHeight = width * img.imageHeight / img.imageWidth
    return img


# ── Story ─────────────────────────────────────────────────────────────────────

def make_story(styles, chart_figs):
    story = []
    S = styles
    fig_conv, fig_bars, fig_delta = chart_figs
    PAGE_W = 6.5 * inch

    # ── Title ────────────────────────────────────────────────────────────────
    story.append(Paragraph(
        "Search-Based LLM Tool Configuration Management:<br/>"
        "Evolving Prompt Templates for Code Summarization", S["title"]))
    story.append(Paragraph(
        "Sean Lai,  Anastasia Strulistova", S["author"]))
    story.append(Paragraph("New York University", S["affil"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.black))
    story.append(Spacer(1, 6))

    # ── Abstract ─────────────────────────────────────────────────────────────
    story.append(Paragraph("Abstract", S["abstract_heading"]))
    story.append(Paragraph(
        "LLM-powered SE tools are acutely sensitive to their prompt configuration: "
        "the structured template governing the model's persona, task framing, "
        "behavioral constraints, and output format. Selecting the optimal "
        "configuration from a combinatorial space of 160,000 candidates is a "
        "software engineering problem infeasible to solve by hand. We formulate "
        "this prompt configuration management task as a Search-Based Software "
        "Engineering (SBSE) optimization problem and apply a Genetic Algorithm (GA) "
        "to evolve high-quality prompt configurations for an LLM-based code "
        "summarization tool. A component bank of 20 choices across four orthogonal "
        "configuration slots (role, task, guard, format) defines the search space. "
        "Fitness blends lexical overlap (ROUGE-L) and calibrated semantic similarity "
        "(cosine via sentence embeddings) against Claude Opus-generated reference "
        "outputs. Over 10 independent trials with a budget-matched Random Search "
        "baseline (P=12, G=15, 180 total evaluations), the GA shows a training-subset "
        "blended score advantage of 0.6763 vs. 0.6642 (Cliff's delta=+0.46, p=0.082). "
        "On a fully held-out 50-function test set neither algorithm significantly "
        "outperforms the other (GA blended=0.6228, RS=0.6301, Cliff's delta=-0.32, "
        "p=0.227), indicating that GA's in-sample advantage does not generalize at "
        "alpha=0.05 given the current search budget and component bank ceiling.",
        S["abstract"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.black))
    story.append(Spacer(1, 6))

    # ── 1. Introduction ───────────────────────────────────────────────────────
    story.append(Paragraph("1. Introduction", S["h1"]))
    story.append(Paragraph(
        "LLM-powered SE tools are increasingly deployed for tasks such as code "
        "summarization, bug localization, and test generation. A critical and "
        "underappreciated SE challenge is <i>prompt configuration management</i>: "
        "deciding which structured prompt template to deploy for a given tool and "
        "task. A prompt template bundles four orthogonal configuration dimensions "
        "the model role/persona, the task instruction, behavioral guard clauses, "
        "and output format constraints. With 20 candidate values per dimension, "
        "the configuration space contains 20^4 = 160,000 distinct templates. "
        "Exhaustively evaluating each at ~1-2 seconds of LLM inference would "
        "take over 44 hours per experiment, making manual configuration management "
        "infeasible at any meaningful scale.",
        S["body"]))
    story.append(Paragraph(
        "We apply SBSE techniques to this configuration management problem using "
        "an LLM-based code summarization tool as the application domain. Code "
        "summarization is a representative SE analysis task whose outputs feed "
        "downstream uses including code review, developer onboarding, and IDE "
        "tooling; documentation generation is one such downstream consumer. "
        "Crucially, the SE problem being solved here is the <i>configuration "
        "management</i> problem, not summarization per se: we treat the LLM "
        "summarization tool as a fixed black box and search for the optimal prompt "
        "configuration to deploy it with.",
        S["body"]))
    story.append(Paragraph(
        "We model each candidate configuration as a four-component genotype drawn "
        "from a curated component bank and define a computable fitness function "
        "combining lexical and semantic similarity to reference outputs. We compare "
        "a Genetic Algorithm (GA) with tournament selection, crossover, mutation, "
        "and elitism against a budget-matched Random Search (RS) baseline.",
        S["body"]))
    story.append(Paragraph("Our contributions are:", S["body"]))
    for item in [
        "(1) A formal SBSE encoding of LLM tool prompt configuration management as "
        "a combinatorial optimization problem.",
        "(2) A blended lexical-semantic fitness function with empirically calibrated "
        "cosine scaling for evaluating configuration quality.",
        "(3) A rigorous 10-trial comparative study with Wilcoxon rank-sum testing and "
        "Cliff's delta effect sizes on both in-sample and held-out benchmarks.",
        "(4) An analysis of why GA's population-mean advantage over RS does not "
        "translate to best-of-trial generalization under the current experimental setup.",
    ]:
        story.append(Paragraph(item, S["body_indent"]))

    # ── 2. Related Work ───────────────────────────────────────────────────────
    story.append(Paragraph("2. Related Work", S["h1"]))
    story.append(Paragraph(
        "SBSE has been applied across a wide range of software engineering tasks. "
        "Harman and Jones [1] introduced the SBSE paradigm, showing that classical "
        "metaheuristics can effectively solve SE optimization problems. McMinn [2] "
        "surveyed search-based test data generation; EvoSuite [3] demonstrated "
        "GA-based unit test generation at industrial scale. Requirement "
        "prioritization [4] and refactoring [5] have similarly been framed as "
        "fitness-guided search problems.",
        S["body"]))
    story.append(Paragraph(
        "Configuration management and hyperparameter optimization are closely "
        "related SBSE domains. Many SE tools expose large configuration spaces "
        "where metaheuristic search outperforms grid or random sampling. Our work "
        "extends this to LLM tool configuration: the prompt template is the "
        "configuration artifact, and its quality can only be assessed by querying "
        "the live LLM, making fitness evaluation expensive and motivating "
        "budget-aware search.",
        S["body"]))
    story.append(Paragraph(
        "On the LLM prompt optimization side, Zhou et al. [6] introduced Automatic "
        "Prompt Engineer (APE), framing prompt selection as a configuration search. "
        "PromptBreeder [7] applies evolutionary computation directly to prompt text "
        "strings. Our work differs in treating the prompt as a structured "
        "configuration tuple (discrete component bank), making the search space "
        "discrete, enumerable, and reproducible, more aligned with classical SBSE "
        "configuration optimization formulations.",
        S["body"]))

    # ── 3. Problem Formulation ────────────────────────────────────────────────
    story.append(Paragraph("3. Problem Formulation", S["h1"]))
    story.append(Paragraph(
        "We formalize the problem as: given an LLM-based SE tool T and a component "
        "bank B defining valid configuration values, find the prompt configuration "
        "P* that maximizes a fitness function measuring output quality. The search "
        "space is the Cartesian product of four configuration slots.",
        S["body"]))

    story.append(Paragraph("3.1 Representation", S["h2"]))
    story.append(Paragraph(
        "A prompt configuration P is encoded as a 4-tuple genotype:",
        S["body"]))
    story.append(Paragraph("P = (role, task, guard, format)", S["math"]))
    story.append(Paragraph(
        "where each component is drawn independently from a component bank B with "
        "20 options per slot, giving |S| = 20^4 = 160,000 distinct configurations. "
        "The slots are semantically orthogonal: <i>role</i> sets the LLM persona, "
        "<i>task</i> specifies the summarization instruction, <i>guard</i> constrains "
        "output behavior, and <i>format</i> prescribes length and structure.",
        S["body"]))
    story.append(Paragraph(
        "Example values: role = \"senior software engineer\", task = \"Summarize "
        "this function in 2-4 sentences\", guard = \"Do not speculate beyond what "
        "the code shows\", format = \"Keep the response under 60 words; one short "
        "paragraph.\"",
        S["body"]))

    story.append(Paragraph("3.2 Fitness Function", S["h2"]))
    story.append(Paragraph(
        "Let G(P, f) denote the summary generated by the target LLM on function f "
        "using configuration P, and R(f) the Opus-generated reference summary. "
        "Fitness is averaged over N functions. Raw cosine similarity is first "
        "calibrated against an empirical baseline b = 0.45:",
        S["body"]))
    story.append(Paragraph(
        "cosine_cal(P,f) = max(0, (cosine_sim(G(P,f), R(f)) - b) / (1 - b))",
        S["math"]))
    story.append(Paragraph("The blended configuration fitness is:", S["body"]))
    story.append(Paragraph(
        "fitness(P) = (1/N) * sum_f [  a * ROUGE-L(G(P,f), R(f))", S["math"]))
    story.append(Paragraph(
        "                             + (1-a) * cosine_cal(P,f)", S["math"]))
    story.append(Paragraph(
        "                             - L_len * length_penalty(P)", S["math"]))
    story.append(Paragraph(
        "                             - L_fmt * format_penalty(G(P,f))  ]", S["math"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("where:", S["body"]))
    for p in [
        "a = 0.3   (ROUGE-L weight; 0.7 on cosine rewards semantic equivalence)",
        "L_len = 0.1,  L_fmt = 0.2   (penalty coefficients)",
        "length_penalty = 0 if tokens(P) <= 200; else ((tokens(P) - 200) / 200)^2",
        "format_penalty = 1.0 if output is empty, contains code fences, or exceeds 10x |R(f)|; else 0",
    ]:
        story.append(Paragraph(p, S["body_indent"]))
    story.append(Paragraph(
        "Cosine similarity uses BAAI/bge-small-en-v1.5 sentence embeddings; "
        "ROUGE-L uses the rouge_score library.",
        S["body"]))

    story.append(Paragraph("3.3 Search Operators", S["h2"]))
    for op in [
        "<b>Selection:</b> k-tournament (k=3). Three individuals sampled uniformly "
        "without replacement; the highest-fitness candidate is selected.",
        "<b>Crossover</b> (rate 0.7): Given parents Pa and Pb, 1-2 randomly chosen "
        "configuration slots are inherited from Pb; remaining slots from Pa.",
        "<b>Mutation</b> (rate 0.3): Each slot replaced independently with a "
        "uniformly random distinct alternative from the component bank.",
        "<b>Elitism:</b> Top 3 individuals carried unchanged to the next generation.",
    ]:
        story.append(Paragraph(op, S["body_indent"]))
        story.append(Spacer(1, 2))

    # ── 4. Experimental Design ────────────────────────────────────────────────
    story.append(Paragraph("4. Experimental Design", S["h1"]))

    story.append(Paragraph("4.1 Algorithms Compared", S["h2"]))
    story.append(Paragraph(
        "<b>Genetic Algorithm (GA):</b> Population size P=12, generations G=15, "
        "operators as in Section 3.3.",
        S["body"]))
    story.append(Paragraph(
        "<b>Random Search (RS):</b> All P x G=180 configurations pre-sampled at "
        "startup using matched seeds and bucketed into G=15 groups of P=12 for "
        "checkpoint-aligned comparison. No selection pressure.",
        S["body"]))

    story.append(Paragraph("4.2 Parameter Settings", S["h2"]))
    param_data = [
        ["Parameter", "Value", "Parameter", "Value"],
        ["Population size (P)", "12",  "Crossover rate",  "0.70"],
        ["Generations (G)",     "15",  "Mutation rate",   "0.30"],
        ["Elite count",          "3",  "Tournament k",    "3"],
        ["Eval subset (inner)", "5 functions", "Workers", "16 (parallel)"],
        ["Target model", "Nemotron-49B-v1.5", "Temperature", "0"],
        ["Embedding model", "bge-small-en-v1.5", "Trials per algo", "10"],
    ]
    story.append(results_table(param_data,
                               [1.7*inch, 1.3*inch, 1.7*inch, 1.3*inch]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("4.3 Dataset", S["h2"]))
    story.append(Paragraph(
        "<b>Training benchmark:</b> 500 Python/JavaScript/TypeScript functions in "
        "data/functions/, paired with Claude Opus reference summaries. Each fitness "
        "call samples eval_subset=5 functions with a fixed per-trial seed.",
        S["body"]))
    story.append(Paragraph(
        "<b>Held-out test set:</b> 50 independently generated functions in data/test/ "
        "(20 Python, 15 JavaScript, 15 TypeScript), never sampled during any trial. "
        "Used exclusively for the generalization evaluation.",
        S["body"]))

    story.append(Paragraph("4.4 Statistical Analysis", S["h2"]))
    story.append(Paragraph(
        "10 independent trials per algorithm (matched seeds). Best-of-trial blended "
        "fitness compared via two-sided Wilcoxon rank-sum test (alpha=0.05). Effect "
        "size: Cliff's delta with Romano et al. [8] thresholds (negligible <0.147, "
        "small <0.33, medium <0.474, large >=0.474).",
        S["body"]))

    # ── 5. Results ────────────────────────────────────────────────────────────
    story.append(Paragraph("5. Results and Statistical Analysis", S["h1"]))

    story.append(Paragraph("5.1 Convergence Analysis", S["h2"]))
    story.append(Paragraph(
        "Figure 1 shows GA population mean and best blended fitness across "
        "generations for trial 0. The mean rose from 0.204 at generation 0 to "
        "0.564 at generation 7, a 2.8x increase, demonstrating textbook "
        "exploitation. The best-of-trial plateau (~0.66-0.67) is bounded by the "
        "component bank quality ceiling and LLM nondeterminism (~0.02 variance "
        "on identical configurations due to MoE routing in Nemotron at temperature=0).",
        S["body"]))
    story.append(buf_to_image(fig_conv, PAGE_W * 0.80))
    story.append(Paragraph(
        "Figure 1: GA convergence trajectory (trial 0). Population mean doubles "
        "in 7 generations; best-of-trial plateaus near the bank quality ceiling.",
        S["caption"]))

    story.append(Paragraph("5.2 Training-Subset vs. Held-Out Comparison", S["h2"]))
    story.append(Paragraph(
        "Figure 2 compares GA and RS mean scores (+/-1 SD) across three metrics "
        "on the training subset and the held-out test set. Tables 1 and 2 give "
        "the full statistical breakdown.",
        S["body"]))
    story.append(buf_to_image(fig_bars, PAGE_W))
    story.append(Paragraph(
        "Figure 2: GA vs. RS configuration quality (mean +/- 1 SD). "
        "GA leads on training; RS leads on held-out, a directional reversal "
        "consistent with overfitting the narrow eval_subset=10 benchmark.",
        S["caption"]))

    t1_data = [
        ["Metric","GA mean (SD)","RS mean (SD)","p-value","Cliff's d","Effect"],
        ["blended",           "0.6763 (0.0261)","0.6642 (0.0256)","0.0821","+0.46","medium"],
        ["rouge_l",           "0.3319 (0.0390)","0.3205 (0.0382)","0.5453","+0.16","small"],
        ["cosine_raw",        "0.9032 (0.0149)","0.8963 (0.0144)","0.2265","+0.32","small"],
        ["cosine_calibrated", "0.8239 (0.0272)","0.8115 (0.0261)","0.2265","+0.32","small"],
    ]
    col_w1 = [1.3*inch,1.35*inch,1.35*inch,0.7*inch,0.65*inch,0.65*inch]
    story.append(results_table(t1_data, col_w1,
        [("FONTNAME",(0,1),(0,-1),"Courier")]))
    story.append(Paragraph(
        "Table 1: Training-subset configuration comparison (eval_subset=10, 10 trials).",
        S["caption"]))

    t2_data = [
        ["Metric","GA mean (SD)","RS mean (SD)","p-value","Cliff's d","Effect"],
        ["blended",           "0.6228 (0.0254)","0.6301 (0.0487)","0.2265","-0.32","small"],
        ["rouge_l",           "0.3058 (0.0200)","0.3086 (0.0274)","0.4497","-0.20","small"],
        ["cosine_raw",        "0.8672 (0.0154)","0.8724 (0.0323)","0.1988","-0.34","medium"],
        ["cosine_calibrated", "0.7586 (0.0280)","0.7680 (0.0587)","0.1988","-0.34","medium"],
    ]
    story.append(results_table(t2_data, col_w1, [
        ("FONTNAME",(0,1),(0,-1),"Courier"),
        ("TEXTCOLOR",(4,1),(4,-1),colors.HexColor("#990000")),
    ]))
    story.append(Paragraph(
        "Table 2: Held-out test set configuration comparison (50 functions, 10 trials).",
        S["caption"]))

    story.append(Paragraph(
        "On the training subset GA achieves a higher blended score in 8 of 10 "
        "trials (mean 0.6763 vs. 0.6642, Cliff's delta=+0.46, medium effect, "
        "p=0.082). On the held-out test set the direction reverses on all four "
        "metrics (all p > 0.19, delta -0.20 to -0.34), indicating the GA "
        "configuration search overfits the narrow 10-function training benchmark.",
        S["body"]))

    story.append(Paragraph("5.3 Effect Size Summary", S["h2"]))
    story.append(Paragraph(
        "Figure 3 visualises Cliff's delta for all four metrics in both evaluation "
        "contexts. The sign flip between the two panels is the central empirical "
        "result of this study.",
        S["body"]))
    story.append(buf_to_image(fig_delta, PAGE_W))
    story.append(Paragraph(
        "Figure 3: Cliff's delta by metric and evaluation context. "
        "Blue = GA favoured; red = RS favoured. "
        "Dotted lines mark Romano et al. thresholds.",
        S["caption"]))

    # ── 6. Threats to Validity ────────────────────────────────────────────────
    story.append(Paragraph("6. Threats to Validity", S["h1"]))

    story.append(Paragraph("6.1 Internal Validity", S["h2"]))
    story.append(Paragraph(
        "<b>LLM nondeterminism.</b> Nemotron-Super-49B-v1.5 uses MoE routing that "
        "varies with server-side batching even at temperature=0. Identical "
        "(configuration, function) pairs produce ~2% fitness variation, violating "
        "the deterministic-fitness assumption and bounding the detectable GA advantage.",
        S["body"]))
    story.append(Paragraph(
        "<b>Small eval subset.</b> Configuration fitness is computed on "
        "eval_subset=5 functions per call. The GA searched against this noisy "
        "5-function signal; the held-out 50-function evaluation is more reliable "
        "but was not observed during the configuration search.",
        S["body"]))

    story.append(Paragraph("6.2 External Validity", S["h2"]))
    story.append(Paragraph(
        "<b>Single target model.</b> Results apply to one model "
        "(Nemotron-Super-49B-v1.5). Configuration landscapes may differ for other "
        "LLMs, limiting generalization of the evolved templates.",
        S["body"]))
    story.append(Paragraph(
        "<b>Synthetic references.</b> Reference summaries are Opus-generated, not "
        "human-written. Fitness measures configuration quality relative to Opus's "
        "style, not human judgment.",
        S["body"]))

    story.append(Paragraph("6.3 Construct Validity", S["h2"]))
    story.append(Paragraph(
        "<b>Fitness-quality alignment.</b> The blended fitness rewards surface "
        "similarity to Opus outputs. A configuration that paraphrases Opus's "
        "phrasing may score higher than a more accurate but lexically distinct one. "
        "Human evaluation is needed to validate that fitness gains correspond to "
        "genuine quality improvements.",
        S["body"]))

    # ── 7. Conclusion ─────────────────────────────────────────────────────────
    story.append(Paragraph("7. Conclusion and Future Work", S["h1"]))
    story.append(Paragraph(
        "We formulated LLM tool prompt configuration management as an SBSE problem "
        "and applied a Genetic Algorithm to search a 160,000-configuration space "
        "for an LLM-based code summarization tool. Against a budget-matched Random "
        "Search baseline over 10 independent trials, the GA demonstrated a "
        "suggestive but non-significant training-subset configuration quality "
        "advantage (p=0.082, Cliff's delta=+0.46). On a fully held-out 50-function "
        "test set the advantage did not hold (p=0.227, Cliff's delta=-0.32), "
        "indicating that the current budget and component bank ceiling prevent the "
        "GA's exploitation advantage from producing generalizable configurations.",
        S["body"]))
    story.append(Paragraph(
        "The central finding is that GA's benefit concentrates in "
        "<i>population-mean improvement</i>, reliably pushing the population away "
        "from low-quality configuration regions, rather than in discovering "
        "superior individual configurations. The bank's quality ceiling "
        "(~0.65-0.67 blended) and LLM nondeterminism (~0.02 per call) together "
        "suppress the GA-vs-RS best-of-trial gap below statistical detectability "
        "at n=10 trials.",
        S["body"]))
    story.append(Paragraph("Future work:", S["body"]))
    for item in [
        "(1) Expand the component bank with more diverse entries to widen the "
        "configuration fitness landscape.",
        "(2) Apply NSGA-II for multi-objective configuration optimization "
        "(output quality vs. prompt conciseness).",
        "(3) Use the LLM for directed configuration mutation (PromptBreeder-style) "
        "to escape the discrete bank constraint.",
        "(4) Human evaluation to validate that configuration fitness gains "
        "correspond to genuine summarization quality improvements.",
    ]:
        story.append(Paragraph(item, S["body_indent"]))

    # ── References ────────────────────────────────────────────────────────────
    story.append(Paragraph("References", S["h1"]))
    for r in [
        "[1] Harman, M., Jones, B.F. (2001). Search-based software engineering. "
        "<i>Information and Software Technology</i>, 43(14), 833-839.",
        "[2] McMinn, P. (2004). Search-based software test data generation: A survey. "
        "<i>Software Testing, Verification and Reliability</i>, 14(2), 105-156.",
        "[3] Fraser, G., Arcuri, A. (2011). EvoSuite: Automatic test suite generation "
        "for object-oriented software. <i>ESEC/FSE 2011</i>, 416-419.",
        "[4] Bagnall, A., Rayward-Smith, V., Whittley, I. (2001). The next release "
        "problem. <i>Information and Software Technology</i>, 43(14), 883-890.",
        "[5] O'Keeffe, M., O Cinnéide, M. (2008). Search-based refactoring for "
        "software maintenance. <i>Journal of Systems and Software</i>, 81(4), 502-516.",
        "[6] Zhou, Y., et al. (2022). Large language models are human-level prompt "
        "engineers. <i>arXiv:2211.01910</i>.",
        "[7] Fernando, C., et al. (2023). PromptBreeder: Self-referential self-improvement "
        "via prompt evolution. <i>arXiv:2309.16797</i>.",
        "[8] Romano, J., Kromrey, J. D., Coraggio, J., Skowronek, J. (2006). Appropriate "
        "statistics for ordinal level data: Should we really be using t-test and Cohen's d "
        "for evaluating group differences on the NSSE and other surveys? "
        "<i>Annual Meeting of the Florida Association of Institutional Research</i>.",
        "[9] Harman, M. (2010). The relationship between SBSE and emergent properties. "
        "<i>ICSE 2010</i>, 213-214.",
    ]:
        story.append(Paragraph(r, S["ref"]))

    return story


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Generating charts...")
    chart_figs = (fig_convergence(), fig_ga_vs_rs(), fig_cliffs_delta())

    out = os.path.abspath(OUTPUT)
    doc = SimpleDocTemplate(
        out, pagesize=letter,
        leftMargin=1.0*inch, rightMargin=1.0*inch,
        topMargin=1.0*inch,  bottomMargin=1.0*inch,
        title="Search-Based LLM Tool Configuration Management",
        author="Sean Lai, Anastasia Strulistova",
        subject="SBSE Final Project Report",
    )
    styles = build_styles()
    story  = make_story(styles, chart_figs)
    doc.build(story)
    print(f"PDF written to: {out}")


if __name__ == "__main__":
    main()

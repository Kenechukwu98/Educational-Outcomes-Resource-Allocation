"""
educational_analysis.py
================================================
Educational Outcomes & Resource Allocation
Full Statistical Analysis Pipeline

Dependencies:
    pip install pandas numpy scipy matplotlib seaborn openpyxl scikit-learn

Usage:
    python educational_analysis.py

Output files (saved to ./outputs/):
    - correlation_heatmap.png
    - scatter_str_vs_score.png
    - scatter_budget_vs_score.png
    - budget_tier_performance.png
    - regional_comparison.png
    - school_type_comparison.png
    - regression_summary.txt
    - analysis_report.csv
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score

warnings.filterwarnings("ignore")

# ── Config ──────────────────────────────────────────────────
DATA_PATH   = "educational_outcomes_dataset.xlsx"
SHEET_NAME  = "Student_Performance_Data"
OUTPUT_DIR  = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

PALETTE = {
    "navy":   "#1F4E79",
    "blue":   "#378ADD",
    "teal":   "#1D9E75",
    "amber":  "#BA7517",
    "coral":  "#D85A30",
    "purple": "#534AB7",
    "green":  "#639922",
    "gray":   "#888780",
}
REGION_COLORS = {
    "South": PALETTE["teal"],   "West":    PALETTE["blue"],
    "North": PALETTE["purple"], "Central": PALETTE["amber"],
    "East":  PALETTE["coral"],
}
TYPE_COLORS = {
    "Charter": PALETTE["purple"],
    "Private": PALETTE["blue"],
    "Public":  PALETTE["teal"],
}

# ── Global plot style ────────────────────────────────────────
plt.rcParams.update({
    "figure.dpi":       150,
    "font.family":      "DejaVu Sans",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.grid":        True,
    "grid.alpha":       0.3,
    "grid.linestyle":   "--",
    "axes.titlesize":   13,
    "axes.titleweight": "bold",
    "axes.labelsize":   10,
    "xtick.labelsize":  9,
    "ytick.labelsize":  9,
})


# ════════════════════════════════════════════════════════════
# 1. LOAD & VALIDATE DATA
# ════════════════════════════════════════════════════════════
def load_data(path: str, sheet: str) -> pd.DataFrame:
    print(f"\n{'='*60}")
    print("  EDUCATIONAL OUTCOMES — STATISTICAL ANALYSIS")
    print(f"{'='*60}")
    print(f"\n[1] Loading data from: {path}")
    df = pd.read_excel(path, sheet_name=sheet)
    print(f"    Shape     : {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"    Columns   : {', '.join(df.columns.tolist())}")
    print(f"    Nulls     : {df.isnull().sum().sum()} total missing values")
    print(f"    Duplicates: {df.duplicated().sum()} duplicate rows")
    return df


# ════════════════════════════════════════════════════════════
# 2. DESCRIPTIVE STATISTICS
# ════════════════════════════════════════════════════════════
NUMERIC_COLS = [
    "Student_Teacher_Ratio", "Budget_Per_Student_USD",
    "Teacher_Qualification_Pct", "Attendance_Rate_Pct",
    "Avg_Teacher_Experience_Yrs", "Computer_Student_Ratio",
    "Extracurricular_Programs", "Avg_Test_Score",
    "Graduation_Rate_Pct", "Pass_Rate_Pct",
    "STEM_Score", "Literacy_Score", "Dropout_Rate_Pct",
]

def descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    print("\n[2] Descriptive Statistics")
    print("─" * 60)
    desc = df[NUMERIC_COLS].describe().round(2)
    print(desc.to_string())
    return desc


# ════════════════════════════════════════════════════════════
# 3. CORRELATION ANALYSIS
# ════════════════════════════════════════════════════════════
CORR_COLS = [
    "Student_Teacher_Ratio", "Budget_Per_Student_USD",
    "Teacher_Qualification_Pct", "Attendance_Rate_Pct",
    "Avg_Teacher_Experience_Yrs", "Computer_Student_Ratio",
    "Extracurricular_Programs", "Avg_Test_Score",
    "Graduation_Rate_Pct", "Dropout_Rate_Pct",
]
CORR_LABELS = [
    "STR", "Budget", "Teacher Qual%", "Attendance",
    "Experience", "Comp Ratio", "Extracurr",
    "Test Score", "Grad Rate", "Dropout",
]

def correlation_analysis(df: pd.DataFrame) -> pd.DataFrame:
    print("\n[3] Correlation Analysis — vs Avg_Test_Score")
    print("─" * 60)
    corr_with_score = (df[NUMERIC_COLS]
                       .corr()["Avg_Test_Score"]
                       .drop("Avg_Test_Score")
                       .sort_values(key=abs, ascending=False)
                       .round(3))
    print(corr_with_score.to_string())

    # Pearson r + p-values
    print("\n  Pearson r  and  p-values:")
    for col in NUMERIC_COLS:
        if col == "Avg_Test_Score":
            continue
        r, p = stats.pearsonr(df[col], df["Avg_Test_Score"])
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"    {col:<35} r={r:+.3f}  p={p:.4f} {sig}")

    return df[CORR_COLS].corr()


def plot_heatmap(corr_matrix: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 7))
    mask = np.zeros_like(corr_matrix, dtype=bool)

    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    sns.heatmap(
        corr_matrix, annot=True, fmt=".2f", cmap=cmap,
        center=0, vmin=-1, vmax=1,
        xticklabels=CORR_LABELS, yticklabels=CORR_LABELS,
        linewidths=0.5, linecolor="#cccccc",
        ax=ax, annot_kws={"size": 8},
    )
    ax.set_title("Pairwise Correlation Matrix — Resource & Outcome Variables",
                 pad=12, fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right", fontsize=8)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "correlation_heatmap.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"\n  Saved → {path}")


# ════════════════════════════════════════════════════════════
# 4. SCATTER PLOTS — KEY RELATIONSHIPS
# ════════════════════════════════════════════════════════════
def scatter_with_regression(df, x_col, y_col, color, title, xlabel, ylabel, fname):
    fig, ax = plt.subplots(figsize=(8, 5))

    # Scatter
    ax.scatter(df[x_col], df[y_col],
               color=color, alpha=0.65, edgecolors="white",
               linewidths=0.4, s=60, zorder=3)

    # OLS regression line
    slope, intercept, r, p, se = stats.linregress(df[x_col], df[y_col])
    xs = np.linspace(df[x_col].min(), df[x_col].max(), 200)
    ax.plot(xs, slope * xs + intercept,
            color=PALETTE["navy"], linewidth=1.8, linestyle="--", zorder=4,
            label=f"OLS  r={r:.3f}  p={p:.4f}")

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=9)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, fname)
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {path}")
    return r, p


def scatter_plots(df: pd.DataFrame) -> None:
    print("\n[4] Scatter Plots — Key Relationships")
    print("─" * 60)

    pairs = [
        ("Student_Teacher_Ratio", "Avg_Test_Score",
         PALETTE["purple"], "Student–Teacher Ratio vs Avg Test Score",
         "Student–Teacher Ratio", "Avg Test Score",
         "scatter_str_vs_score.png"),
        ("Budget_Per_Student_USD", "Avg_Test_Score",
         PALETTE["teal"], "Budget per Student vs Avg Test Score",
         "Budget per Student (USD)", "Avg Test Score",
         "scatter_budget_vs_score.png"),
        ("Attendance_Rate_Pct", "Avg_Test_Score",
         PALETTE["amber"], "Attendance Rate vs Avg Test Score",
         "Attendance Rate (%)", "Avg Test Score",
         "scatter_attendance_vs_score.png"),
        ("Teacher_Qualification_Pct", "Avg_Test_Score",
         PALETTE["coral"], "Teacher Qualification % vs Avg Test Score",
         "Teacher Qualification (%)", "Avg Test Score",
         "scatter_qual_vs_score.png"),
    ]
    for x, y, c, title, xl, yl, fn in pairs:
        r, p = scatter_with_regression(df, x, y, c, title, xl, yl, fn)
        print(f"    {x:<35} → r={r:+.3f}, p={p:.4f}")


# ════════════════════════════════════════════════════════════
# 5. BUDGET TIER ANALYSIS
# ════════════════════════════════════════════════════════════
def budget_tier_analysis(df: pd.DataFrame) -> pd.DataFrame:
    print("\n[5] Budget Tier Analysis")
    print("─" * 60)

    bins   = [0, 3125, 4750, 6375, 10000]
    labels = ["Low\n$1.5k–$3.1k", "Mid-Low\n$3.1k–$4.7k",
              "Mid-High\n$4.7k–$6.3k", "High\n$6.3k–$8.0k"]
    df["Budget_Tier"] = pd.cut(df["Budget_Per_Student_USD"],
                                bins=bins, labels=labels, include_lowest=True)

    tier_stats = (df.groupby("Budget_Tier", observed=True)
                    [["Avg_Test_Score", "Graduation_Rate_Pct", "Pass_Rate_Pct"]]
                    .agg(["mean", "std", "count"])
                    .round(2))
    print(tier_stats.to_string())

    # Bar chart
    means = (df.groupby("Budget_Tier", observed=True)
               [["Avg_Test_Score", "Pass_Rate_Pct"]]
               .mean().round(2))

    fig, ax = plt.subplots(figsize=(8, 5))
    x    = np.arange(len(means))
    w    = 0.35
    b1   = ax.bar(x - w/2, means["Avg_Test_Score"], w,
                  color=PALETTE["blue"],  label="Avg Test Score",  alpha=0.9)
    b2   = ax.bar(x + w/2, means["Pass_Rate_Pct"],  w,
                  color=PALETTE["teal"],  label="Pass Rate (%)",   alpha=0.9)

    for bar in list(b1) + list(b2):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.5,
                f"{bar.get_height():.1f}",
                ha="center", va="bottom", fontsize=8, color="#333")

    ax.set_xticks(x)
    ax.set_xticklabels(means.index, fontsize=9)
    ax.set_ylim(55, 100)
    ax.set_ylabel("Score / Rate")
    ax.set_title("Performance by Budget Tier")
    ax.legend(fontsize=9)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "budget_tier_performance.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"\n  Saved → {path}")

    # ANOVA across tiers
    groups = [g["Avg_Test_Score"].values
              for _, g in df.groupby("Budget_Tier", observed=True)]
    F, p = stats.f_oneway(*groups)
    print(f"\n  One-way ANOVA (test score across budget tiers): F={F:.3f}, p={p:.5f}")
    return df


# ════════════════════════════════════════════════════════════
# 6. REGIONAL & SCHOOL-TYPE ANALYSIS
# ════════════════════════════════════════════════════════════
def regional_analysis(df: pd.DataFrame) -> None:
    print("\n[6] Regional Analysis")
    print("─" * 60)

    reg = (df.groupby("Region")
             [["Avg_Test_Score", "Graduation_Rate_Pct",
               "Budget_Per_Student_USD", "Dropout_Rate_Pct"]]
             .mean().round(2)
             .sort_values("Avg_Test_Score", ascending=False))
    print(reg.to_string())

    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = [REGION_COLORS.get(r, PALETTE["gray"]) for r in reg.index]
    bars = ax.barh(reg.index, reg["Avg_Test_Score"], color=colors, alpha=0.88, edgecolor="white")
    for bar, val in zip(bars, reg["Avg_Test_Score"]):
        ax.text(val + 0.2, bar.get_y() + bar.get_height()/2,
                f"{val:.1f}", va="center", fontsize=9)
    ax.set_xlim(70, 96)
    ax.set_xlabel("Avg Test Score")
    ax.set_title("Average Test Score by Region")
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "regional_comparison.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {path}")

    # ANOVA
    groups = [g["Avg_Test_Score"].values for _, g in df.groupby("Region")]
    F, p = stats.f_oneway(*groups)
    print(f"\n  One-way ANOVA (test score across regions): F={F:.3f}, p={p:.5f}")


def school_type_analysis(df: pd.DataFrame) -> None:
    print("\n[7] School Type Analysis")
    print("─" * 60)

    stype = (df.groupby("School_Type")
               [["Avg_Test_Score", "Graduation_Rate_Pct",
                 "Pass_Rate_Pct", "Dropout_Rate_Pct",
                 "Attendance_Rate_Pct", "STEM_Score", "Literacy_Score"]]
               .mean().round(2)
               .sort_values("Avg_Test_Score", ascending=False))
    print(stype.to_string())

    metrics = ["Avg_Test_Score", "Graduation_Rate_Pct", "Pass_Rate_Pct"]
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.5))
    for ax, metric in zip(axes, metrics):
        vals   = stype[metric]
        colors = [TYPE_COLORS.get(t, PALETTE["gray"]) for t in vals.index]
        bars   = ax.bar(vals.index, vals, color=colors, alpha=0.88, edgecolor="white")
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 0.3,
                    f"{bar.get_height():.1f}",
                    ha="center", va="bottom", fontsize=9)
        ax.set_title(metric.replace("_", " ").replace("Pct", "(%)"), fontsize=10)
        ax.set_ylim(vals.min() * 0.9, vals.max() * 1.05)
    plt.suptitle("Performance Metrics by School Type", fontsize=12, fontweight="bold", y=1.02)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "school_type_comparison.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {path}")


# ════════════════════════════════════════════════════════════
# 7. MULTIPLE LINEAR REGRESSION
# ════════════════════════════════════════════════════════════
FEATURES = [
    "Student_Teacher_Ratio",
    "Budget_Per_Student_USD",
    "Teacher_Qualification_Pct",
    "Attendance_Rate_Pct",
    "Computer_Student_Ratio",
    "Extracurricular_Programs",
    "Avg_Teacher_Experience_Yrs",
]
TARGET = "Avg_Test_Score"

def multiple_regression(df: pd.DataFrame) -> None:
    print("\n[8] Multiple Linear Regression")
    print("─" * 60)

    X = df[FEATURES].values
    y = df[TARGET].values

    # Standardise
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Fit
    model = LinearRegression()
    model.fit(X_scaled, y)
    y_pred = model.predict(X_scaled)

    r2  = r2_score(y, y_pred)
    mse = np.mean((y - y_pred) ** 2)
    rmse = np.sqrt(mse)

    print(f"\n  R²   = {r2:.4f}")
    print(f"  RMSE = {rmse:.3f}")
    print(f"  Intercept = {model.intercept_:.3f}")
    print("\n  Standardised Coefficients (feature importance):")
    coefs = sorted(zip(FEATURES, model.coef_), key=lambda x: abs(x[1]), reverse=True)
    for feat, coef in coefs:
        bar = "█" * int(abs(coef) * 4) + ("▲" if coef > 0 else "▼")
        print(f"    {feat:<35} β={coef:+.4f}  {bar}")

    # T-tests for each feature independently (simple bivariate)
    print("\n  Bivariate Pearson r + t-test (vs Avg_Test_Score):")
    for feat in FEATURES:
        r, p = stats.pearsonr(df[feat], df[TARGET])
        print(f"    {feat:<35} r={r:+.4f}  p={p:.5f}")

    # Save regression summary
    summary_lines = [
        "MULTIPLE LINEAR REGRESSION SUMMARY",
        "=" * 50,
        f"Target variable : {TARGET}",
        f"Features        : {len(FEATURES)}",
        f"Observations    : {len(df)}",
        f"R²              : {r2:.4f}",
        f"RMSE            : {rmse:.3f}",
        "",
        "Standardised Coefficients:",
    ]
    for feat, coef in coefs:
        summary_lines.append(f"  {feat:<35} β={coef:+.4f}")

    path = os.path.join(OUTPUT_DIR, "regression_summary.txt")
    with open(path, "w") as f:
        f.write("\n".join(summary_lines))
    print(f"\n  Saved → {path}")


# ════════════════════════════════════════════════════════════
# 8. EXPORT ANALYSIS SUMMARY CSV
# ════════════════════════════════════════════════════════════
def export_summary(df: pd.DataFrame) -> None:
    print("\n[9] Exporting Analysis Summary CSV")
    print("─" * 60)

    # Add derived columns
    df["Budget_Tier_Label"] = pd.cut(
        df["Budget_Per_Student_USD"],
        bins=[0, 3125, 4750, 6375, 10000],
        labels=["Low", "Mid-Low", "Mid-High", "High"],
        include_lowest=True,
    )
    df["STR_Tier"] = pd.cut(
        df["Student_Teacher_Ratio"],
        bins=[0, 10, 20, 35, 999],
        labels=["Excellent", "Good", "Average", "Poor"],
        include_lowest=True,
    )
    df["Score_Percentile"] = df["Avg_Test_Score"].rank(pct=True).round(3)
    df["At_Risk_Flag"] = (
        (df["Dropout_Rate_Pct"] > 10) & (df["Avg_Test_Score"] < 75)
    ).map({True: "YES", False: "no"})
    df["Composite_Score"] = (
        df["Avg_Test_Score"]    / 98.0 * 0.4
      + df["Graduation_Rate_Pct"] / 99.0 * 0.3
      + df["Pass_Rate_Pct"]    / 92.4 * 0.2
      + df["Attendance_Rate_Pct"] / 98.5 * 0.1
    ).round(4)

    out_cols = [
        "Student_ID", "School_Name", "Region", "School_Type", "Enrollment",
        "Budget_Per_Student_USD", "Budget_Tier_Label",
        "Student_Teacher_Ratio", "STR_Tier",
        "Teacher_Qualification_Pct", "Attendance_Rate_Pct",
        "Avg_Test_Score", "Score_Percentile",
        "Graduation_Rate_Pct", "Pass_Rate_Pct",
        "STEM_Score", "Literacy_Score", "Dropout_Rate_Pct",
        "Composite_Score", "At_Risk_Flag",
    ]
    path = os.path.join(OUTPUT_DIR, "analysis_report.csv")
    df[out_cols].to_csv(path, index=False)
    print(f"  Saved → {path}")
    print(f"  At-risk schools flagged: {(df['At_Risk_Flag']=='YES').sum()}")


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
def main():
    df = load_data(DATA_PATH, SHEET_NAME)
    descriptive_stats(df)
    corr_matrix = correlation_analysis(df)
    plot_heatmap(corr_matrix)
    scatter_plots(df)
    df = budget_tier_analysis(df)
    regional_analysis(df)
    school_type_analysis(df)
    multiple_regression(df)
    export_summary(df)

    print(f"\n{'='*60}")
    print("  Analysis complete. All outputs saved to ./outputs/")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

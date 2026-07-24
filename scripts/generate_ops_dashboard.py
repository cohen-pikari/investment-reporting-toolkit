"""
Investment Operations Daily MIS Dashboard Generator
------------------------------------------------------
Renders a management-facing visual summary of the day's reconciliation
run: total capital at risk, exception concentration by type, and
exception concentration by asset class. Reads directly from the
reconciliation output — fully generic to however many positions or
exception types are present, not hardcoded to specific tickers.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os


def generate_dashboard(exceptions_csv="output/exceptions_only.csv",
                        output_path="output/daily_ops_mis_dashboard.png"):
    if not os.path.exists(exceptions_csv):
        print(f"Error: {exceptions_csv} not found. Run reconciliation_engine.py first.")
        return

    df = pd.read_csv(exceptions_csv)

    total_risk = df["mv_variance"].abs().sum()
    total_exceptions = len(df)

    by_type = df.groupby("exception_type")["mv_variance"].apply(lambda x: x.abs().sum()).sort_values(ascending=False)
    by_asset_class = df["asset_class"].value_counts()

    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5))
    fig.suptitle(
        f"INVESTMENT OPERATIONS DAILY MIS DASHBOARD | {datetime.today().strftime('%Y-%m-%d')}\n"
        f"Total Capital At Risk: ${total_risk:,.2f}  |  Open Exceptions: {total_exceptions}",
        fontsize=14, fontweight="bold", color="#111111", y=0.98,
    )

    # Panel A: Capital at risk by exception type
    sns.barplot(x=by_type.values, y=by_type.index, ax=ax1, palette="Reds_r",
                hue=by_type.index, legend=False)
    ax1.set_title("Capital At Risk by Exception Type", fontsize=11, fontweight="bold", pad=10)
    ax1.set_xlabel("Absolute Variance ($ AUD)", fontsize=10)
    ax1.set_ylabel("")
    for i, v in enumerate(by_type.values):
        ax1.text(v, i, f" ${v:,.0f}", va="center", fontsize=9, fontweight="bold")

    # Panel B: Exception count by asset class
    sns.barplot(x=by_asset_class.values, y=by_asset_class.index, ax=ax2, palette="viridis",
                hue=by_asset_class.index, legend=False)
    ax2.set_title("Exception Volume by Asset Class", fontsize=11, fontweight="bold", pad=10)
    ax2.set_xlabel("Number of Open Exceptions", fontsize=10)
    ax2.set_ylabel("")
    ax2.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

    plt.tight_layout(rect=[0, 0, 1, 0.90])
    os.makedirs("output", exist_ok=True)
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"Dashboard generated: {output_path}")


if __name__ == "__main__":
    generate_dashboard()

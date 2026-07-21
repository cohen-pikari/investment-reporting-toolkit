import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# 1. Establish the operational data matrix from your live terminal test run
data = {
    'Ticker': ['AAPL', 'BHP.AX', 'ALT-VC-PRV'],
    'Security Name': ['Apple Inc.', 'BHP Group Limited', 'Collins St Private Equity'],
    'MV Variance': [146590.00, 77558.00, -25000.00],
    'Exception Type': ['PRICING_BREAK', 'PRICING_BREAK', 'ALTERNATIVES_VALUATION_LAG']
}

df = pd.DataFrame(data)
df['Absolute Variance'] = df['MV Variance'].abs()

# 2. Initialize visual canvas guidelines (High-density institutional styling)
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle(f"INVESTMENT OPERATIONS DAILY MIS DASHBOARD | {datetime.today().strftime('%Y-%m-%d')}\n"
             f"Total Net Portfolio Variance Exposure: ${df['MV Variance'].sum():,.2f}", 
             fontsize=14, fontweight='bold', color='#111111', y=0.98)

# Panel A: Absolute Financial Variance Magnitude Chart
colors = ['#d9534f' if val > 0 else '#f0ad4e' for val in df['MV Variance']]
sns.barplot(x='Ticker', y='Absolute Variance', data=df, ax=ax1, palette='Reds_r', hue='Ticker', legend=False)
ax1.set_title("Financial Variance Magnitude (Absolute Value)", fontsize=11, fontweight='bold', pad=10)
ax1.set_ylabel("Variance Value ($ AUD)", fontsize=10)
ax1.set_xlabel("Portfolio Ticker", fontsize=10)

# Format value bars cleanly with dollar amounts
for p in ax1.patches:
    ax1.annotate(f"${p.get_height():,.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                 ha='center', va='center', xytext=(0, 8), textcoords='offset points', fontsize=9, fontweight='bold')

# Panel B: Exception Type Concentration Metrics
exception_counts = df['Exception Type'].value_counts().reset_index()
exception_counts.columns = ['Exception Type', 'Count']
sns.barplot(x='Count', y='Exception Type', data=exception_counts, ax=ax2, palette='viridis', hue='Exception Type', legend=False)
ax2.set_title("Operational Exception Categorization Density", fontsize=11, fontweight='bold', pad=10)
ax2.set_xlabel("Number of Open Breaks", fontsize=10)
ax2.set_ylabel("")
ax2.set_xlim(0, 3)
ax2.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

plt.tight_layout(rect=[0, 0, 1, 0.90])

# 3. Export clean PNG artifact directly to your repository folder
output_path = "output/daily_ops_mis_dashboard.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"📊 S-Tier Operational Dashboard successfully generated and exported to: {output_path}")


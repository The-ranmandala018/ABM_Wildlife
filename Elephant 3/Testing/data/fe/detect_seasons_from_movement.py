# detect_seasons_from_movement.py
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster

# ------------------- Paths -------------------
RESULT_ROOT = Path("Detect Season")
RESULT_ROOT.mkdir(exist_ok=True)
FIG_ROOT = RESULT_ROOT / "figures"
FIG_ROOT.mkdir(exist_ok=True)

# ------------------- 1. Load data -------------------
df = pd.read_csv("Research Paper/LA11_behavior_classified.csv", parse_dates=['datetime'])
df = df.sort_values('datetime').reset_index(drop=True)

# THIS LINE WAS MISSING ←←←←←←←←←←←←←←←←←←←←←←←
df['date'] = df['datetime'].dt.date
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

# ------------------- 2. Daily behavior proportions -------------------
daily = df.groupby('date').agg(
    prop_resting=('behavior', lambda x: (x == 'resting').mean()),
    prop_foraging=('behavior', lambda x: (x == 'foraging').mean()),
    prop_walking=('behavior', lambda x: (x == 'walking').mean()),
    daily_km=('step_length', lambda x: x.sum() / 1000),
    n_fixes=('datetime', 'size')
).reset_index()

daily = daily.sort_values('date').reset_index(drop=True)
print(f"Daily behavior profiles: {len(daily)} days")

# ------------------- 3. Hierarchical clustering on behavior time series -------------------
X = daily[['prop_resting', 'prop_foraging', 'prop_walking']].values
Z = linkage(X, method='ward')

# Dendrogram — open this and decide how many seasons!
plt.figure(figsize=(16, 8))
dendrogram(Z, truncate_mode='level', p=6)
plt.title("Hierarchical Clustering of Daily Behavioral Profiles\n(Teimouri et al. 2018 — exact method)")
plt.xlabel("Day")
plt.ylabel("Ward Distance")
plt.axhline(y=1.3, color='red', linestyle='--', label='Try cutting here first')
plt.legend()
plt.tight_layout()
plt.savefig(FIG_ROOT / "dendrogram_behavioral_seasons.png", dpi=300, bbox_inches='tight')
plt.show()

# Choose number of seasons based on the dendrogram above
n_seasons = 6          # CHANGE THIS after looking at the plot!
daily['movement_season'] = fcluster(Z, t=n_seasons, criterion='maxclust')

# ------------------- 4. Extract contiguous seasons -------------------
periods = []
current_season = None
start_date = None

for _, row in daily.iterrows():
    if row['movement_season'] != current_season:
        if current_season is not None:
            periods.append({
                'season_id': f"Season_{current_season}",
                'start': start_date,
                'end': prev_date,
                'days': (prev_date - start_date).days + 1,
                'cluster': current_season
            })
        start_date = row['date']
        current_season = row['movement_season']
    prev_date = row['date']

# last period
periods.append({
    'season_id': f"Season_{current_season}",
    'start': start_date,
    'end': daily.iloc[-1]['date'],
    'days': (daily.iloc[-1]['date'] - start_date).days + 1,
    'cluster': current_season
})

seasons = pd.DataFrame(periods)
seasons = seasons[seasons['days'] >= 20]  # keep only meaningful seasons

# ------------------- 5. Save & plot -------------------
seasons.to_csv(RESULT_ROOT / "REAL_movement_defined_seasons.csv", index=False)
print("\nREAL MOVEMENT-DEFINED SEASONS (≥20 days):")
print(seasons[['season_id', 'start', 'end', 'days']])

# Plot
plt.figure(figsize=(16, 6))
colors = sns.color_palette("tab10", n_seasons)
for _, s in seasons.iterrows():
    plt.axvspan(s['start'], s['end'], color=colors[s['cluster']-1], alpha=0.4,
                label=s['season_id'] if s['season_id'] not in plt.gca().get_legend_handles_labels()[1] else "")

plt.plot(daily['date'], daily['daily_km'], 'k-', alpha=0.7, linewidth=1, label="Daily distance (km)")
plt.ylabel("Daily distance (km)")
plt.title(f"Elephant LA11 — {n_seasons} Movement-Defined Seasons\n(Hierarchical clustering of behavioral time series — no calendar used)")
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.savefig(FIG_ROOT / "movement_defined_seasons.png", dpi=300, bbox_inches='tight')
plt.show()

# Summary
summary = daily.groupby('movement_season')[['prop_resting','prop_foraging','prop_walking','daily_km']].mean()
summary['n_days'] = daily.groupby('movement_season').size()
print("\nBehavioral signature of each season:")
print(summary.round(3))
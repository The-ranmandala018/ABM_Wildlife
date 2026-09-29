import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.signal import find_peaks

RESULT_ROOT = Path("Wavelet")
RESULT_ROOT.mkdir(exist_ok=True)
FIG_ROOT = RESULT_ROOT / "figures"
FIG_ROOT.mkdir(exist_ok=True)

# ==================== 1. Load and prepare daily data ====================
df = pd.read_csv("results/tables/LA11_with_segments.csv", parse_dates=['datetime'])
df['date'] = df['datetime'].dt.floor('D')

daily = df.groupby('date').agg(
    daily_km=('step_length', lambda x: x.sum() / 1000),
    residence_time=('residence_time', 'mean')
).reset_index()

# Complete time series
full_dates = pd.date_range(start=daily['date'].min(), end=daily['date'].max(), freq='D')
daily = daily.set_index('date').reindex(full_dates)
daily[['daily_km', 'residence_time']] = daily[['daily_km', 'residence_time']].interpolate('linear')
daily = daily.reset_index().rename(columns={'index': 'date'})  # Correctly rename column

print(f"Final series: {len(daily)} days from {daily['date'].min().date()} to {daily['date'].max().date()}")

signal = daily['residence_time'].values.astype(float)
n = len(signal)

# ==================== 2. FULL CORRECT HAAR DWT (Sur et al. 2014) ====================
def haar_dwt_full_correct(signal, max_level=10):
    """Returns list of detail coeffs, each exactly length n"""
    s = signal.copy()
    details = []

    for level in range(max_level):
        # Pad to even length
        pad = 0
        if len(s) % 2 == 1:
            pad = 1
            s = np.append(s, s[-1])

        # Haar transform
        approx = (s[::2] + s[1::2]) / np.sqrt(2)
        detail = (s[::2] - s[1::2]) / np.sqrt(2)

        # Upsample detail back to original resolution (before padding)
        scale = 2 ** level
        upsampled = np.repeat(detail, scale)

        # Ensure upsampled is at least length n, pad if needed, then cut to n exactly
        if len(upsampled) < n:
            upsampled = np.append(upsampled, [upsampled[-1]] * (n - len(upsampled)))
        upsampled = upsampled[:n]

        # Remove padding artifact if any
        if pad and len(upsampled) > n:
            upsampled = upsampled[:-pad]

        details.append(upsampled)
        s = approx

    return details

details = haar_dwt_full_correct(signal, max_level=10)

# ==================== 3. Seasonal energy (levels 6–9 → 64–512 days) ====================
seasonal_energy = np.zeros(n)
for level in [5, 6, 7, 8]:  # levels 6–9 (0-indexed)
    seasonal_energy += np.abs(details[level])

# Smooth seasonal energy
seasonal_energy = np.convolve(seasonal_energy, np.ones(60) / 60, mode='same')

# ==================== 4. Detect peaks ====================
peaks, _ = find_peaks(seasonal_energy,
                      height=np.percentile(seasonal_energy, 89),
                      distance=110)

change_dates = daily.iloc[peaks]['date'].dt.strftime('%Y-%m-%d').tolist()

print(f"\nFULL HAAR DWT DETECTED {len(change_dates)} MAJOR SEASONAL TRANSITIONS:")
for i, d in enumerate(change_dates, 1):
    print(f"  {i}. {d}")

# ==================== 5. Build clean seasons ====================
boundaries = [daily['date'].iloc[0]] + daily.iloc[peaks]['date'].tolist() + [daily['date'].iloc[-1]]
seasons = []

for i in range(len(boundaries) - 1):
    start = boundaries[i]
    end = boundaries[i + 1]
    days = (end - start).days
    if days >= 80:
        seasons.append({
            'Season': f'Season_{i+1}',
            'Start': start.strftime('%Y-%m-%d'),
            'End': end.strftime('%Y-%m-%d'),
            'Days': days
        })

seasons_df = pd.DataFrame(seasons)
seasons_df.to_csv(RESULT_ROOT / "FINAL_HAAR_seasons.csv", index=False)

print("\nFINAL MOVEMENT-DEFINED SEASONS (Sur et al. 2014 method):")
print(seasons_df.to_string(index=False))

# ==================== 6. Plot ====================
plt.figure(figsize=(16, 10))

plt.subplot(3, 1, 1)
plt.plot(daily['date'], signal, 'steelblue', lw=1)
plt.ylabel("Residence Time (s)")
plt.title("Elephant LA11 – Full Discrete Haar Wavelet Decomposition (Sur et al. 2014)")

plt.subplot(3, 1, 2)
plt.plot(daily['date'], seasonal_energy, 'purple', lw=1.5)
for p in peaks:
    plt.axvline(daily.iloc[p]['date'], color='red', ls='--', lw=2)
plt.ylabel("Seasonal Wavelet Energy")
plt.title("Reconstructed Energy (Detail Levels 6–9)")

plt.subplot(3, 1, 3)
for i, s in seasons_df.iterrows():
    plt.axvspan(s['Start'], s['End'], color=f'C{i}', alpha=0.35,
                label=f"{s['Season']} ({s['Days']} days)")
plt.plot(daily['date'], daily['daily_km'], 'k-', lw=1.2)
plt.xlabel("Date")
plt.ylabel("Daily distance (km)")
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.savefig(FIG_ROOT / "FINAL_PERFECT_HAAR_seasons.png", dpi=300, bbox_inches='tight')
plt.show()

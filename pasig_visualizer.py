"""Script to visualize Pasig 2025 election results from CSV file
and generate bar charts of top candidates per contest.

Author: Your Name
Date: 2025
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

# ------------------------
# CONFIGURATION
# ------------------------

csv_file = "pasig_results.csv"
output_dir = "."

# ------------------------
# LOAD AND PROCESS DATA
# ------------------------

df = pd.read_csv(csv_file)

total_votes_per_candidate = df.groupby(['contest', 'candidate'], as_index=False).agg({
    'votes': 'sum',
    'percentage': 'mean'
})

total_votes_per_candidate['rank'] = total_votes_per_candidate.groupby('contest')['votes']\
    .rank(method='first', ascending=False)

top_candidates = total_votes_per_candidate[total_votes_per_candidate['rank'] <= 5]

key_contests = [
    "MAYOR of NCR - CITY OF PASIG",
    "VICE-MAYOR of NCR - CITY OF PASIG",
    "MEMBER, HOUSE OF REPRESENTATIVES of NCR - CITY OF PASIG - LONE LEGDIST",
    "SENATOR of PHILIPPINES"
]

filtered_top_candidates = top_candidates[top_candidates['contest'].isin(key_contests)]

# ------------------------
# VISUALIZATION
# ------------------------

plt.style.use('ggplot')

for contest in key_contests:
    if contest != "MEMBER, HOUSE OF REPRESENTATIVES of NCR - CITY OF PASIG - LONE LEGDIST":
        subset = filtered_top_candidates[filtered_top_candidates['contest'] == contest]
        subset = subset.sort_values('votes', ascending=True)
        labels = subset['candidate']
        values = subset['votes']
        percentages = subset['percentage']
    else:
        rep_candidates = df[df['contest'] == contest]
        subset = rep_candidates.groupby('candidate', as_index=False).agg({
            'votes': 'sum',
            'percentage': 'mean'
        }).sort_values(by='votes', ascending=True)
        labels = subset['candidate']
        values = subset['votes']
        percentages = subset['percentage']

    plt.figure(figsize=(12, 7))
    bars = plt.barh(labels, values, color='skyblue', edgecolor='black')

    for bar, vote, pct in zip(bars, values, percentages):
        width = bar.get_width()
        label = f"{int(vote):,} votes\n({pct:.1f}%)"
        plt.text(width + max(values)*0.005, bar.get_y() + bar.get_height()/2,
                 label, va='center', fontsize=9, color='black')

    plt.title(f"{contest}\nTop Candidates by Total Votes", fontsize=16, weight='bold')
    plt.xlabel("Total Votes", fontsize=12)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    plt.tight_layout()

    safe_name = contest.replace(' ', '_').replace(',', '').replace('/', '-')
    filename = os.path.join(output_dir, f"{safe_name}.png")
    plt.savefig(filename, dpi=300)
    print(f"Saved: {filename}")

    plt.show()

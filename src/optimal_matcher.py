import pandas as pd
import numpy as np
from scipy.optimize import linear_sum_assignment

# Load and preprocess data
df = pd.read_csv("data/sheet_data.csv")
columns = {
    'Full Name': 'name',
    'Gender': 'gender',
    'Gender Preference for Matching': 'preference',
    '💼 Career Ambition': 'career',
    '👨‍👩‍👧 Family-Oriented': 'family',
    '😂 Sense of Humor': 'humor',
    '🌍 Adventure Level': 'adventure',
    '🙏 Religious Views': 'religion',
    'Which of the following would be a deal-breaker for you?': 'dealbreakers'
}
df = df[list(columns.keys())].rename(columns=columns)
df.dropna(subset=['name', 'gender', 'preference'], inplace=True)
df.reset_index(drop=True, inplace=True)
participants = df.to_dict('records')
n = len(participants)

# Scoring function
def compute_score(p1, p2):
    if p1['preference'] != p2['gender'] or p2['preference'] != p1['gender']:
        return -np.inf
    score = 0
    for trait in ['career', 'family', 'humor', 'adventure', 'religion']:
        if pd.notna(p1[trait]) and pd.notna(p2[trait]):
            score += 5 - abs(p1[trait] - p2[trait])
    db1 = str(p1['dealbreakers']).lower().split(',')
    db2 = str(p2['dealbreakers']).lower().split(',')
    if any(term.strip() in str(p2['dealbreakers']).lower() for term in db1):
        score -= 3
    if any(term.strip() in str(p1['dealbreakers']).lower() for term in db2):
        score -= 3
    return score

# Build cost matrix
cost_matrix = np.full((n, n), 1e9)
for i in range(n):
    for j in range(i+1, n):
        score = compute_score(participants[i], participants[j])
        if score != -np.inf:
            cost_matrix[i, j] = -score
            cost_matrix[j, i] = -score

# Run Hungarian algorithm
row_ind, col_ind = linear_sum_assignment(cost_matrix)

# Track unique matches
matched = set()
final_matches = []
for i, j in zip(row_ind, col_ind):
    if i < j and i not in matched and j not in matched and cost_matrix[i][j] != 1e9:
        final_matches.append((participants[i]['name'], participants[j]['name'], int(-cost_matrix[i][j])))
        matched.update([i, j])

# Output to console
print("\n✅ Optimal Matches:")
for a, b, score in final_matches:
    print(f"{a} ❤️ {b} (Score: {score})")

# Save to matches.txt for email script
with open("data/matches.txt", "w") as f:
    for a, b, score in final_matches:
        f.write(f"{a}, {b}, {score}\n")

print("\n📄 Matches saved to matches.txt")

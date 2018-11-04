# Import packages
import pandas as pd
import numpy as np
import math

# Read in scores and data
score = pd.read_csv("data/score.csv")
score = score.drop(["region"], axis=1)

score_r = pd.read_csv("data/score.csv")
score_r = score_r.drop(["score"], axis=1)

games = pd.read_csv("data/games.csv")

# Define constants
k = 16

# Create tournament index (ADD WEEKEND AND NEW INDEX NUMBER)
conditions = [
    (games['date'] == '9/22/2018') | (games['date'] == '9/23/2018'),
    (games['date'] == '9/29/2018') | (games['date'] == '9/30/2018'),
    (games['date'] == '10/13/2018') | (games['date'] == '10/14/2018'),
    (games['date'] == '10/20/2018') | (games['date'] == '10/21/2018'),
    (games['date'] == '10/27/2018') | (games['date'] == '10/27/2018')]
choices = [1, 2, 3, 4, 5]
games['tournament'] = np.select(conditions, choices, 0)

# Loop on tournament index
for i in range(0, games['tournament'].max()):

    # Split on tournaments
    t = games[games["tournament"] == (i+1)]

    # Join Elo score
    t = t.join(score.set_index("team"), on="team_a")
    t.rename(columns={"score": "r_a", "region": "region"}, inplace=True)
    t = t.join(score.set_index("team"), on="team_b")
    t.rename(columns={"score": "r_b", "region": "region"}, inplace=True)

    # Create expected win probabilities
    t["e_a"] = 1/(1+10**((t["r_b"]-t["r_a"])/400))
    t["e_b"] = 1/(1+10**((t["r_a"]-t["r_b"])/400))

    # Join actual wins
    score["s"] = score["team"].map(t["winner"].value_counts()).fillna(0)

    # Join expected wins
    score["e"] = score["team"].map(t.groupby("team_a")["e_a"].sum()).fillna(0)
    score["e"] = score["e"] + score["team"].map(t.groupby("team_b")["e_b"].sum()).fillna(0)

    # Calculate new score
    score["new_score"] = score["score"] + k * (score["s"] - score["e"])

    # Drop interim columns
    score = score.drop(["s", "e", "score"], axis=1)
    score.rename(columns={'new_score':'score'}, inplace=True)

    # Sort by score
    score = score.sort_values(by=["score"], ascending=False)

# Join regions
score = score.join(score_r.set_index("team"), on="team")

# Split on region
score_east = score[score["region"] == "east"]
score_east = score_east.drop(["region"], axis=1)
score_west = score[score["region"] == "west"]
score_west = score_west.drop(["region"], axis=1)

# Export to CSV
score.to_csv("results/score_all.csv", index=False)
score_east.to_csv("results/score_east.csv", index=False)
score_west.to_csv("results/score_west.csv", index=False)

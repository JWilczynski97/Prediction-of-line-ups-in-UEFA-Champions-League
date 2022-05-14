# Copyright (c) Jakub Wilczyński 2021

# The first goal of this program was calculation of WhoScored.com effectiveness in prediction of managerial decisions in the UEFA Champions League
# matches of the seasons from 2010/2011 to 2019/2020. The second goal was setting the probability of performance for every player of team.
# The way of the calculation was described in README file of this project.

# tools import
import pandas as pd
from sklearn.metrics import accuracy_score

# data import
DATA_LOCATION = "../Databases/Data.csv"
data = pd.read_csv(DATA_LOCATION,
                      usecols=["Performance_ID", "Player_name", "Prev_1_start", "Prev_1_missing", "Prev_1_rating",
                               "Prev_1_diff_rival", "Prev_1_diff_best", "Prev_2_start", "Prev_2_missing",
                               "Prev_2_rating",
                               "Prev_2_diff_rival", "Prev_2_diff_best", "Prev_3_start", "Prev_3_missing",
                               "Prev_3_rating",
                               "Prev_3_diff_rival", "Prev_3_diff_best", "Prev_4_start", "Prev_4_missing",
                               "Prev_4_rating",
                               "Prev_4_diff_rival", "Prev_4_diff_best", "Prev_5_start", "Prev_5_missing",
                               "Prev_5_rating",
                               "Prev_5_diff_rival", "Prev_5_diff_best", "Prev_CL_start", "Prev_CL_missing",
                               "Prev_CL_rating",
                               "Missing", "Predicted", "Season_minutes", "Team_news", "Starting", "Team_ID"])

# index reset
data.reset_index(drop=True, inplace=True)
data.index += 1
data = data[data["Prev_5_start"] != 99]

# effectiveness of prediction from WhoScored.com experts
# 82.51 % - this is a percentage of WhoScored.com good types
# This value is considered as a percentage chance what WhoScored.com gives each player present in the predicted squads.
whoscored_effectiveness = round(float(accuracy_score(data['Starting'], data['Predicted'])), 5)
data['WhoScored_Prediction'] = data['Predicted']
data['WhoScored_Prediction'].replace(1, whoscored_effectiveness, inplace=True)  # set 0% chance for player if he is not present in the predicted squad

# chance for a performance of player if he is not present in the predicted squad
inefficiency = 1 - whoscored_effectiveness         # 17.49 %
for team in pd.unique(data['Team_ID']):
    team_players = [player for index, player in data[data["Team_ID"] == team].iterrows() if player['Missing'] != 2]
    N = len(team_players)
    players_not_predicted = [player["Performance_ID"] for player in team_players if player["WhoScored_Prediction"] == 0]
    for performance in players_not_predicted:
        data.loc[data.Performance_ID == performance, "WhoScored_Prediction"] = round(11 * inefficiency / (N - 11), 5)

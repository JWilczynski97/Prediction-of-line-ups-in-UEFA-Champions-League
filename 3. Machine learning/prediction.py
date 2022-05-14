# Copyright (c) Jakub Wilczyński 2021

# Machine Learning algorithms
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor

# LogLoss - cost function to evaluate the effectiveness of algorithms and WhoScored.com experts
from sklearn.metrics import log_loss

# other tools import
import pandas as pd
from statistics import mean
import warnings
from sklearn.model_selection import train_test_split
from sklearn.exceptions import DataConversionWarning

warnings.filterwarnings(action='ignore', category=DataConversionWarning)

# data import from .csv file
data = pd.read_csv("../Data.csv",
                    usecols=["Performance_ID", "Player_name", "Prev_1_start", "Prev_1_missing", "Prev_1_rating",
                             "Prev_1_diff_rival", "Prev_1_diff_best", "Prev_2_start", "Prev_2_missing", "Prev_2_rating",
                             "Prev_2_diff_rival", "Prev_2_diff_best", "Prev_3_start", "Prev_3_missing", "Prev_3_rating",
                             "Prev_3_diff_rival", "Prev_3_diff_best", "Prev_4_start", "Prev_4_missing", "Prev_4_rating",
                             "Prev_4_diff_rival", "Prev_4_diff_best", "Prev_5_start", "Prev_5_missing", "Prev_5_rating",
                             "Prev_5_diff_rival", "Prev_5_diff_best", "Prev_CL_start", "Prev_CL_missing", "Prev_CL_rating",
                             "Missing", "Predicted", "WhoScored_Prediction", "Season_minutes", "Team_news", "Starting", "Team_ID"])

# index reset
data.reset_index(drop=True, inplace=True)
data.index += 1

# learning dataset
X = data.drop(['Starting'], axis=1)
y = data[["Starting"]]

# lists for results
ws_results = []
tree_results = []
rf_results = []
knn_results = []
svm_results = []

# the result will be average of 100 different examples/datasets
for i in range(1, 101):
    print(f'{i} --------------------------')

    # division into training (85% of dataset) and test data (15%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15)

    whoscored_prediction = X_test['WhoScored_Prediction']

    # data cleaning (dropping the unnecessary columns)
    X_test_with_names = X_test
    X_train = X_train.drop(["Performance_ID", "Player_name", 'WhoScored_Prediction', "Team_ID"], axis=1)
    X_test = X_test.drop(["Performance_ID", "Player_name", 'WhoScored_Prediction', "Team_ID"], axis=1)

    """ WhoScored predictions """
    ws_loss = log_loss(y_test, whoscored_prediction)
    print(f'LogLoss for WhoScored: {round(ws_loss, 3)}')
    ws_results.append(ws_loss)

    """ DECISION TREE """
    tree = DecisionTreeRegressor(criterion='mse', max_depth=6)
    tree.fit(X_train, y_train)
    tree_pred = tree.predict(X_test)
    tree_loss = log_loss(y_test, tree_pred)

    print(f'LogLoss for Decision Tree: {round(tree_loss, 3)}')
    tree_results.append(tree_loss)

    """ RANDOM FOREST """
    random_forest = RandomForestRegressor(n_estimators=137, bootstrap=True, max_depth=6)
    random_forest.fit(X_train, y_train)
    random_forest_pred = random_forest.predict(X_test)
    random_forest_loss = log_loss(y_test, random_forest_pred)
    print(f'LogLoss for Random forest: ', round(random_forest_loss, 3))
    rf_results.append(random_forest_loss)

    """ K Neighbors """
    knn = KNeighborsRegressor(n_neighbors=6, weights='distance', p=1)
    knn.fit(X_train, y_train)
    knn_pred = knn.predict(X_test)
    knn_loss = log_loss(y_test, knn_pred)
    print("Log Loss for KNN: ", round(knn_loss, 3))
    knn_results.append(knn_loss)

    """ SVR """
    svm = SVR(kernel='rbf', C=0.01, epsilon=0.1, gamma='scale')
    svm.fit(X_train, y_train)
    svm_pred = svm.predict(X_test)
    svm_loss = log_loss(y_test, svm_pred)
    print("Log Loss for SVR: ", round(svm_loss, 3))
    svm_results.append(svm_loss)

print(f"Average effectiveness: ")
print(f"- WhoScored.com: {mean(ws_results)}")
print(f"- Decision Tree: {mean(tree_results)}")
print(f"- Random Forest: {mean(rf_results)}")
print(f"- KNN:           {mean(knn_results)}")
print(f"- SVM:           {mean(svm_results)}")

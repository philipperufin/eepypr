import pandas as pd

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics

csv_path = r'C:\Users\geo_phru\Desktop\GAP\turkey_val\vali_4326_stm.csv'

df = pd.read_csv(csv_path)
df['id']

Y = df['ID']
X = df.drop('ID', axis=1)

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state=86)

param_grid = {'n_estimators': [100, 250, 500],
              'max_features': ['auto', 'sqrt'],
              'min_samples_split': [2, 4, 6, 8],
              'min_samples_leaf': [2, 4, 6, 8]}

rf = RandomForestClassifier(oob_score=True)
clf = GridSearchCV(rf, param_grid, cv=5, verbose=50, n_jobs=4)
clf.fit(X_train, y_train)


print(clf.best_params_)

rf_best = clf.best_estimator_
rf_y_train_pred = rf_best.predict(X_train)
rf_y_test_pred = rf_best.predict(X_test)
import ee
import datetime
import fct.stm

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics

ee.Initialize()

#### get stm values from point shape
point_shape = r'C:\Users\geo_phru\Desktop\GAP\turkey_val\vali_gh_4326.shp'
startDate = datetime.datetime(2015, 7, 1)
endDate = datetime.datetime(2019, 9, 30)
out_path = r'C:\Users\geo_phru\Desktop\GAP\turkey_val\vali_4326_stm.csv'

df = fct.stm.STM_CSV(point_shape, startDate, endDate, False, out_path)

# initiate target (Y) and predictor (X) variables
Y = df['class']
X = df.drop('class', axis=1)

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state=86)

# gridsearch
param_grid = {'n_estimators': [100, 250, 500],
              'max_features': ['auto', 'sqrt'],
              'min_samples_split': [2, 4, 6, 8],
              'min_samples_leaf': [2, 4, 6, 8]}

rf = RandomForestClassifier(oob_score=True)
clf = GridSearchCV(rf, param_grid, cv=5, verbose=50, n_jobs=40)
clf.fit(X_train, y_train)


print(clf.best_params_)

rf_best = clf.best_estimator_
rf_y_train_pred = rf_best.predict(X_train)
rf_y_test_pred = rf_best.predict(X_test)
import pandas as pd
import geopandas
import glob
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics


csv_path = r'C:\Users\geo_phru\Desktop\SUSADICA\r1'
csv_s1 = glob.glob(csv_path + '\*\*s1.csv')
csv_s2 = glob.glob(csv_path + '\*\*s2.csv')

# season 1 STMs
for i, f in enumerate(csv_s1):
    print(f)
    if i == 0:
        df_s1 = pd.read_csv(f)
        gp_s1 = geopandas.read_file(f[:-14] + '.shp')

        if 'poly_ID' in gp_s1.columns:
            gp_s1 = gp_s1.drop('poly_ID', axis=1)


    if i > 0:
        add_df = pd.read_csv(f)
        add_gp = geopandas.read_file(f[:-14] + '.shp')

        if 'poly_ID' in add_gp.columns:
            add_gp = add_gp.drop('poly_ID', axis=1)

        df_s1 = df_s1.append(add_df)
        gp_s1 = gp_s1.append(add_gp, sort=True)

# season 2 STMs
for i, f in enumerate(csv_s2):
    print(f)
    if i == 0:
        df_s2 = pd.read_csv(f)

    if i > 0:
        add_df = pd.read_csv(f)
        df_s2 = df_s2.append(add_df)

# clean up
df_s1 = df_s1.drop(['id', 'longitude', 'latitude', 'time'], axis=1)
df_s1.columns = df_s1.columns + '_s1'
df_s1 = df_s1.rename(columns={'ID_s1':'ID'})

df_s2 = df_s2.drop(['id', 'longitude', 'latitude', 'time'], axis=1)
df_s2.columns = df_s2.columns + '_s2'
df_s2 = df_s2.rename(columns={'ID_s2':'ID'})

gp_s1 = gp_s1[['ID', 'class', 'year']]

# merge dataframes
df_yr = df_s1.merge(df_s2, left_index=True, right_index=True)
df_cy = df_yr.merge(gp_s1, left_index=True, right_index=True)

# write to csv
df_cy.to_csv(csv_path+r'\stm_s1_s2_r1.csv')


# prep for rf
df = df_cy
df.columns
y = df['class']
x = df.drop(['ID_y', 'ID', 'class', 'year'], axis=1)

xcal, xval, ycal, yval = train_test_split(x, y, test_size=0.33, random_state=86)

param_grid = {'n_estimators': [100, 250, 500],
              'max_features': ['auto', 'sqrt'],
              'min_samples_split': [2, 4, 6, 8],
              'min_samples_leaf': [2, 4, 6, 8]}

rf = RandomForestClassifier(oob_score=True)
clf = GridSearchCV(rf, param_grid, cv=5, verbose=50, n_jobs=4)

clf.fit(xcal, ycal)
print(clf.best_params_)

rf_best = clf.best_estimator_
rf_y_train_pred = rf_best.predict(X_train)
rf_y_test_pred = rf_best.predict(X_test)
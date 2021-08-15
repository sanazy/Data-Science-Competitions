# -*- coding: utf-8 -*-
"""QueraConnect_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fQ01CesYM87b6nk18dYIlF53g7k6h_sd
"""

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# !pip install catboost
# !pip install optuna

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

import optuna
import catboost as cb
from catboost import Pool, CatBoostClassifier

from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, matthews_corrcoef, f1_score
from sklearn.metrics import classification_report

df_train = pd.read_csv('train.csv')
df_test = pd.read_csv('test.csv')

def feature_engineering(df, isTrain):
  # replace playType values
  df['playType'] = df['playType'].replace(['جریان بازی','ضربه آزاد مستقیم','پنالتی','مستقیم از کرنر'],
                                        ['game','free','penalty','corner'])
  # replace bodyPart values 
  df['bodyPart'] = df['bodyPart'].replace(['پای راست','پای چپ','سر','سایر'],
                                          ['right','left','head','other'])
  # replace interferenceOnShooter values
  df['interferenceOnShooter'] = df['interferenceOnShooter'].replace(['متوسط','کم','زیاد'],
                                                                    [1, 0, 2])
  # replace NaN with mode in interferenceOnShooter column
  df['interferenceOnShooter'].fillna(df['interferenceOnShooter'].mode()[0], inplace=True)

  df['xy'] = df['x'] + df['y']
  df['inter'] = df['interveningOpponents'] + df['interveningTeammates'] + df['interferenceOnShooter']
  
  # if dataframe is for training
  if isTrain:
    # replace playType values
    df['outcome'] = df['outcome'].replace(['موقعیت از دست رفته','مهار توسط دروازه بان','برخورد به دفاع','گُل','برخورد به تیردروازه','گُل به خودی'],
                                          [0, 0, 0, 1, 0, 1])
    # drop columns
    df.drop(['matchId', 'playerId'], inplace = True, axis = 1)  
  
  return df

df_train = feature_engineering(df_train, True)
df_test  = feature_engineering(df_test, False)

# define target column
target = 'outcome'

# define categorical columns
cat_train = df_train[['playType', 'bodyPart']] 
cat_test  = df_test[['playType', 'bodyPart']] 

# define features
X = df_train.loc[:, df_train.columns != target]

# define label 
y = df_train[target]

# separate train from validation and test sets
X_train, X_val, y_train, y_val = train_test_split(X,
                                                  y,
                                                  stratify = y,
                                                  random_state = 1,
                                                  test_size = 0.2)
# define features test
X_test = df_test

"""***
# Hyper parameter tuning
"""

def objective(trial):
  # parameters
  param = {
      "objective": trial.suggest_categorical("objective", ["Logloss"]),
      "colsample_bylevel": trial.suggest_float("colsample_bylevel", 0.01, 0.1),
      "depth": trial.suggest_int("depth", 1, 12),
      "boosting_type": trial.suggest_categorical("boosting_type", ["Ordered", "Plain"]),
      "bootstrap_type": trial.suggest_categorical(
          "bootstrap_type", ["Bayesian", "Bernoulli", "MVS"]
      ),
      "used_ram_limit": "3gb"
  }

  if param["bootstrap_type"] == "Bayesian":
      param["bagging_temperature"] = trial.suggest_float("bagging_temperature", 0, 10)
  elif param["bootstrap_type"] == "Bernoulli":
      param["subsample"] = trial.suggest_float("subsample", 0.1, 1)

  # catboost model
  model = cb.CatBoostClassifier(**param, 
                                cat_features = cat_train, 
                                class_weights = [0.15, 0.85])
  # train model
  model.fit(X_train, 
            y_train, 
            eval_set = [(X_val, y_val)], 
            verbose = 0, 
            early_stopping_rounds = 10)

  # predict
  preds = model.predict(X_val)
  pred_labels = np.rint(preds)

  # metric
  fpr_train, tpr_train, thresh_train = metrics.roc_curve(y_val, pred_labels)
  auc = metrics.auc(fpr_train, tpr_train)

  return auc

# optuna optimization
study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=10, timeout=600)

# best trail result
print("Number of finished trials: {}".format(len(study.trials)))
print("Best trial:")
trial = study.best_trial

print("  Value: {}".format(trial.value))
print("  Params: ")
for key, value in trial.params.items():
    print("    {}: {}".format(key, value))

"""***
#Train with best Hyperparameters
"""

# concatenate train and validation sets for training
X_trainval = pd.concat([X_train, X_val], axis=0, ignore_index=False, sort=False)
y_trainval = pd.concat([y_train, y_val], axis=0, ignore_index=False, sort=False)

train_dataset = Pool(data = X_trainval, 
                     label = y_trainval,
                     cat_features = cat_train)

test_dataset = Pool(data = X_test, 
                    cat_features = cat_test)

model = CatBoostClassifier(
    colsample_bylevel= 0.07,
    depth= 7,
    boosting_type= 'Ordered',
    bootstrap_type= 'Bernoulli',
    subsample= 0.43,
    iterations = 500, 
    class_weights = [0.15, 0.85],
    loss_function = 'Logloss',
    early_stopping_rounds = 5)

model.fit(train_dataset)

"""***
# Feature Importance
"""

def plot_feature_importance(importance, names):
    
    # Create arrays from feature importance and feature names
    feature_importance = np.array(importance)
    feature_names = np.array(names)
    
    # Create a DataFrame using a Dictionary
    data = {'feature_names':feature_names, 'feature_importance':feature_importance}
    fi_df = pd.DataFrame(data)
    
    # Sort the DataFrame in order decreasing feature importance
    fi_df.sort_values(by=['feature_importance'], ascending=False,inplace=True)
    
    # Define size of bar plot
    plt.figure(figsize=(10,8))
    # Plot Searborn bar chart
    sns.barplot(x=fi_df['feature_importance'], y=fi_df['feature_names'])
    # Add chart labels
    plt.title('FEATURE IMPORTANCE')
    plt.xlabel('FEATURE IMPORTANCE')
    plt.ylabel('FEATURE NAMES')

# plot the feature importance plot
plot_feature_importance(model.get_feature_importance(train_dataset), X_train.columns)

"""***
# Prediction
"""

preds_proba = model.predict_proba(test_dataset)
preds = pd.DataFrame(preds_proba)
preds[1].to_csv('output.csv', index=False, header=['prediction'])
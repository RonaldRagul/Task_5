# -*- coding: utf-8 -*-
"""Task_5.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YqqMRymyVNmD1Vbc-dMICSN832-zUGf7
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

user =pd.read_csv('takehome_users.csv',encoding='latin-1')
user.head()

user.isnull().sum()

user["last_session_creation_time"].fillna(0,inplace=True)
user['invited_by_user_id'].fillna(0,inplace=True)
user.isnull().sum()

user.info()

user.describe()

user.dtypes

user.head()

user_eng =pd.read_csv('takehome_user_engagement.csv')
user_eng.isnull().sum()

user_eng.dtypes

user_eng.head()

#total time of visit
user_eng.visited.count()

#total users
len(user_eng.user_id.unique())

"""**this is shown us some users are visited many times with same user id**"""

user.head()

df = user.email.value_counts().to_frame()
temp_list = list(df[df.email==2].index)
user[user.email.isin(temp_list)].sort_values(by='email').head()

"""**here we see some mail id's are repeted twice**"""

user_eng.tail(10)

#visited column has same values so drop it
user_eng.drop(["visited"],axis=1,inplace=True)

user_eng["time_stamp"]= pd.to_datetime(user_eng.time_stamp)

# Adding org_size for knowing the no of users in oraganization
temp = user.org_id.value_counts()
user['org_size'] = [temp[i] for i in user.org_id]
# Adding referred to know whether the user was invited to sign then true else false.
user['referred'] = user.invited_by_user_id!=0
user

"""**if a user visited more than 3 days a week,he known as a adopted user.so we'll add a column with boolean value**"""

#7_day_visit
def get_visit_count(grp, freq):
    return grp.rolling(freq, on='time_stamp')['user_id'].count()

user_eng['7_day_visit'] = user_eng.groupby('user_id', as_index=False, group_keys=False).apply(get_visit_count, '7D')
#adopted user
df_adopted = user_eng.groupby('user_id')['7_day_visit'].max().to_frame().reset_index()
df_adopted['adopted_user'] = (df_adopted['7_day_visit']>2)
df_adopted.head()

df = pd.merge(user,df_adopted,how ='outer',left_on='object_id', right_on='user_id').drop(['user_id','7_day_visit'],axis=1)

df

df.adopted_user.fillna(False,inplace=True)

# Adding one more column for checking if the reference user is adopted
df = pd.merge(df,df[['object_id','adopted_user']], how='left',left_on='invited_by_user_id',right_on='object_id')
df.drop('object_id_y',axis=1,inplace=True)
df.rename(columns={'object_id_x':'object_id','adopted_user_x':'adopted_user','adopted_user_y':'adopted_reference'},inplace=True)
df.adopted_reference.fillna(False,inplace=True)
df.head()

sns.countplot(x="creation_source", data=df,hue='adopted_user',palette=['red','green'])
plt.xticks(rotation=60)

df.drop(['object_id','creation_time','name','email','last_session_creation_time',],axis=1,inplace=True)

df_users = pd.get_dummies(df)
df_users.head()

X = df_users.drop(labels=['adopted_user'],axis=1)
y = df_users.adopted_user

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

# Applying SelectKBest class to score the 12 features
bestfeatures = SelectKBest(score_func=chi2, k=12)
fit = bestfeatures.fit(X,y)
dfscores = pd.DataFrame(fit.scores_)
dfcolumns = pd.DataFrame(X.columns)

# Concatenating two dataframes for better visualization 
featureScores = pd.concat([dfcolumns,dfscores],axis=1)
featureScores.columns = ['Specs','Score']
print(featureScores.nlargest(12,'Score'))

from sklearn.ensemble import ExtraTreesClassifier

model = ExtraTreesClassifier()
model.fit(X,y)
print(model.feature_importances_)

# Plotting graph of feature importances for better visualization
feat_importances = pd.Series(model.feature_importances_, index=X.columns)
feat_importances.nlargest(12).plot(kind='barh')
plt.show()

"""From the above heatmap, and the p-values, the important features are org_id, org_size, invited_by_user_id, referred, adopted_reference, creation_source_PERSONAL_PROJECTS.

so we can conclude that the most important features are org_id, org_size, invited_by_user_id.
"""
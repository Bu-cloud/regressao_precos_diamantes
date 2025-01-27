# -*- coding: utf-8 -*-
"""diamantes.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ukPf7bGZeVOHeD_e319EQ58kjNq-xCjl

# Regressão de preços de diamantes
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('diamonds.csv')

df.info()

df.isna().sum()

df.head()

df.describe()

df['color'].value_counts()

plt.hist(df['carat'])
plt.show()

n_ca = df[df['carat']>=3.25]
plt.hist(n_ca['carat'])
plt.show()

plt.boxplot(df['price'])
plt.show()

# Gráfico de quartis de table para observar os outliers
plt.boxplot(df['table'])
plt.show()

# Retira a coluna de índice
df.drop('Unnamed: 0',axis=1,inplace=True)

#  Ver valores de dimensão igual a zero
df[df['x']==0]
df[df['y']==0]
df[df['z']==0]

# Excluir valores de dimensão igual a zero e outliers
df = df[df['z']!=0]
df = df[df['z']<30]
df = df[df['y']<30]
# Renumerar as linhas
df = df.reset_index()

# profundidade calculada esperada
calc_depth = (100*2*df['z'])/(df['x']+df['y'])
count=0
for i in range(df.shape[0]):
  # limite de 10% de diferença entre o cálculo e o dado no dataset
  threshold = df['depth'][i]*0.1
  if df['depth'][i] > calc_depth[i]+threshold or df['depth'][i] < calc_depth[i]-threshold:
    count+=1
print("profundidade errada acima de 10%:",count)

"""Não faz sentido os diamantes terem dimensões zero, assim, eles serão excluídos por serem poucas linhas. Os valores muito extremos de y e z também serão excluídos."""

# Criando um dataset com os valores de dimensão acima do limite para análise

# Quantidade de linhas do dataset original
m,_ = df.shape
# Inicializa o novo dataset
subset_depth = pd.DataFrame()
x = list()
y = list()
z = list()
de = list()
cde = list()
# Percorre as linhas
for i in range(m):
  # limite de 10% de diferença entre o cálculo e o dado no dataset
  threshold = df['depth'][i]*0.1
  d = df['depth'][i]
  c = calc_depth[i]
  # Se a profundidade original no dataset está 10% acima ou abaixo da calculada, adiciona as dimensões e profundiades às listas rre
  if d > c+threshold or d < c-threshold:
    x.append(df['x'][i])
    y.append(df['y'][i])
    z.append(df['z'][i])
    de.append(d)
    cde.append(c)
# Junta as listas em forma de colunas do novo dataset
subset_depth = pd.concat([pd.Series(x),pd.Series(y),pd.Series(z),pd.Series(de),pd.Series(cde)],axis=1)

# Após observar o dataset, os valores mais próximos a 1 mm na dimensão z foram removidos por estarem abaixo do quartil 25%
print(df[df['z']==1.07]) #linha 14627
print(df[df['z']==1.41]) # linha 21645
print(df[df['z']==1.53])

# depois de confirmar que havia apenas uma linha com esses valores, retirei do dataset
df.drop([14627,21645,20685],inplace=True)

# Observando o outlier do valor máximo
df[df['table']==95]

# Observando table em diamantes com dimensões semelhantes - entre 8 e 10 mm
df[(df['x']>8) & (df['x']<10) & (df['y']>8) & (df['y']<10)]

# Mediana dos valores de table
subs = df[(df['x']>8) & (df['x']<10) & (df['y']>8) & (df['y']<10)]['table'].median()

# Substitui o outlier table pela mediana
df.loc[24920,'table'] = subs

# Valores abaixo de 25% de todos os valores de table
q1_table = df['table'].quantile(0.25)
# Valores abaixo de 75% de todos os valores de table
q3_table = df['table'].quantile(0.75)
# Intervalo interquartil
iqr_t = q3_table - q1_table
# Conta os outliers segundo o método dos quartis

print("Total de outliers de table:",df[df['table']>q3_table+1.5*iqr_t].count()+df[df['table']<q1_table-1.5*iqr_t].count())

# Outliers superiores
out_s = q3_table+1.5*iqr_t
# Outliers inferiores
out_i = q1_table-1.5*iqr_t
# Remove os outliers de table
df.drop(df[df.table > out_s].index, inplace=True)
df.drop(df[df.table < out_i].index, inplace=True)

"""Observando o subset acima, é provável que o valor de table de 95 provavelmente foi um erro de digitação, assim, ele será substituído pela mediana.Essas linhas representam cerca de 1.1% do dataset e serão removidas

"""

df.reset_index(drop=True,inplace=True)

"""# Modelo"""

print("zeroz x:",df[df['x']==0]['x'].count())
print("zeros y:",df[df['y']==0]['y'].count())
print("zeros z:",df[df['z']==0]['z'].count())

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

X_train,X_test,y_train,y_test = train_test_split(df.drop(['price'],axis=1),df['price'],test_size=0.2,random_state=42)

stdscaler = StandardScaler()

oe = OrdinalEncoder(dtype=int)
color_cat = ['J','I','H','G','F','E','D']
df['color'] = oe.fit_transform(np.array(df['color']).reshape(-1,1))

cut_cats = ['Fair','Good','Very Good','Ideal','Premium']
oe_cut = OrdinalEncoder(categories=[cut_cats],dtype=int)
df['cut'] = oe_cut.fit_transform(np.array(df['cut']).reshape(-1,1))

clarity_cats = ['I1','SI2','SI1','VS2','VS1','VVS2','VVS1','IF']
oe_cl = OrdinalEncoder(categories=[clarity_cats],dtype=int)
df['clarity'] = oe_cl.fit_transform(np.array(df['clarity']).reshape(-1,1))

df['clarity'].value_counts()

from sklearn import linear_model
from sklearn.preprocessing import MinMaxScaler
clf = linear_model.Lasso(alpha=0.1)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.fit_transform(X_test)
clf.fit(X_train,y_train)
y_pred = clf.predict(X_test)
erro = mean_squared_error(y_pred,y_test)
erro

import sklearn
sklearn.metrics.get_scorer_names()

from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import GridSearchCV
param_grid = {'max_depth':[5,8,10,12,15,20,22,25],
              'min_samples_leaf':[1,2,3,4]}

dt = DecisionTreeRegressor(random_state=42)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.fit_transform(X_test)
grid_search = GridSearchCV(estimator=dt,param_grid=param_grid,cv=5,n_jobs=-1,verbose=2,scoring='neg_mean_squared_error')
grid_search.fit(X_train,y_train)
best_rg = grid_search.best_estimator_
y_pred = best_rg.predict(X_test)
erro = mean_squared_error(y_test,y_pred)
erro

from sklearn.ensemble import HistGradientBoostingRegressor as GBR # é uma versão mais rápida do gradientboosting pra datasets com mais de 10000 linhas
gbr = GBR(random_state=42)
grid_search = GridSearchCV(estimator=gbr,param_grid=param_grid,cv=5,n_jobs=-1,verbose=2,scoring='neg_mean_squared_error')
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.fit_transform(X_test)
grid_search.fit(X_train,y_train)
best_rg = grid_search.best_estimator_
y_pred = best_rg.predict(X_test)
erro = mean_squared_error(y_test, y_pred)
erro
# estimadores: histgradientboostingregressor, param_grid = {'max_depth':[5,8,10,12,15,20,22,25],'min_samples_leaf':[1,2,3,4]}, cv=5, n_jobs=-1
# sem l2 reg: 267598 # com l2 reg: 273559
# gradient boost regressor: 271745
# com standard scaler e l2: 279172    sem l2: 277313

ridge=linear_model.Ridge(alpha=0.1)
 ridge.fit_intercept=True
 ridge.fit(X_train,y_train)
 y_pred = ridge.predict(X_test)
 erro = mean_squared_error(y_test,y_pred)
 erro

# Vamos fazer um gráfico para plotar os erros
# Estilo do gráfico
plt.style.use('fivethirtyeight')

# Erros no conjunto de treino
plt.scatter(best_rg.predict(X_train), best_rg.predict(X_train) - y_train,
            color = "green", s = 10, label = 'Dados de treino')

# Erros no conjunto de teste
plt.scatter(best_rg.predict(X_test), best_rg.predict(X_test) - y_test,
            color = "blue", s = 10, label = 'Dados de teste')

# Linha representando o erro 0
plt.hlines(y = 0, xmin = 0, xmax = 50, linewidth = 2)

# Legenda
plt.legend(loc = 'upper right')

# Título
plt.title("Erros Residuais")

# Mostra o gráfico
plt.show()

df_1 = pd.DataFrame({'Verdadeiros':y_test,'Preditos':y_pred})

plt.hist(y_test)

plt.hist(y_pred)

df_1
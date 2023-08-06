#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 13 21:51:33 2023

@author: muthyala.7
"""

import FeatureSpaceConstruction
import SISSORegressor
import torch
import numpy as np 
import pandas as pd 
import time


'''
########################################################################################################

CaseStudy - 1

#######################################################################################################
'''
x = [np.random.uniform(0,2,size=10) for i in range(4)]
df = pd.DataFrame()
for i in range(len(x)):
  variable = 'x'+str(i+1)
  df[variable] = x[i]
operators = ['+','/']
y = 5*((df.iloc[:,0])/(df.iloc[:,1]*(df.iloc[:,2]+df.iloc[:,3]))) + 3 + 0.01*np.random.normal(0,1,10)
df.insert(0,'Target',y)
df['x5'] = np.random.choice([0, 1], size=len(df), p=[0.50, 0.50])

start_c = time.time()
fc = FeatureSpaceConstruction.feature_space_construction(operators,df,3,'cuda')
df_created = fc.feature_space()
#Create Instace for class 
x = torch.tensor(df_created.iloc[:,1:].values)
y = torch.tensor(df_created.iloc[:,0])
names = df_created.iloc[:,1:].columns
start = time.time()
sr = SISSORegressor.SISSO_Regressor(x,y,names,1,5,'cuda')
sr.SISSO()
print('SISSO Completed',time.time()-start_c,'\n')
print('\n')

'''
###############################################################################################

CaseStudy -2 
###############################################################################################
'''

y1 = 3*np.sqrt(df.iloc[:,1]) + 2.5*np.sin(df.iloc[:,2]) + 2.5 + 0.05*np.random.normal(0,1,10)
df['Target'] = y1
operators = ['sqrt','sin']
start_c = time.time()
fc = FeatureSpaceConstruction.feature_space_construction(operators,df,3,'cuda')
df_created = fc.feature_space()
#Create Instace for class 
x = torch.tensor(df_created.iloc[:,1:].values)
y = torch.tensor(df_created.iloc[:,0])
names = df_created.iloc[:,1:].columns
start = time.time()
sr = SISSORegressor.SISSO_Regressor(x,y,names,2,5,'cuda')
sr.SISSO()
print("SISSO Completed: ",time.time()-start_c,'\n')

'''
#################################################################################################

CaseStudy -3 

#################################################################################################
'''
y2 = 1.0*(df.iloc[:,1]*df.iloc[:,2]/df.iloc[:,3]) - 2 + (df.iloc[:,4]/df.iloc[:,3]) + 0.01*np.random.normal(0,1,10)
df['Target'] = y2
operators = ['/','*']
start_c = time.time()
fc = FeatureSpaceConstruction.feature_space_construction(operators,df,3,'cuda')
df_created = fc.feature_space()
#Create Instace for class 
x = torch.tensor(df_created.iloc[:,1:].values)
y = torch.tensor(df_created.iloc[:,0])
names = df_created.iloc[:,1:].columns
start = time.time()
sr = SISSORegressor.SISSO_Regressor(x,y,names,2,20,'cuda')
sr.SISSO()
print("SISSO Completed: ",time.time()-start_c,'\n')

'''
##########################################################################################################

CaseStudy-4

#########################################################################################################
'''

y2 = 3*(np.exp(df.iloc[:,1])/(df.iloc[:,2]+np.exp(df.iloc[:,1]))) + 0.01*np.random.normal(0,1,10)
df['Target'] = y2
operators = ['/','+','exp']
start_c = time.time()
fc = FeatureSpaceConstruction.feature_space_construction(operators,df,4,'cuda')
df_created = fc.feature_space()
#Create Instace for class 
x = torch.tensor(df_created.iloc[:,1:].values)
y = torch.tensor(df_created.iloc[:,0])
names = df_created.iloc[:,1:].columns
start = time.time()
sr = SISSORegressor.SISSO_Regressor(x,y,names,1,20,'cuda')
sr.SISSO()
print("SISSO Completed: ",time.time()-start_c,'\n')


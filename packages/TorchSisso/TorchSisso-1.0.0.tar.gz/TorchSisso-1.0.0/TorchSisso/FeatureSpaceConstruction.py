#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 13 21:42:41 2023

@author: muthyala.7
"""
import torch 
import pandas as pd 
import numpy as np 
import warnings
import itertools
import time

class feature_space_construction:

  '''
  ##############################################################################################################
  Define global variables like number of operators and the input data frame and the operator set given

  ############################################################################################################## 
  '''
  def __init__(self,operators,df,no_of_operators=3,device='cpu',list1=None):
    print(f'Starting Feature Space Construction in {device}')
    self.no_of_operators = no_of_operators
    self.df = df
    self.operators = operators
    self.device = torch.device(device)
    self.dimensionality = list1
    #Manipulate the dataframe by selecting only the numerical datatypes and popping out the target column
    self.df = self.df.select_dtypes(include=['float64','int64'])
    # Compute the variance of each column
    variance = self.df.var()

    # Get the names of the zero variance columns
    zero_var_cols = variance[variance == 0].index

    # Drop the zero variance columns from the dataframe
    self.df = self.df.drop(zero_var_cols, axis=1)

    self.df.rename(columns = {f'{self.df.columns[0]}':'Target'},inplace=True)
    self.Target_column = self.df.pop('Target')

    # Get the column values and convert it to tensor 
    self.df_feature_values = torch.tensor(self.df.values).to(self.device)
    #Create a dataframe for appending new datavalues 
    self.new_features_values = pd.DataFrame()

    #Get the column headers 
    self.columns = self.df.columns.tolist()
    
    #Creating empty tensor for single operators
    self.feature_values = torch.empty(self.df.shape[0],0).to(self.device)
    self.feature_names = []
    #creating empty tensor for combinations
    self.feature_values1 = torch.empty(self.df.shape[0],0).to(self.device)
    self.feature_names1 = []
  '''
  ###############################################################################################################

  Construct all the features that can be constructed using the single operators like log, exp, sqrt etc..

  ###############################################################################################################
  '''

  def single_variable(self,operators_set):
    #Check for the validity of the operator set given 
    for op in operators_set:

      if op in ['exp','sin','cos','sqrt','cbrt','log','ln','^-1','^2','^3','exp(-1)','abs']:
        continue
      else:
        raise TypeError('Invalid Operator found in the given operator set')
    
    #Looping over operators set to get the new features/predictor variables 

    for j in range(len(operators_set)):

      op = operators_set[j]
      #Looping over all the initial feature set with the specific operator set 

      for i in range(len(self.columns)):
        if op == 'exp':

          #Applying the operator and adding to the new dataframe
          feature = f'{op}({self.columns[i]})'
          value = torch.exp(self.df_feature_values[:,i]).to(self.device)
          self.feature_values = torch.cat((self.feature_values,value.unsqueeze(1)), dim=1).to(self.device)
          self.feature_names.append(feature)
          #self.new_features_values[feature] = value.cpu().numpy()

        elif op == 'ln':

          #Applying the log operator to the feature and feature values\
          #This is the exponential not the base 10
          feature = f'{op}({self.columns[i]})'
          value = torch.log(self.df_feature_values[:,i]).to(self.device)
          self.feature_values = torch.cat((self.feature_values,value.unsqueeze(1)), dim=1).to(self.device)
          self.feature_names.append(feature)
          #self.new_features_values[feature] = value.cpu().numpy()
        
        elif op == 'sin':
          #Applying the sin operator to the featrure and feature values
          feature = f'{op}({self.columns[i]})'
          value = torch.sin(self.df_feature_values[:,i]).to(self.device)
          self.feature_values = torch.cat((self.feature_values,value.unsqueeze(1)), dim=1).to(self.device)
          #self.new_features_values[feature] = value.cpu().numpy()
          self.feature_names.append(feature)
        
        elif op =='log':

          #Applying the log10 operator to the feature and feature values
          feature = f'{op}({self.columns[i]})'
          value = torch.log10(self.df_feature_values[:,i]).to(self.device)
          self.feature_values = torch.cat((self.feature_values,value.unsqueeze(1)), dim=1).to(self.device)
          self.feature_names.append(feature)
          #self.new_features_values[feature] = value.cpu().numpy()
        
        elif op =='cos':

          #Applying the cos operator to the feature and feature values
          feature = f'{op}({self.columns[i]})'
          value = torch.cos(self.df_feature_values[:,i]).to(self.device)
          self.feature_values = torch.cat((self.feature_values,value.unsqueeze(1)), dim=1).to(self.device)
          self.feature_names.append(feature)
#          self.new_features_values[feature] = value.cpu().numpy()
        
        elif op =='cbrt':

          #Applying the cuberoot function to the feature and feature values 
          feature = f'{op}({self.columns[i]})'
          value = torch.pow(self.df_feature_values[:,i],1/3).to(self.device)
          self.feature_values = torch.cat((self.feature_values,value.unsqueeze(1)), dim=1).to(self.device)
          self.feature_names.append(feature)
#          self.new_features_values[feature] = value.cpu().numpy()
        
        elif op =='sqrt':

          #Applying the sqaureroot function to the feature and feature values
          feature = f'{op}({self.columns[i]})'
          value = torch.sqrt(self.df_feature_values[:,i]).to(self.device)
          self.feature_values = torch.cat((self.feature_values,value.unsqueeze(1)), dim=1).to(self.device)
          self.feature_names.append(feature)
#          self.new_features_values[feature] = value.cpu().numpy()

        elif op =='^2':

          #Applying the square function to the feature and feature values
          feature = f'({self.columns[i]}){op}'
          value = torch.pow(self.df_feature_values[:,i],2).to(self.device)
          self.feature_values = torch.cat((self.feature_values,value.unsqueeze(1)), dim=1).to(self.device)
          self.feature_names.append(feature)
          #self.new_features_values[feature] = value.cpu().numpy()
        
        elif op =='^3':

          #Applying the cube function to the feature and feature values
          feature = f'({self.columns[i]}){op}'
          value = torch.pow(self.df_feature_values[:,i],3).to(self.device)
          self.feature_values = torch.cat((self.feature_values,value.unsqueeze(1)), dim=1).to(self.device)
          self.feature_names.append(feature)
#          self.new_features_values[feature] = value.cpu().numpy()
        
        elif op == '^-1':

          #Applying the inverse function to the feature and feature valuies
          feature = f'({self.columns[i]}){op}'
          value = torch.reciprocal(self.df_feature_values[:,i]).to(self.device)
          self.feature_values = torch.cat((self.feature_values,value.unsqueeze(1)), dim=1).to(self.device)
          self.feature_names.append(feature)
#          self.new_features_values[feature] = value.cpu().numpy()

        elif op =='exp(-1)':

          #Appying the inverse exponential to the feature and feature values
          feature = f'{op}({self.columns[i]})'
          value = torch.reciprocal(torch.exp(self.df_feature_values[:,i])).to(self.device)
          self.feature_values = torch.cat((self.feature_values,value.unsqueeze(1)), dim=1).to(self.device)
          self.feature_names.append(feature)
          #self.new_features_values[feature] = value.cpu().numpy()
            
    # create Boolean masks for NaN and Inf values
    nan_columns = torch.any(torch.isnan(self.feature_values), dim=0)
    inf_columns = torch.any(torch.isinf(self.feature_values), dim=0)
    nan_or_inf_columns = nan_columns | inf_columns

    # Remove columns from tensor
    self.feature_values = self.feature_values[:, ~nan_or_inf_columns]

    # Remove corresponding elements from list
    self.feature_names = [elem for i, elem in enumerate(self.feature_names) if not nan_or_inf_columns[i]]

    return self.feature_values, self.feature_names #self.new_features_values
  


  '''
  ################################################################################################

  Defining method to perform the combinations of the variables with the initial feature set
  ################################################################################################
  '''
  def combinations(self,operators_set):

    #Checking for the operator set
      for op in operators_set:
        if op in ['+','-','*','/','abs']:
          continue
        else:
          raise TypeError("Valid set of operators +,-,*,/, abs please check the operators set")
          break
      
      #Defining the set of combinations to be performed
      import itertools
      from itertools import combinations

      #getting list of cobinations without replacement using itertools 
      combinations = list(combinations(self.columns,2))
      #Creating a list for the adding the features combinations created
      #Converting columns to numpy array to support on GPU if not the indexing doesn't support to GPU
      column_array = np.array(self.columns)
      #Applying the operators to the combinations created
      for comb in combinations:

        #Get the index position of the combination created
        index1 = np.where(column_array == comb[0])[0][0]
        index2 = np.where(column_array == comb[1])[0][0]
        index_1 = torch.tensor([index1,index2]).to(self.device)
        #Extract the values from the original tensor 
        values = torch.tensor(self.df_feature_values[:,index_1]).to(self.device)
        for op in operators_set:
          
          #Apply the conditions of operators
          if op =='+':
            feature_value = torch.add(values[:,0],values[:,1]).to(self.device)
            #print(feature_value.device,self.feature_values1.device)
            self.feature_values1 = torch.cat((self.feature_values1,feature_value.unsqueeze(1)), dim=1).to(self.device)
            col_name = f'({comb[0]}{op}{comb[1]})'
            self.feature_names1.append(col_name)
          elif op =='-':
            feature_value = torch.sub(values[:,0],values[:,1]).to(self.device)
            self.feature_values1 = torch.cat((self.feature_values1,feature_value.unsqueeze(1)), dim=1).to(self.device)
            col_name = f'({comb[0]}{op}{comb[1]})'
            self.feature_names1.append(col_name)
            #feature_value1 = torch.sub(values[:,1],values[:,0]).to(self.device)
            #self.feature_values1 = torch.cat((self.feature_values1,feature_value1.unsqueeze(1)), dim=1).to(self.device)
            #col_name = f'({comb[1]}{op}{comb[0]})'
            #self.feature_names1.append(col_name)
          elif op == '*':
            feature_value = torch.mul(values[:,0],values[:,1]).to(self.device)
            self.feature_values1 = torch.cat((self.feature_values1,feature_value.unsqueeze(1)), dim=1).to(self.device)
            col_name = f'({comb[0]}{op}{comb[1]})'
            self.feature_names1.append(col_name)
          elif op =='/':
            feature_value = torch.div(values[:,0],values[:,1]).to(self.device)
            self.feature_values1 = torch.cat((self.feature_values1,feature_value.unsqueeze(1)), dim=1).to(self.device)
            col_name = f'({comb[0]}{op}{comb[1]})'
            self.feature_names1.append(col_name)
            #feature_value1 = torch.div(values[:,1],values[:,0]).to(self.device)
            #self.feature_values1 = torch.cat((self.feature_values1,feature_value1.unsqueeze(1)), dim=1).to(self.device)
            #col_name = f'({comb[1]}{op}{comb[0]})'
            #self.feature_names1.append(col_name)
          elif op == 'abs':
            feature_value = torch.abs(torch.sub(values[:,0],values[:,1])).to(self.device)
            self.feature_values1 = torch.cat((self.feature_values1,feature_value.unsqueeze(1)), dim=1).to(self.device)
            col_name = f'(|{comb[0]}-{comb[1]}|)'
            self.feature_names1.append(col_name)
            
      
      #Removing Nan and inf columns from tenosr and corresponding variable name form the list
      nan_columns = torch.any(torch.isnan(self.feature_values1), dim=0)
      inf_columns = torch.any(torch.isinf(self.feature_values1), dim=0)
      nan_or_inf_columns = nan_columns | inf_columns

      # Remove columns from tensor
      self.feature_values1 = self.feature_values1[:, ~nan_or_inf_columns]

      # Remove corresponding elements from list
      self.feature_names1 = [elem for i, elem in enumerate(self.feature_names1) if not nan_or_inf_columns[i]]

      #Returning the dataframe created
      return self.feature_values1,self.feature_names1 #created_space
  

  '''
  ##########################################################################################################

  Creating the space based on the given set of conditions

  ##########################################################################################################

  '''

  def feature_space(self):
    #based on the dimension we will be performing the feature space creation
    start_time = time.time()
    basic_operators = [op for op in self.operators if op in ['+', '-', '*', '/']]
    other_operators = [op for op in self.operators if op not in ['+', '-', '*', '/']]
    values, names = self.combinations(basic_operators)
    values1, names1 = self.single_variable(other_operators)
    #Merging two dataframes
    space_created = torch.cat((self.df_feature_values,values,values1), dim=1).to(self.device)
    self.columns = self.columns + names + names1 
    del values, values1, names, names1
    print('Time for phi 1 creation is: ',time.time() - start_time)
    print('First Feature Space building is completed with features count: ',int(space_created.shape[1]))
    #Update the columns according to the new phi created for the next phase features
    self.df_feature_values = (space_created).to(self.device)
    #Creating the phi2 based on the space created 
    start_time = time.time()
    values, names = self.combinations(basic_operators)
    values1, names1 = self.single_variable(other_operators)
    space_created_2 = torch.cat((space_created,values,values1), dim=1).to(self.device)
    self.columns = self.columns + names + names1 
    #######################
    #code to remove duplicate columns from dataframe
    #########################
    #Converting tensor to numpy and then dataframe to remove duplicates
    #space1 = space_created_2.cpu().numpy()
    space = pd.DataFrame(space_created_2.cpu(),columns = self.columns)
    print(space.shape)
    space = space.round(7)
    #space = space.dropna(axis=1, how='any')
    # Transpose the dataframe
    space = space.T.drop_duplicates().T
    print(space.shape)

    print('Time taken to create and remove redundant features in phi2 is ', time.time() - start_time)
    del space_created
    del values, values1, names, names1
    self.columns = space.columns.tolist()
    self.df_feature_values = torch.tensor(space.values).to(self.device)
    print('Second Feature Space building is completed',space.shape)

    if self.no_of_operators >3: 
      for i in range(4,self.no_of_operators+1):
        if i == 4:
          values, names = self.combinations(basic_operators)
          values1,names1 = self.single_variable(other_operators)
          space_created_3 = torch.cat((self.df_feature_values,values,values1),dim=1).to(self.device)
          #space_created_3 = torch.cat((values,self.df_feature_values),dim=1).to(self.device)
          del space_created_2
          self.columns = self.columns + names + names1
          #self.columns = names + self.columns
          space1 = space_created_3.cpu().numpy()
          space = pd.DataFrame(space1,columns = self.columns)
          space = space.dropna(axis=1, how='any')
          space = space.round(7)
          # Transpose the dataframe
          space = space.T.drop_duplicates().T
          del values, names,
          self.columns = space.columns.tolist()
          self.df_feature_values = torch.tensor(space.values).to(self.device)
          print('Third Feature Space building is completed',space.shape)
          if self.no_of_operators+1 == 5:
            space.insert(0,'Target',self.Target_column)
            space = space.dropna(axis=1, how='any')
            #returniung the dataframe
            return space
          else:
            continue
        if i == 5:
          values, names = self.combinations(basic_operators)
          values1,names1 = self.single_variable(other_operators)
          space_created_4 = torch.cat((self.df_feature_values,values,values1),dim=1).to(self.device)
          del space_created_3
          self.columns = self.columns + names + names1
          space1 = space_created_4.cpu().numpy()
          space = pd.DataFrame(space1,columns = self.columns)
          space = space.dropna(axis=1, how='any')
          space = space.round(7)
          # Transpose the dataframe
          space = space.T.drop_duplicates().T
          del values, values1, names, names1
          self.df_feature_values = torch.tensor(space.values).to(self.device)
          self.columns = space.columns.tolist()
          self.df_feature_values = torch.tensor(space.values).to(self.device)
          print('Fourth Feature Space building is completed',space.shape)
          if self.no_of_operators+1 == 6:
            space.insert(0,'Target',self.Target_column)
            space = space.dropna(axis=1, how='any')
            #returniung the dataframe
            return space
          else:
            continue
        if i == 6:
          values, names = self.combinations(basic_operators)
          values1,names1 = self.single_variable(other_operators)
          space_created_5 = torch.cat((self.df_feature_values,values,values1),dim=1).to(self.device)
          del space_created_4
          self.columns = self.columns + names + names1
          del values, values1, names, names1
          space1 = space_created_5.cpu().numpy()
          space = pd.DataFrame(space1,columns = self.columns)
          space = space.dropna(axis=1, how='any')
          space = space.round(7)
          # Transpose the dataframe
          space = space.T.drop_duplicates().T
          self.df_feature_values = torch.tensor(space.values).to(self.device)
          self.columns = space.columns.tolist()
          print('Fifth Feature Space building is completed',space.shape)
          if self.no_of_operators+1 == 7:
            space.insert(0,'Target',self.Target_column)
            space = space.dropna(axis=1, how='any')
            #returniung the dataframe
            return space
          else:
            continue
        if i == 7:
          values, names = self.combinations(basic_operators)
          values1,names1 = self.single_variable(other_operators)
          space_created_6 = torch.cat((self.df_feature_values,values,values1),dim=1).to(self.device)
          del space_created_5
          self.columns = self.columns + names + names1
          del values, values1, names, names1
          space1 = space_created_6.cpu().numpy()
          space = pd.DataFrame(space1,columns = self.columns)
          space = space.dropna(axis=1, how='any')
          space = space.round(7)
          # Transpose the dataframe
          space = space.T.drop_duplicates().T
          self.df_feature_values = torch.tensor(space.values).to(self.device)
          self.columns = space.columns.tolist()
          print('Sixth Feature Space building is completed',space.shape)
          if self.no_of_operators+1 == 8:
            space.insert(0,'Target',self.Target_column)
            space = space.dropna(axis=1, how='any')
            #returniung the dataframe
            return space
          else:
            continue
          

    else:
      space.insert(0,'Target',self.Target_column)
      space = space.dropna(axis=1, how='any')
      #returniung the dataframe
      return space

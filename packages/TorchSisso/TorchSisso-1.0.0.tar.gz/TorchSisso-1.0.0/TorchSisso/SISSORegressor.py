#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 13 21:48:04 2023

@author: muthyala.7
"""

import torch
import warnings
warnings.filterwarnings('ignore')
import itertools
import time 
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

class SISSO_Regressor:
    
    def __init__(self,x,y,names,dimension=1,sis_features=20,device='cpu'):
        print(f'Starting SISSO in {device}')
        self.device = torch.device(device)
        self.x = x.to(self.device)
        self.y =y.to(self.device)
        self.dimension= dimension
        self.sis_features = sis_features
        self.feature_names = names
        self.x_mean = self.x.mean(dim=0).to(self.device)
        self.x_std = self.x.std(dim=0).to(self.device)
        self.y_mean = self.y.mean().to(self.device)
        self.y_centered = (self.y - self.y_mean).to(self.device)
        self.x_standardized = ((self.x - self.x_mean)/self.x_std).to(self.device)
        self.scores = []
        self.indices = []
        self.residual = torch.empty(self.y_centered.shape).to(self.device)
        self.x_std_clone = torch.clone(self.x_standardized).to(self.device)
    
    def higherdimension(self):
        
        min_error = torch.dot(self.y_centered,self.y_centered).to(self.device)
        for indices in self.indices:
            self.x_standardized[:,indices] = 0
        scores = torch.abs(torch.mm(self.residual,self.x_standardized)).to(self.device)
        scores[torch.isnan(scores)] = 0
        for indices in self.indices:
            self.x_standardized[:,indices] = self.x_std_clone[:,indices]
        sorted_scores,sorted_indices = torch.topk(scores,k=self.sis_features)
        self.scores.append(sorted_scores)
        self.indices.append(sorted_indices)
        combinations_generated = itertools.combinations(torch.cat(self.indices).flatten(),len(self.indices))
        #print(len(self.indices),len(list(combinations_generated)))
        start_c = time.time()
        for combinations in combinations_generated:
            x_sub = self.x_standardized[:,combinations].to(self.device)
            coefficients = x_sub.pinverse()@self.y_centered.reshape(-1,1).to(self.device)
            sum_of_residuals = torch.sum((x_sub @ coefficients - self.y_centered.reshape(-1,1))**2).to(self.device)
            index = torch.tensor(combinations)
            if sum_of_residuals <min_error:
                min_error = sum_of_residuals
                coefs_min, indices_min = coefficients,torch.tensor(combinations)
            else:
                continue
        print('Time taken to go through all combinations is:', time.time()-start_c)
        rmse = torch.sqrt(min_error/int(self.y_centered.shape[0])).to(self.device)
        non_std_coeff = ((coefs_min.T/self.x_std[indices_min])).to(self.device)
        non_std_intercept = self.y.mean() - torch.dot(self.x_mean[indices_min]/self.x_std[indices_min],coefs_min.flatten()).to(self.device)
        self.residual = self.y_centered - torch.mm(coefs_min.T,self.x_standardized[:,indices_min].T).to(self.device)
        terms = []
        for i in range(len(non_std_coeff.squeeze())):
          term = str(float(non_std_coeff.squeeze()[i])) + "*" + str(self.feature_names[int(indices_min[i])])
          terms.append(term)
        return rmse,terms,non_std_intercept,non_std_coeff

    
    
    def SISSO(self):
        
        if self.x.shape[1] > self.sis_features*self.dimension:
            print('Started SISSO')
        else:
            raise RuntimeError('Number of features in SIS screening are greater than total number of features.')
        
        for i in range(1,self.dimension+1):
            
            if i == 1:
                scores = torch.abs(torch.mm(self.y_centered.unsqueeze(1).T,self.x_standardized)).to(self.device)
                # set NaN values to zero, so that we don't jeprodize the indexing 
                scores[torch.isnan(scores)] = 0
                sorted_scores, sorted_indices = torch.topk(scores,k=self.sis_features)
                self.scores.append(sorted_scores)
                self.indices.append(sorted_indices)
                #calculate all standardized coeffcients 
                coefs = scores/(self.x_std*self.y.std())
                selected_index = int(self.indices[0][0][0])
                #coeff, intercept = linear_regression(self.x[:,selected_index].unsqueeze(1), self.y.unsqueeze(1)).to(device)
                model = LinearRegression().fit(self.x[:,selected_index].cpu().numpy().reshape(-1,1), self.y.cpu().numpy())
                coeff = model.coef_
                intercept = model.intercept_
                print("Coefficient:", float(coeff))
                print("Intercept:", float(intercept))
                print('selected variable: ', self.feature_names[selected_index])
                #std_coeff = torch.tensor(self.scores[0][0][0]/int(self.y.shape[0]))
                std_coeff = (torch.tensor(coeff).to(self.device)*(self.x_std[selected_index])/self.y.std()).to(self.device)
                self.residual = self.y_centered - (std_coeff*self.x_standardized[:,selected_index]).to(self.device)
                #rmse = torch.sqrt(torch.mean((self.y - torch.tensor(coeff).to(self.device)*self.x[:,selected_index])**2)).to(self.device)
                self.residual = self.residual.unsqueeze(1).T
                y_pred = model.predict(self.x[:,selected_index].cpu().numpy().reshape(-1,1))
                rmse = torch.sqrt(torch.tensor(mean_squared_error(self.y.cpu().numpy(),y_pred))).to(self.device)
                if intercept > 0: 
                    equation = str(float(coeff)) + '*' + str(self.feature_names[selected_index]) + '+' + str(float(intercept))
                    print('Equation: ',equation)
                    print('RMSE:', float(rmse))
                else:
                    equation = str(float(coeff)) + '*' + str(self.feature_names[selected_index]) + '-' + str(float(intercept))[1:]
                    print('Equation: ',equation)
                    print('RMSE',float(rmse))
            else:
                start_time = time.time()
                rmse,terms,intercept,coefs = self.higherdimension()
                equation = ''
                for k in range(len(terms)):
                  print(f'{k+1} term in the equation is {terms[k]}')
                  if coefs.flatten()[k] > 0:
                      equation = equation + (str(terms[k])) + '+ '
                  else:
                    equation = equation + (str(terms[k])) 
                print(f'{i} term equation:',equation[:len(equation)-2])
                print('Intercept:', float(intercept))
                print('RMSE:',float(rmse))
                print(f'Time taken for {i} dimension is: ', time.time()-start_time)
                
                
                
                
                
                                
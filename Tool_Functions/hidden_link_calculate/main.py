#coding=utf-8
import json

import pandas as pd
import multiprocessing
from numpy import *
import csv
import math
#import cvxpy as cvx 
from scipy import sparse as sp
from scipy.linalg import lstsq
from scipy.linalg import solve
from scipy.optimize import nnls
import scipy

def main(userInfo: object, diffusionInfo: object):

    #reading input data
    #data contains:feature vector, state
    #data=pd.read_csv(from_file,encoding='utf-8')
    data=pd.read_json(userInfo,orient='records')
    data.sort_values(by='0')
    ## get the features of nodes ##
    feature_sample=data[['node1_x','node1_y']]
    feature_sample.index=data.index
    ## rescale features to a compact cube ##
    feature_max=[]
    for item in feature_sample.columns:
        feature_max.append(max(absolute(array(feature_sample[item]))))
        feature_sample[item]/=max(absolute(array(feature_sample[item])))
    ## define infect event and get 0-1 infection status sequence ##

    # draw subsample nodes and spreading info on these nodes
    #data_sample=random.choice(data.index,size=3)
    data_sample = range(0,300)
    features=feature_sample.iloc[list(data_sample)]
    features.index=arange(len(data_sample))
    #spreading_sample=pd.read_csv('obs_500x300.csv',encoding='utf-8')
    spreading_sample = pd.read_json(diffusionInfo,orient='records')
    spreading_sample = spreading_sample.sort_values(by='user_id')
    spreading_sample.drop('user_id',axis=1,inplace=True)
    spreading=spreading_sample.values

    # generate observation input
    obs=spreading[::10]
    print('obs.shape>>>>>>>>>>>')
    print(obs.shape)

    features_matirx = features.values
    # print('features_onerow*************************')
    # print(features_matirx[0])
    bandwidth = (diag(ones(features.shape[1])*float(features.shape[0])**(-1./float(features.shape[1]+1))))/10
    print('bandwidth*******************************')
    print(bandwidth)

    #single_point_solver(features_matirx[0])`   
    rxt_params = []
    rxt_list = []
    for ti in obs:
        for row in features_matirx:
            l = []
            l.append(row)
            # print('row>>>>>>>>')
            # print(row)
            l.append(ti)
            # print('ti>>>>>>>>>>>>>')
            l.append(features_matirx)
            l.append(bandwidth)
            rxt_params.append(l)
    return pd.Series(rxt_params).to_json(orient='records')



#coding=utf-8
import pandas as pd
import multiprocessing
from numpy import *
import math
import json

def gaussiankernel(x,z,args,N):
    if N==1:
        sigma = args
        y = (1./sqrt(2.*pi)/sigma)*exp(-(x-z)**2/(2.*sigma**2))
    else:
        sigma = args
        cov=[]
        for j in range(N):
            cov+=[1./sigma[j,j]**2]
        N=float(N)

        y = 1./(2.*pi)**(N/2.)*abs(linalg.det(sigma))**(-1.)*exp((-1./2.)*dot((x-z)**2,array(cov)))
    return y

def construct_rxt(x):
    #construct r(x,t) in paper
    kernel=[]
    x[0]=asarray(x[0])
    x[2] = asarray(x[2])
    n=x[2].shape[1]
    bandwidth=asarray(x[3])
    for row in x[2]:
        kernel.append(gaussiankernel(x[0],row,bandwidth,n))
    rxt_upper=dot(kernel,asarray(x[1]))
    rxt_lower=0
    for i in kernel:
        rxt_lower = rxt_lower+i
    rxt = rxt_upper/rxt_lower
    if rxt > 0.999:
        rxt = 0.999
    elif rxt < 0.001:
        rxt = 0.001
    return rxt

def parallel_r_main(jsoninput,dt=0.1):
    #TO PANG:
    #you should make gaussiankernel a tool as well,
    #please do it yourself so you know what's the experience for other users to change their code.
    input=pd.read_json(jsoninput,orient='records')
    rxt_params=input.values.tolist()

    cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cores)
    cnt = 0
    #construct r(x,t) in parallel
    # rxt_matrix is like:
    # r(x1,t1) .... r(xn,t1)
    # ...
    # r(x1,tm) .... r(xn,tm)
    rxt_list = pool.map(construct_rxt, rxt_params)
    rxt_matrix=asarray(rxt_list).reshape(51,300)
    #construct all overline_r(x,t)
    overline_r_all=-log(1-rxt_matrix)
    # #get the D matrix
    D = rxt_matrix
    # #compute differensiation
    # #diff_x_all is like:
    # #dx1t1 dx2t1 .... dxnt1
    # #dx1t2 dx2t2 .... dx2tm
    # #...
    # #dx1tm dx2tm .... dxntm

    overline_r_all2 = copy(overline_r_all)
    overline_r_all2_add = row_stack((overline_r_all2, overline_r_all2[-1,:]))
    overline_r_all2_splite = overline_r_all2_add[1:,]

    diff_x_all = (overline_r_all2_splite-overline_r_all)/dt

    #reconstruct the compress sensing signal to get edge function
    xit_all = []
    diff_group_by_x = diff_x_all.T
    for xit in diff_group_by_x:
        xit_matrix = []
        xit_matrix.append(xit)
        xit_matrix.append(D)
        xit_all.append(xit_matrix)
    return pd.Series(xit_all).to_json(orient='records')

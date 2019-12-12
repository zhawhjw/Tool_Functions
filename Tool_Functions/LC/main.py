# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 20:59:17 2019

@author: user
"""

import pandas as pd
import numpy as np
import time
from collections import Counter

import ot
import ot.plot
import random


def main(exampleTable: object, industryList: object):
    df1 = pd.read_csv(exampleTable)
    df4 = pd.read_csv(industryList)
    np.set_printoptions(suppress=True)
    lng = df1['lng']
    lng = np.float32(lng)
    lat = df1['lat']
    lat = np.float32(lat)
    ind_list = df4['industry list'].tolist()
    ind_code3 = df1[df1['ind_code3'].isin(ind_list)]['ind_code3']
    result = Counter(ind_code3)  # 统计企业数量
    np.set_printoptions(suppress=True)
    p1 = dict((key, value) for key, value in result.items() if value > 0)  # 筛选企业数超过10的行业
    ind_code = list(p1.keys())
    N = len(ind_code)
    ranlist = df1.index.tolist()
    csq_result = np.empty(shape=[0, 6])
    f = 0
    for x in range(N):
        for y in range(x + 1, N):
            i_code = ind_code[x]  # 取值有问题
            j_code = ind_code[y]
            ni = p1[i_code]
            nj = p1[j_code]
            df2 = df1[df1['ind_code3'] == i_code]  # 取出某一行业内所有企业
            index_i = df2.index.tolist()  # 将取出的某一行业的索引提取
            df3 = df1[df1['ind_code3'] == j_code]  # 取出某一行业内所有企业
            index_j = df3.index.tolist()  # 将取出的某一行业的索引提取
            di = np.empty(shape=[ni, 2])
            dj = np.empty(shape=[nj, 2])

            for i in range(ni):
                m = index_i[i]
                # m=int(m[3:])
                di[i, :] = [lng[m], lat[m]]

            for j in range(nj):
                m = index_j[j]
                # m=int(m[3:])
                dj[j, :] = [lng[m], lat[m]]

            a, b = np.ones((ni,)) / ni, np.ones((nj,)) / nj

            M = ot.dist(di, dj, metric='euclidean')
            g0 = ot.sinkhorn2(a, b, M, 1)

            fij = np.empty(shape=[1, 1000])  # 放置空矩阵存放模拟结果
            fji = np.empty(shape=[1, 1000])
            for c in range(1000):
                e = random.sample(ranlist, nj)  # 取出nj个随机数
                de = np.empty(shape=[nj, 2])
                for j in range(nj):
                    m = e[j]
                    # m=int(m[3:])
                    de[j, :] = [lng[m], lat[m]]
                M = ot.dist(di, de, metric='euclidean')
                ge = ot.sinkhorn2(a, b, M, 1)
                fij[0, c] = ge[0]

                # result[x,y]=sum(sum(count > g0 for count in fij))/1000

                e1 = random.sample(ranlist, ni)  # 取出ni个随机数
                de1 = np.empty(shape=[ni, 2])
                for i in range(ni):
                    m = e1[i]
                    # m=int(m[3:])
                    de1[i, :] = [lng[m], lat[m]]
                M1 = ot.dist(dj, de1, metric='euclidean')
                ge1 = ot.sinkhorn2(b, a, M1, 1)
                fji[0, c] = ge1[0]
            resij = sum(sum(count > g0[0] for count in fij)) / 1000
            resji = sum(sum(count > g0[0] for count in fji)) / 1000
            csq_result = np.append(csq_result, [[i_code, j_code, resij, g0[0], len(index_i), len(index_j)]], axis=0)
            csq_result = np.append(csq_result, [[j_code, i_code, resji, g0[0], len(index_j), len(index_i)]], axis=0)
            f = f + 1

    csq_result = pd.DataFrame(csq_result)

    csq_result.columns = ['ind_i', 'ind_j', 'co-agg index', 'W Distance', 'ni', 'nj']
    return csq_result.copy()


print(main("./example.csv", "./industry+list.csv"))

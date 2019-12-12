#coding=utf-8
from sys import argv
from os.path import exists
import pandas as pd
import multiprocessing
from numpy import *
import csv
import math
import datetime
#import cvxpy as cvx 
from scipy import sparse as sp
from scipy.linalg import lstsq
from scipy.linalg import solve
from scipy.optimize import nnls
import scipy
import json

def OrthogonalMP(A, b, tol=1E-6, nnz=None, positive=False):
  '''approximately solves min_x |x|_0 s.t. Ax=b using Orthogonal Matching Pursuit
  Args:
    A: design matrix of size (d, n)
    b: measurement vector of length d
    tol: solver tolerance
    nnz = maximum number of nonzero coefficients (if None set to n)
    positive: only allow positive nonzero coefficients
  Returns:
     vector of length n
  '''

  AT = A.T
  d, n = A.shape
  if nnz is None:
    nnz = n
  x = zeros(n)
  resid = copy(b)
  normb = linalg.norm(b)
  indices = []

  for i in range(nnz):
    if linalg.norm(resid)/normb < tol:
      break
    projections = AT.dot(resid)
    if positive:
      index = argmax(projections)
    else:
      index = argmax(abs(projections))
    if index in indices:
      break
    indices.append(index)
    if len(indices) == 1:
      A_i = A[:,index]
      x_i = projections[index] / A_i.T.dot(A_i)
    else:
      A_i = vstack([A_i, A[:,index]])
      x_i = solve(A_i.dot(A_i.T), A_i.dot(b), assume_a='sym')
      if positive:
        while min(x_i) < 0.0:
          am = argmin(x_i)
          indices = indices[:am] + indices[am+1:]
          A_i = vstack([A_i[:am], A_i[am+1:]])
          x_i = solve(A_i.dot(A_i.T), A_i.dot(b), assume_a='sym')
    resid = b - A_i.T.dot(x_i)

  for i, index in enumerate(indices):
    try:
      x[index] += x_i[i]
    except IndexError:
      x[index] += x_i
  return x


# NOTE: Standard Algorithm, e.g. Tropp, ``Greed is Good: Algorithmic Results for Sparse Approximation," IEEE Trans. Info. Theory, 2004.
def MatchingPursuit(x, tol=1E-4, nnz=None, positive=True, orthogonal=False):
  '''approximately solves min_x |x|_0 s.t. Ax=b using Matching Pursuit
  Args:
    A: design matrix of size (d, n)
    b: measurement vector of length d
    tol: solver tolerance
    nnz = maximum number of nonzero coefficients (if None set to n)
    positive: only allow positive nonzero coefficients
    orthogonal: use Orthogonal Matching Pursuit (OMP)
  Returns:
     vector of length n
  '''
  A = asarray(x[1])
  b = asarray(x[0])
  if orthogonal:
    return OrthogonalMP(A, b, tol=tol, nnz=nnz, positive=positive)

  AT = A.T
  d, n = A.shape
  if nnz is None:
    nnz = n
  x = zeros(n)
  resid = copy(b)
  normb = linalg.norm(b)
  selected = zeros(n, dtype=bool)

  for i in range(nnz):
    if linalg.norm(resid)/normb < tol:
      break
    projections = AT.dot(resid)
    projections[selected] = 0.0
    if positive:
      index = argmax(projections)
    else:
      index = argmax(abs(projections))
    atom = AT[index]
    coef = projections[index]/linalg.norm(A[:,index])
    if positive and coef <= 0.0:
      break
    resid -= coef*atom
    x[index] = coef
    selected[index] = True
  return x

def minimizer_L1(x):
    D=x[1]
    y=x[0].T
    # print('D>>>>>>>>>>>>>>>>>>>>>>')
    # print(D)
    # print('y>>>>>>>>>>>>>>>>>>>>>>')
    # print(y)
    if(D.shape[0] < D.shape[1]):
        edge_row = MatchingPursuit(y,D,orthogonal=True)
    else:
        edge_row,residual = nnls(D,y,maxiter=None)
    return edge_row

def parallel_minimizer(xit_all):
    cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cores)
    xit_all=pd.read_json(xit_all,orient='records').values.tolist()
    edge_list = pool.map(MatchingPursuit, xit_all)
    return pd.Series(edge_list).to_json(orient='records')
# -*- coding: utf-8 -*-
"""copy_our_moon.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XqXfNOrfHKQlRenGpXLsGeK2mQJ_yd4_

# explanation and goal of project

# import libraries
"""

import math
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.spatial.distance import cdist
from sklearn.datasets import make_moons
from sklearn import datasets
import random
from IPython.display import set_matplotlib_formats
from sklearn.neighbors import kneighbors_graph
set_matplotlib_formats('svg', 'pdf')

"""initialize hyperparameter"""

n = 1000
n_labeled = 10
alpha = 0.99
sigma = 0.1
gamma=0.001
k = 7

"""#create database 
here i create database of moons and then show the shape and one sample from them 
"""

X, Y = make_moons(n, shuffle=True, noise=0.1, random_state=None)
X.shape , Y.shape , X[0] , Y[0]

print(X)
print(Y)

"""# make database unbalance
in this part, I delete the number of the sample that belong to class 1 and their value in x dimension bigger than one that I assume as the border that deletes half of my class 1 moon 
"""

for l in reversed(range(Y.shape[0])):
  if Y[l]==1 and X[l,0]>1:
    n=n-1
    X=np.delete(X,l,0)
    Y=np.delete(Y,l)

"""# add init label of classes or not labeled to samples
we get `n_labeled` first sample of Y by `Y[:n_labeled,None]` if we don't use None then the result shape become (10,) but by use None it become (10,1) and make it column of number 0 or 1 instead of row of 0 or 1

the result of this code for 10 sample  `Y[:n_labeled,None]==np.arange(2)` is :


```
[[ True False]                     
 [ True False]
 [False  True]
 [False  True]
 [ True False]
 [ True False]
 [False  True]
 [ True False]
 [False  True]
 [ True False]]
 ```
while `Y[:n_labeled,None]` is:


```
[[0]
 [0]
 [1]
 [1]
 [0]
 [0]
 [1]
 [0]
 [1]
 [0]]
 ```

so if Y[i]==0 first parameter become True and second one become oposite of it and False and if Y[i]==1 first parameter become False and second one become oposite of it and True.

by add `.astype(float))` change this True and false to 0 and 1


```
(Y[:n_labeled,None] == np.arange(2)).astype(float):

[[1. 0.]
 [1. 0.]
 [0. 1.]
 [0. 1.]
 [1. 0.]
 [1. 0.]
 [0. 1.]
 [1. 0.]
 [0. 1.]
 [1. 0.]]
```
and then labeled other sample by code below:


```
np.zeros((n-n_labeled,2)):

array([[0., 0.],
       [0., 0.],
       [0., 0.],
       ...,
       [0., 0.],
       [0., 0.],
       [0., 0.]])
```

so if the sample has not label it become [0,0] and if it has label and label is belonge to class 1 it become [1,0] or if belonge to class 0 it become [0,1]
"""

Y_input = np.concatenate(((Y[:n_labeled,None] == np.arange(2)).astype(float), np.zeros((n-n_labeled,2))))

Y_input.shape

"""# colorize and plot modify database
now at first for sample type we define color :

*   green for supervised sample class 1
*   yellow for supervised sample class 0
*   red for sample that algorithm labeling as class 0
*   blue for sample that algorithm labeling as class 1

and then plot it


"""

color=list()
for i in range(Y.shape[0]):
  if Y_input[i,0]==0 and Y_input[i,1]==0:
    if Y[i]==0:
      color.append('red')
    elif Y[i]==1:
      color.append('blue')
  if Y_input[i,0]==1:
    color.append('green')
  if Y_input[i,1]==1:
    color.append('yellow')

plt.scatter(X[0:,0], X[0:,1], color=color)
plt.title("ideal_classification")
plt.savefig("ideal_classification.pdf", format='pdf')
plt.show()

"""# calculate  euclidean distance between nodes and W base on below formule:
![image_2022-09-21_17-39-21.png](data:image/png;base64,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)

"""

dm = cdist(X, X, 'euclidean')
rbf = lambda x, sigma: math.exp((-x**2)/(2*(math.pow(sigma,2))))
vfunc = np.vectorize(rbf)
W = vfunc(dm, sigma)
np.fill_diagonal(W, 0)

A = kneighbors_graph(X, k, mode='connectivity', include_self=True)
A.toarray()
A=scipy.sparse.csr_matrix.toarray(A)
W=np.multiply(W,A)

def calculate_D(W):
  d=np.sum(W,axis=1)
  """A=np.zeros([len(d),len(d)])
  for i in range(len(d)):
    A[i,i]=d[i]"""
  A=np.diag(np.sum(W,axis=1))
  return d,A

d,D=calculate_D(W)

D.shape , Y_input.shape , d.shape

inverse_w = np.linalg.inv(D)
inverse_w.shape

"""# calculate P and L and G:

![image.png](data:image/png;base64,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)

![image.png](data:image/png;base64,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)
"""

def calculate_P_L(D,W):
  d = np.sum(W, axis=1)
  pi=(d/np.sum(d))
  pi = pi.reshape((1,pi.shape[0]))
  print("pi shape:",pi.shape)
  P=np.dot(np.linalg.inv(D),W)
  print(D)
  print(np.linalg.inv(D))
  G=np.matmul(np.ones((pi.shape[1] , 1)),pi)
  return P,D-W,G

P,L,G=calculate_P_L(D,W)
P.shape , G

"""#initilize F by formule of below and plot it :
 ![image.png](data:image/png;base64,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)
"""

# F = np.dot(S, Y_input)*alpha + (1-alpha)*Y_input
F=np.dot(np.linalg.inv(D),Y_input)

Y_result = np.zeros_like(F)
Y_result[np.arange(len(F)), F.argmax(1)] = 1

Y_v = [1 if x == 0 else 0 for x in Y_result[0:,0]]

F.shape , G.shape

color = ['red' if l == 0 else 'blue' for l in Y_v]
plt.scatter(X[0:,0], X[0:,1], color=color)
#plt.savefig("iter_n.pdf", format='pdf')
plt.show()

"""# after one time iteration run code"""

F = np.dot(P, F) +(-gamma)*np.dot(G, F) +gamma*np.dot(np.linalg.inv(D),Y_input)
Y_result = np.zeros_like(F)
Y_result[np.arange(len(F)), F.argmax(1)] = 1

Y_v = [1 if x == 0 else 0 for x in Y_result[0:,0]]

color = ['red' if l == 0 else 'blue' for l in Y_v]
plt.scatter(X[0:,0], X[0:,1], color=color)
#plt.savefig("iter_n.pdf", format='pdf')
plt.show()

"""# after n_iter time itration run algorithm"""

n_iter = 2000
for t in range(n_iter):
  # F = np.dot(P, F) - np.dot(G, F)*gamma + gamma*np.dot(diagonal_power(D,-1),Y_input)
  F = np.dot(P, F) +(-gamma)*np.dot(G, F) +gamma*np.dot(np.linalg.inv(D),Y_input)
  # F = np.dot(S, F)*alpha + (1-alpha)*Y_input

Y_result = np.zeros_like(F)
Y_result[np.arange(len(F)), F.argmax(1)] = 1

Y_v = [1 if x == 0 else 0 for x in Y_result[0:,0]]

color = ['red' if l == 0 else 'blue' for l in Y_v]
plt.scatter(X[0:,0], X[0:,1], color=color)
#plt.savefig("iter_n.pdf", format='pdf')
plt.show()

"""this method have predict other sample with high accurcy Despite that all supervised labeled sample are from one class(red color) and not from another class (blue color)"""
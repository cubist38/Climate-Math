# -*- coding: utf-8 -*-
"""Dự đoán.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1996CRQ4DBks8G_C69-rj69UFTfDoaYNd

**Liên kết với drive**
"""

from google.colab import drive
drive.mount('/content/drive')

"""**Gọi các thư viện cần thiết**"""

import pandas as pd
import numpy as np
import sklearn
import matplotlib.pyplot as plt
from sklearn import linear_model
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

"""**Đọc dữ liệu bằng thư viện pandas**"""

PATH = '/content/drive/MyDrive/TUDTK/SEATTLE TACOMA AIRPORT, WA US.csv'
df = pd.read_csv(PATH) # đọc file csv
df = df.drop(['STATION', 'NAME', 'DATE'], axis=1) # loại bỏ 3 cột station, name, date
df

"""**Xử lý các giá trị khuyết (NaN) trên dòng và cột**


"""

df = df.dropna(axis = 0, how = 'all') #loại bỏ các dòng mà có tất cả các thuộc tính đều là NaN
df = df.dropna(axis = 1, how = 'any') # loại bỏ cột mà có NaN
df

"""**In ra tên của các cột sau khi đã xử lý NaN**"""

headname = list(df.columns) # danh sách tên các cột
print(headname)

"""**Trích xuất dữ liệu**"""

df_Xtrain = df.drop(['PRCP'], axis = 1) # gán df_Xtrain là df bỏ đi cột PRCP 
df_ytrain = df['PRCP'] # gán df_ytrain là cột PRCP
df_Xtrain
df_ytrain

"""**Kiểm định tương quan**.


**Bạn có thể tham khảo thêm tại đây:**

https://medium.com/nerd-for-tech/hypothesis-testing-on-linear-regression-c2a1799ba964
"""

import statsmodels.api as sm  

features_name = ['CONST'] + list(df_Xtrain.columns)
y_train = np.asarray(df_ytrain, dtype=float)
X_train = sm.add_constant(np.asarray(df_Xtrain, dtype=float))
model = sm.OLS(y_train, X_train).fit()
print(model.summary(xname=features_name))

"""**Trích lọc ra những feature có p-value <= 0.05 (= alpha)**

**Điều này có nghĩa rằng những feature này có mối liên hệ tuyến tính với lượng mưa**
"""

features_name = np.asarray(features_name)

selected_features = features_name[np.where(model.pvalues <= 0.05)]

print(selected_features)

X = np.array(df[selected_features[0]]).reshape(-1, 1)
for i in range(1, len(selected_features)): 
    X = np.c_[X, np.array(df[selected_features[i]]).reshape(-1, 1)]
y = np.array(df['PRCP']).reshape(-1, 1)
X = np.c_[np.ones((X.shape[0], 1)), X]

"""**Chia tập dữ liệu ra thành 2 tập train (80%) và test (20%)**"""

X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y, test_size = 0.2, random_state = 5)

"""**Lọc những điểm dữ liệu bị nhiễu**

**Tìm hiểu thêm tại đây:**

https://medium.com/mlearning-ai/how-to-find-and-remove-outliers-from-a-regression-in-python-449bc9e13101
"""

from sklearn.neighbors import LocalOutlierFactor

lof = LocalOutlierFactor(contamination = 0.05, n_neighbors = 20, novelty = False) # Tìm và loại bỏ 5% điểm dữ liệu ngoại lai
yhat = lof.fit_predict(X_train)

#Chọn toàn bộ hàng không phải là những điểm dữ liệu ngoại lai 

mask = yhat != -1

#Chọn toàn bộ hàng là những điểm dữ liệu ngoại lai

non_mask = yhat == -1

X_train, y_train = X_train[mask, :], y_train[mask]

print(X_train.shape, y_train.shape)

"""**Hàm ReLU trả về x nếu x > 0 ngược lại trả về 0.**"""

def ReLU(x):
  return np.maximum(x, 0)

"""Sau bước kiểm định ta đã có được các thuộc tính CDSD ($x_1$), DP01 ($x_2$), DP10 ($x_3$), DT00 ($x_4$), ,DX70 ($x_5$), , EMXP ($x_6$) có liên hệ tuyến tính, giả sử $h_\theta$ là hàm biểu diễn lượng mưa dự đoán và m là số dòng của dữ liệu ta có:

$h_\theta(x) = \theta_0 + \theta_1 * x_1 + \theta_2 *x_2 + \theta_3 *x_3 + \theta_4 *x_4 + \theta_5 *x_5 + \theta_6 *x_6$
    
Hay ta có thể viết như sau: $h_\theta(x) = X * \theta $

Với: $X = \begin{pmatrix} x_0 & x_1 & x_2 & x_3 & x_4 & x_5 & x_6 \end{pmatrix} \in m \times 6, \theta = \begin{pmatrix} \theta_0 \\ \theta_1 \\ \theta_2 \\ \theta_3 \\ \theta_4 \\ \theta_5 \\ \theta_6 \end{pmatrix}$, trong đó $x_0 = \begin{pmatrix} 1 \\ 1 \\ \vdots \\ 1 \end{pmatrix}$

Hàm mất mát của mô hình Linear Regression được định nghĩa như sau:
    
$J(\theta) = \frac{1}{2m} \sum_{i = 1}^m\frac{1}{2}[h_\theta (x^{(i)}) - y^{
(i)}]^2$
   
Ta sẽ đi tìm các hệ số $\theta$ sao cho hàm $J(\theta)$ đạt giá trị bé nhất, thật vậy:
    
$\begin{pmatrix} h_\theta(x^1) \\ h_\theta(x^2) \\ \vdots \\ h_\theta(x^m) \end{pmatrix} - \begin{pmatrix} y^1 \\ y^2 \\ \vdots \\ y^m \end{pmatrix}$

$= \begin{pmatrix} \theta x^1 \\ \theta x^2 \\ \vdots \\ \theta x^m \end{pmatrix} - \begin{pmatrix} y^1 \\ y^2 \\ \vdots \\ y^m \end{pmatrix}$

$= \begin{pmatrix} \theta_0 + \theta_1 * x_1^1 + \theta_2 *x_2^1 + \theta_3 *x_3^1 + \theta_4 *x_4^1 + \theta_5 *x_5^1 + \theta_6 *x_6^1 \\ \theta_0 + \theta_1 * x_1^2 + \theta_2 *x_2^2 + \theta_3 *x_3^2 + \theta_4 *x_4^2 + \theta_5 *x_5^2 + \theta_6 *x_6^2 \\\vdots \\ \theta_0 + \theta_1 * x_1^m + \theta_2 *x_2^m + \theta_3 *x_3^m + \theta_4 *x_4^m + \theta_5 *x_5^m + \theta_6 *x_6^m \end{pmatrix} - \begin{pmatrix} y^1 \\ y^2 \\ \vdots \\ y^m \end{pmatrix}$

$= X\theta - y$
    
Ta nhận thấy rằng: $J(\theta) = (X\theta - y)^T (X\theta - y)$, ta tìm giá trị của $\theta$ sao cho hàm này bé nhất bằng cách phương trình đạo hàm $J'(\theta) = 0$, thật vậy ta có:
    
$J(\theta) = (X\theta - y)^T (X\theta - y)$

$= [(X\theta)^T - y^T](X\theta - y)$

$= (X\theta)^TX\theta - (X\theta)^Ty - y^T X\theta + y^Ty$ 

$= (X\theta)^TX\theta - y^TX\theta - y^TX\theta + y^Ty$ 

$= (X\theta)^TX\theta - 2y^TX\theta + y^Ty$
    
$\Rightarrow J'(\theta) = 2X^TX\theta - 2y^TX$
    
$\Rightarrow 2X^TX\theta  = 2y^TX$
    
$\Rightarrow (X^TX)^{-1}X^TX\theta  = (X^TX)^{-1}y^TX$
    
$\Rightarrow \theta  = (X^TX)^{-1}y^TX$
    
Vậy là ta đã có công thức cho $\theta$ và xem như bài toán được giải xong. Công thức này được gọi là **"Normal Equation"**.
    
Tuy nhiên, để dễ dàng thì chúng tôi sẽ sử dụng thư viện skikit-learn cũng được lấy ý tưởng như trên. Ở đây ngoài sử dụng thuật LinearRegression chúng tôi còn cho kết quả dự đoán đi qua hàm **ReLU** để khi kết quả dự đoán ra âm thì sẽ trả về 0 ngược lại thì trả về chính nó.
"""

from sklearn.linear_model import LinearRegression

model = LinearRegression(fit_intercept = False)
model.fit(X_train, y_train)

print('Accuracy: %.10f' % model.score(X_test, y_test))

y_pred = ReLU(model.predict(X_test)) # Cho kết quả dự đoán đi qua hàm ReLU để khi kết quả dự đoán < 0 sẽ trả về 0


plt.scatter(y_test, y_pred)
plt.show()

"""**Bảng dữ liệu gồm 2 cột, cột dự đoán và cột thực tế**"""

x_test = X_test[:, 0]
y_test2 = y_test[:, 0]
y_pred2 = y_pred[:, 0]

df_pred = pd.DataFrame({'Predicted': y_pred2, 'Actual': y_test2})
df_pred

df_pred.to_csv('/content/drive/MyDrive/TUDTK/Result.csv')

"""**Preprocessing data (tách data gốc thành tập train và tập test)**"""

plt.plot(y_test, 'go-')
plt.plot(y_pred, 'ro-')
plt.show()

"""**Các thông số dùng để đánh giá mô hình**"""

from sklearn import metrics
print('R Squared:', metrics.r2_score(y_test, y_pred))
print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred)) # MSE
print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred))) #RMSE
print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred)) # MAE
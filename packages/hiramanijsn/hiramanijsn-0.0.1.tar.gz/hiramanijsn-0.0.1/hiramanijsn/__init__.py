
def SVM():
    code = """
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix,accuracy_score
from matplotlib.colors import ListedColormap

# Loading the dataset
dataset = pd.read_csv(r"https://raw.githubusercontent.com/stavanR/Machine-Learning-Algorithms-Dataset/master/Social_Network_Ads.csv")

# Splitting the data into independent and dependent variables
X = dataset.iloc[:,[2,3]].values
y = dataset.iloc[:,4].values

# Splitting the data into training set and testing set
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=1/3,random_state=0)

# Feature scaling
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.fit_transform(X_test)

# Training the model with linear kernel
classifier = SVC(kernel='linear',random_state=0)
classifier.fit(X_train,y_train)

# Predicting the test set results
y_pred = classifier.predict(X_test)

# Evaluating the model using confusion matrix and accuracy score
cm = confusion_matrix(y_test,y_pred)
print(accuracy_score(y_test,y_pred))

# Visualizing the training set results using a meshgrid and contourf plot
x_set, y_set = X_train, y_train
x1, x2 = np.meshgrid(np.arange(start = x_set[:, 0].min() - 1, stop = x_set[:, 0].max() + 1, step=0.01),
                      np.arange(start = x_set[:, 1].min() - 1, stop = x_set[:, 1].max() + 1, step = 0.01))
plt.contourf(x1, x2, classifier.predict(np.array([x1.ravel(), x2.ravel()]).T).reshape(x1.shape),
             alpha = 0.75, cmap = ListedColormap(('red', 'green')))
plt.xlim(x1.min(), x1.max())
plt.ylim(x2.min(), x2.max())
for i, j in enumerate(np.unique(y_set)):
    plt.scatter(x_set[y_set == j, 0], x_set[y_set == j, 1],
                c = ListedColormap(('red', 'green'))(i), label = j)
plt.legend()
plt.show()

# Visualizing the testing set results using a meshgrid and contourf plot
x_set, y_set = X_test, y_test
x1, x2 = np.meshgrid(np.arange(start = x_set[:, 0].min() - 1, stop = x_set[:, 0].max() + 1, step=0.01),
                      np.arange(start = x_set[:, 1].min() - 1, stop = x_set[:, 1].max() + 1, step = 0.01))
plt.contourf(x1, x2, classifier.predict(np.array([x1.ravel(), x2.ravel()]).T).reshape(x1.shape),
             alpha = 0.75, cmap = ListedColormap(('red', 'green')))
plt.xlim(x1.min(), x1.max())
plt.ylim(x2.min(), x2.max())
for i, j in enumerate(np.unique(y_set)):
    plt.scatter(x_set[y_set == j, 0], x_set[y_set == j, 1],
                c = ListedColormap(('red', 'green'))(i), label = j)
plt.legend()
plt.show()

# Training the model with polynomial kernel
classifier = SVC(kernel='poly',random_state=0)
classifier.fit(X_train,y_train)

# Predicting the test set results
y_pred = classifier.predict(X_test)

# Evaluating the model using confusion matrix and accuracy score
cm = confusion_matrix(y_test,y_pred)
print(accuracy_score(y_test,y_pred))

# Training the model with radial basis function (rbf) kernel
classifier = SVC(kernel='rbf',random_state=0)
classifier.fit(X_train,y_train)

# Predicting the test set results
y_pred = classifier.predict(X_test)

# Evaluating the model using confusion matrix and accuracy score
cm = confusion_matrix(y_test,y_pred)
print(accuracy_score(y_test,y_pred))

# Trying different values of regularization parameter (C) and gamma for rbf kernel

# C = 0.1, gamma = default (scale)
classifier = SVC(C=0.1,kernel='rbf',random_state=0)
classifier.fit(X_train,y_train)
y_pred = classifier.predict(X_test)
cm = confusion_matrix(y_test,y_pred)
print(accuracy_score(y_test,y_pred))

# C = 1, gamma = default (scale)
classifier = SVC(C=1,kernel='rbf',random_state=0)
classifier.fit(X_train,y_train)
y_pred = classifier.predict(X_test)
cm = confusion_matrix(y_test,y_pred)
print(accuracy_score(y_test,y_pred))

# C = 10, gamma = default (scale)
classifier = SVC(C=10,kernel='rbf',random_state=0)
classifier.fit(X_train,y_train)
y_pred = classifier.predict(X_test)
cm = confusion_matrix(y_test,y_pred)
print(accuracy_score(y_test,y_pred))

# C = 100, gamma = default (scale)
classifier = SVC(C=100,kernel='rbf',random_state=0)
classifier.fit(X_train,y_train)
y_pred = classifier.predict(X_test)
cm = confusion_matrix(y_test,y_pred)
print(accuracy_score(y_test,y_pred))

# C = 10, gamma = 0.1
classifier = SVC(C=10,kernel='rbf',random_state=0,gamma=0.1)
classifier.fit(X_train,y_train)
y_pred = classifier.predict(X_test)
cm = confusion_matrix(y_test,y_pred)
print(accuracy_score(y_test,y_pred))

# C = 10, gamma = 1
classifier = SVC(C=10,kernel='rbf',random_state=0,gamma=1)
classifier.fit(X_train,y_train)
y_pred = classifier.predict(X_test)
cm = confusion_matrix(y_test,y_pred)
print(accuracy_score(y_test,y_pred))

# C = 10, gamma = 10
classifier = SVC(C=10,kernel='rbf',random_state=0,gamma=10)
classifier.fit(X_train,y_train)
y_pred = classifier.predict(X_test)
cm = confusion_matrix(y_test,y_pred)
print(accuracy_score(y_test,y_pred))

# C = 10, gamma = 100
classifier = SVC(C=10,kernel='rbf',random_state=0,gamma=100)
classifier.fit(X_train,y_train)
y_pred = classifier.predict(X_test)
cm = confusion_matrix(y_test,y_pred)
print(accuracy_score(y_test,y_pred))

"""
    return code

def Forest():
    code = """
# Importing required libraries

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix,accuracy_score
from matplotlib.colors import ListedColormap

# Loading the dataset

dataset = pd.read_csv(r"https://raw.githubusercontent.com/stavanR/Machine-Learning-Algorithms-Dataset/master/Social_Network_Ads.csv")

# Extracting the feature and target variables

X = dataset.iloc[:,[2,3]].values
y = dataset.iloc[:,4].values

# Splitting the data into training and testing sets

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=1/5,random_state=0)

# Feature scaling

sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.fit_transform(X_test)

# Building a random forest classifier with 10 trees using entropy criterion 

classifier = RandomForestClassifier(n_estimators=10,criterion='entropy',random_state=0)
classifier.fit(X_train,y_train)

# Making predictions on the test set

y_pred = classifier.predict(X_test)

# Evaluating the accuracy of the model

cm = confusion_matrix(y_test,y_pred)
print(accuracy_score(y_test,y_pred))

# Visualizing the classification boundary of the random forest classifier on the training set

x_set, y_set = X_train, y_train  
x1, x2 = np.meshgrid(np.arange(start = x_set[:, 0].min() - 1, stop = x_set[:, 0].max() + 1, step  =0.01),  
np.arange(start = x_set[:, 1].min() - 1, stop = x_set[:, 1].max() + 1, step = 0.01))  
plt.contourf(x1, x2, classifier.predict(np.array([x1.ravel(), x2.ravel()]).T).reshape(x1.shape),  
alpha = 0.75, cmap = ListedColormap(('red', 'green')))  
plt.xlim(x1.min(), x1.max())  
plt.ylim(x2.min(), x2.max())  
for i, j in enumerate(np.unique(y_set)):  
    plt.scatter(x_set[y_set == j, 0], x_set[y_set == j, 1],  
        c = ListedColormap(('red', 'green'))(i), label = j) 
plt.title("Random Forest Classification (Training set)")
plt.xlabel("Age")
plt.ylabel("Estimated Salary") 
plt.legend()  
plt.show()

# Visualizing the classification boundary of the random forest classifier on the testing set

x_set, y_set = X_test, y_test  
x1, x2 = np.meshgrid(np.arange(start = x_set[:, 0].min() - 1, stop = x_set[:, 0].max() + 1, step  =0.01),  
np.arange(start = x_set[:, 1].min() - 1, stop = x_set[:, 1].max() + 1, step = 0.01))  
plt.contourf(x1, x2, classifier.predict(np.array([x1.ravel(), x2.ravel()]).T).reshape(x1.shape),  
alpha = 0.75, cmap = ListedColormap(('red', 'green')))  
plt.xlim(x1.min(), x1.max()) 
plt.ylim(x2.min(), x2.max())  
for i, j in enumerate(np.unique(y_set)):  
    plt.scatter(x_set[y_set == j, 0], x_set[y_set == j, 1],  
        c = ListedColormap(('red', 'green'))(i), label = j) 
plt.title("Random Forest Classification (Testing set)")
plt.xlabel("Age")
plt.ylabel("Estimated Salary") 
plt.legend()  
plt.show()  

# Building random forest classifiers with different number of trees using both Gini and Entropy criteria

n = []
giniacc = []
for i in range(100):
  n.append(i + 1)
  classifier = RandomForestClassifier(n_estimators=i+1,criterion='gini',random_state=0)
  classifier.fit(X_train,y_train)
  y_pred = classifier.predict(X_test)
  cm = confusion_matrix(y_test,y_pred)
  giniacc.append(accuracy_score(y_test,y_pred))

entropyacc = []
for i in range(100):
  classifier = RandomForestClassifier(n_estimators=i+1,criterion='entropy',random_state=0)
  classifier.fit(X_train,y_train)
  y_pred = classifier.predict(X_test)
  cm = confusion_matrix(y_test,y_pred)
  entropyacc.append(accuracy_score(y_test,y_pred))

# Plotting the accuracy vs number of trees graph for both Gini and Entropy criteria

plt.plot(n,giniacc,label="Gini")
plt.plot(n,entropyacc,label="Entropy")
plt.legend()
plt.show()

"""
    return code

def NN():
    code = """
# Importing necessary libraries
import numpy as np

# Defining inputs and expected output for the AND Gate
inputs = np.array([[0,0],[0,1],[1,0],[1,1]])
expected_output = np.array([[0],[0],[0],[1]])

# Initializing the weights and biases with random values
inputlayerneurons, hiddenlayerneurons, outputlayerneurons = 2,1,1
hidden_weights = np.random.uniform(size=(inputlayerneurons,hiddenlayerneurons))
hidden_bias = np.random.uniform(size=(1,hiddenlayerneurons))
output_weights = np.random.uniform(size=(hiddenlayerneurons, outputlayerneurons))
output_bias = np.random.uniform(size=(1,outputlayerneurons))

# Defining the sigmoid function for activation
def sigmoid(x):
  return  1/(1+np.exp(-x))

# Defining the derivative of sigmoid function
def sigmoid_derivative(x):
  return  x*(1-x)

# Defining the learning rate and number of epochs
lr=0.1
epochs = 10000

# Training the model using Back Propagation algorithm
for i in range(epochs):
  # Forward Propagation
  hidden_layer_activation = np.dot(inputs, hidden_weights)
  hidden_layer_activation += hidden_bias
  hidden_layer_output = sigmoid(hidden_layer_activation)

  output_layer_activation = np.dot(hidden_layer_output, output_weights)
  output_layer_activation += output_bias
  predicted_output = sigmoid(output_layer_activation)

  # Back Propagation
  error = expected_output - predicted_output
  d_predicted_output = error * sigmoid_derivative(predicted_output)
  error_hidden_layer = d_predicted_output.dot(output_weights.T)
  d_hidden_layer = error_hidden_layer * sigmoid_derivative(hidden_layer_output)

  # Updating weights and biases
  output_weights += hidden_layer_output.T.dot(d_predicted_output) * lr
  output_bias += np.sum(d_predicted_output, axis=0, keepdims=True) * lr
  hidden_weights += inputs.T.dot(d_hidden_layer) * lr
  hidden_bias += np.sum(d_hidden_layer, axis=0, keepdims=True) * lr

# Printing the output and weights after training the model
print("Actual Output", expected_output)
print("Predicted Output", predicted_output)
print("Hidden Layer Weights", hidden_weights)
print("Hidden Layer Bias", hidden_bias)
print("Output Layer Weights", output_weights)

"""
    return code

def CNN():
    code = """
import numpy as np

answer = {0: "red", 1: "blue"}

# Initializing weights and expected outputs
inputs = np.array([[3, 1.5], [2, 1], [4, 1.5], [3, 1], [3.5, 0.5], [2, 0.5], [5.5, 1], [1, 1]])
expected_output = np.array([[0], [1], [0], [1], [0], [1], [0], [1]])

# Initializing the weights and biases with random values
input_layer_neurons, hidden_layer_neurons, output_layer_neurons = 2, 2, 1
hidden_weights = np.random.uniform(size=(input_layer_neurons, hidden_layer_neurons))
hidden_bias = np.random.uniform(size=(1, hidden_layer_neurons))
output_weights = np.random.uniform(size=(hidden_layer_neurons, output_layer_neurons))
output_bias = np.random.uniform(size=(1, output_layer_neurons))

# Defining the sigmoid activation function
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# Defining the derivative of the sigmoid function
def sigmoid_derivative(x):
    return x * (1 - x)

# Defining the learning rate (lr)
lr = 0.1

# Training the neural network
for i in range(10000):
    # Forward propagation
    hidden_layer_activation = np.dot(inputs, hidden_weights)
    hidden_layer_activation += hidden_bias
    hidden_layer_output = sigmoid(hidden_layer_activation)

    output_layer_activation = np.dot(hidden_layer_output, output_weights)
    output_layer_activation += output_bias
    predicted_output = sigmoid(output_layer_activation)

    # Backpropagation
    error = expected_output - predicted_output
    d_predicted_output = error * sigmoid_derivative(predicted_output)
    error_hidden_layer = d_predicted_output.dot(output_weights.T)
    d_hidden_layer = error_hidden_layer * sigmoid_derivative(hidden_layer_output)

    # Updating weights and biases
    output_weights += hidden_layer_output.T.dot(d_predicted_output) * lr
    output_bias += np.sum(d_predicted_output, axis=0, keepdims=True) * lr
    hidden_weights += inputs.T.dot(d_hidden_layer) * lr
    hidden_bias += np.sum(d_hidden_layer, axis=0, keepdims=True) * lr

# Testing the trained neural network
test_input = np.array([[4.5, 1]])

hidden_layer_activation = np.dot(test_input, hidden_weights)
hidden_layer_activation += hidden_bias
hidden_layer_output = sigmoid(hidden_layer_activation)

output_layer_activation = np.dot(hidden_layer_output, output_weights)
output_layer_activation += output_bias
predicted_output = sigmoid(output_layer_activation)

# Printing the predicted output and corresponding label
print("Predicted output:", predicted_output[0][0])

if predicted_output[0][0] <= 0.5:
    print("Label:", answer[0])  # Red
else:
    print("Label:", answer[1])  # Blue

"""
    return code

def Naive():
    code = """
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

#Load dataset from URL
df = pd.read_csv(r"https://raw.githubusercontent.com/dhirajk100/Naive-Bayes/master/NaiveBayes-Classification-Data.csv")

#Split dataset into features and target variable
X = df.iloc[:,:-1].values
y = df.iloc[:,-1].values

#Split dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size = 1/3, random_state = 42)

#Create a Gaussian Naive Bayes model
model = GaussianNB()

#Train the model using the training set
model.fit(X_train,y_train)

#Make predictions on the testing set
y_pred = model.predict(X_test)

#Compute the accuracy of the model
accuracy = accuracy_score(y_test,y_pred)

#Print the accuracy
print("Accuracy : ",accuracy)

#Plot the full dataset with color-coded diabetes labels
sns.scatterplot(x="glucose",y="bloodpressure", data=df, hue="diabetes").set(title="Full Data")
plt.show()

#Plot the testing data with color-coded actual diabetes labels
sns.scatterplot(x=X_test[:,0],y=X_test[:,1], hue=y_test).set(title="Testing Data")
plt.show()

"""
    return code

def KNN():
    code = """
#Import necessary libraries

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix,accuracy_score
from matplotlib.colors import ListedColormap

#Load dataset

df = pd.read_csv("file.csv")

#Split dataset into independent and dependent variables

x = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

#Split the dataset into training and testing data

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size = 1/3, random_state = 0)

#Train the KNN classifier model

model = KNeighborsClassifier(n_neighbors=3, metric='minkowski', p=2)
model.fit(X_train,y_train)

#Predict the testing data and calculate accuracy score and confusion matrix

y_pred = model.predict(X_test)
cm= confusion_matrix(y_test, y_pred)
accuracy = accuracy_score(y_test,y_pred)

#Visualize the training data with different classes

values = []
for x in y_train:
if(x=="A"):
values.append(0)
elif(x=="B"):
values.append(1)
else:
values.append(2)
scatter = plt.scatter(X_train[:,0],X_train[:,1],c=values,cmap=ListedColormap(["red","blue","green"]))
plt.legend(handles=scatter.legend_elements()[0],labels=["A","B","C"],title="Class")
plt.xlim([0,5])
plt.ylim([0,5])
plt.xlabel("X1")
plt.ylabel("X2")
plt.title("Training data")
plt.show()

#Visualize the testing data with different classes

values = []
for x in y_test:
if(x=="A"):
values.append(0)
elif(x=="B"):
values.append(1)
else:
values.append(2)
scatter = plt.scatter(X_test[:,0],X_test[:,1],c=values,cmap=ListedColormap(["red","blue","green"]))
plt.legend(handles=scatter.legend_elements()[0],labels=["A","B","C"],title="Class")
plt.xlim([0,5])
plt.ylim([0,5])
plt.xlabel("X1")
plt.ylabel("X2")
plt.title("Testing data")
plt.show()

#Visualize the predicted data with different classes

values = []
for x in y_pred:
if(x=="A"):
values.append(0)
elif(x=="B"):
values.append(1)
else:
values.append(2)
scatter = plt.scatter(X_test[:,0],X_test[:,1],c=values,cmap=ListedColormap(["red","blue","green"]))
plt.legend(handles=scatter.legend_elements()[0],labels=["A","B","C"],title="Class")
plt.xlim([0,5])
plt.ylim([0,5])
plt.xlabel("X1")
plt.ylabel("X2")
plt.title("Predicted data")
plt.show()

#Predict the class for given data points and visualize them on scatter plot

y_pred = []
y_pred.append(model.predict([[3,2]]))
y_pred.append(model.predict([[4.2,1.8]]))
scatter = plt.scatter([3,4.2],[2,1.8])
plt.xlim([0,5])
plt.ylim([0,5])
plt.xlabel("X1")
plt.ylabel("X2")
plt.title("Predicted data")
plt.text(3,2,f"(3,2) {y_pred[0][0]}")
plt.text(4.2,1.8,f"(4.2,1.8) {y_pred[1][0]}")
plt.show()
print("Accuracy: ",accuracy*100)
"""
    return code

def PCA():
    code = """
# Importing required Libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Load iris dataset
dataset = pd.read_csv('iris.data')
X = dataset.iloc[:,:-1].values

# Standardize the data
sc = StandardScaler()
X = sc.fit_transform(X)

# Perform PCA with 2 components
pca = PCA(n_components = 2)
X_pca = pca.fit_transform(X)

# Print explained variance and explained variance ratio
explained_variance = pca.explained_variance_
explained_variance_ratio = pca.explained_variance_ratio_
print(explained_variance)
print(explained_variance_ratio,'\n\n')

"""
    return code

def KMeans():
    code = """
# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Importing the dataset
dataset = pd.read_csv('https://raw.githubusercontent.com/stavanR/Machine-Learning-Algorithms-Dataset/master/Mall_Customers.csv')
X = dataset.iloc[:, [3, 4]].values

# Using the elbow method to find the optimal number of clusters
from sklearn.cluster import KMeans
wcss = []
for i in range(1, 11):
  kmeans = KMeans(n_clusters = i, init = 'k-means++', random_state = 42)
  kmeans.fit(X)
  wcss.append(kmeans.inertia_)
plt.plot(range(1, 11), wcss)
plt.title('The Elbow Method')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')
plt.show()

# Fitting K-Means to the dataset
kmeans = KMeans(n_clusters = 5, init = 'k-means++', random_state = 42)
y_kmeans = kmeans.fit_predict(X)

# Visualising the clusters
plt.scatter(X[y_kmeans == 0, 0], X[y_kmeans == 0, 1], s = 100, c = 'red', label = 'Cluster 1')
plt.scatter(X[y_kmeans == 1, 0], X[y_kmeans == 1, 1], s = 100, c = 'blue', label = 'Cluster 2')
plt.scatter(X[y_kmeans == 2, 0], X[y_kmeans == 2, 1], s = 100, c = 'green', label = 'Cluster 3')
plt.scatter(X[y_kmeans == 3, 0], X[y_kmeans == 3, 1], s = 100, c = 'cyan', label = 'Cluster 4')
plt.scatter(X[y_kmeans == 4, 0], X[y_kmeans == 4, 1], s = 100, c = 'magenta', label = 'Cluster 5')
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s = 300, c = 'yellow', label = 'Centroids')
plt.title('Clusters of customers')
plt.xlabel('Annual Income (k$)')
plt.ylabel('Spending Score (1-100)')
plt.legend()
plt.show()

"""
    return code

def LR():
    code = """
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
dataset=pd.read_csv(r"C:\Users\Jugal\Desktop\SEM-6\MACHINE LEARNING\Salary_Data.csv")
X=dataset.iloc[:,:-1].values
y=dataset.iloc[:,1].values
from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=1/3,random_state=0)
from sklearn.linear_model import LinearRegression
regressor=LinearRegression()
regressor.fit(X_train,y_train)
y_pred=regressor.predict(X_test)
r_sq = regressor.score(X_train, y_train)
print('coefficient of determination:', r_sq)
print('intercept W0:', regressor.intercept_)
print('slope W1:', regressor.coef_)
plt.scatter(X_train,y_train,color='red')
plt.plot(X_train,regressor.predict(X_train),color='blue')
plt.title('Salary vs Experience')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.show()
plt.scatter(X_test,y_test,color='red')
plt.plot(X_train,regressor.predict(X_train),color='blue')
plt.title('Salary vs Experience')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.show()
"""
    return code

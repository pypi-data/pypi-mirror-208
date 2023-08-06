import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df_zc_r = pd.read_csv('https://raw.githubusercontent.com/NishanD21/Astronomical-Objects-Classification/main/Datasets/sgq_classification_zc_r.csv')

x = df_zc_r.drop("class",axis='columns')
y = df_zc_r["class"]

from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.1,random_state=42, stratify=y)

from sklearn.ensemble import RandomForestClassifier

# initializing model
model_rf = RandomForestClassifier(n_estimators=100, random_state=42)
model_rf.fit(x_train,y_train)

def predictor(alpha, delta, u, g, i, r, z, redshift): # To predict the class of the astronomical objet for given features.
    # Load the trained model
    model = model_rf
    
    # Make the prediction
    x = np.array([[alpha, delta, u, g, i, r, z, redshift]])
    prediction = model.predict(x)[0]
    
    # Map the predicted value to the desired class
    if prediction == 0:
        return "Galaxy"
    elif prediction == 1:
        return "Quasar"
    elif prediction == 2:
        return "Star"
    else:
        return "Unknown"

data = df_zc_r.copy()

def plot_feature_distribution(data): # To plot the distribution of each feature in the dataset.

    # Extract the features
    features = data.columns[:-1]

    # Plot the distribution of each feature
    for feature in features:
        sns.displot(data=data, x=feature, hue='class', kde=True)
        plt.title(f"Distribution of {feature}")
        plt.show()

def plot_feature_distribution_t(): # To plot the distribution of each feature in the dataset.

    # Extract the features
    features = data.columns[:-1]

    # Plot the distribution of each feature
    for feature in features:
        sns.displot(data=data, x=feature, hue='class', kde=True)
        plt.title(f"Distribution of {feature}")
        plt.show()


def plot_correlation_matrix(data): #To Plot the correlation matrix of the dataset.

    # Calculate the correlation matrix
    corr_matrix = data.corr()

    # Plot the correlation matrix
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
    plt.title("Correlation Matrix")
    plt.show()

def plot_correlation_matrix_t(): #To Plot the correlation matrix of the dataset.

    # Calculate the correlation matrix
    corr_matrix = data.corr()

    # Plot the correlation matrix
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
    plt.title("Correlation Matrix")
    plt.show()


def get_feature_names():# To get the names of the features used to train the model.

    return ['alpha', 'delta', 'u', 'g', 'i', 'r', 'z', 'redshift']

# Feature descriptions
FEATURES = {
    'u': 'U-band (ultraviolet) magnitude',
    'g': 'G-band (green) magnitude',
    'r': 'R-band (red) magnitude',
    'i': 'I-band (infrared) magnitude',
    'z': 'Z-band (near-infrared) magnitude',
    'redshift': 'Redshift (measure of the expansion of the universe)',
    'ra': 'Right ascension (angular distance eastward along the celestial equator from the vernal equinox)',
    'dec': 'Declination (angular distance north or south of the celestial equator)'
}

def get_feature_descriptions(): #To get the feature descriptions
    return FEATURES


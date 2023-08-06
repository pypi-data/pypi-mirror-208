import setuptools

setuptools.setup(
    name='bfcm',
    version='0.0.8',
    author='Isel Grau, Gonzalo Nápoles, Leonardo Concepción, Fabian Hoitsma, Lisa Koutsoviti, João Paulo Papa, Koen Vanhoof',
    author_email='lisa.koutsoviti@uhasselt.be',
    description='A library that quantifies implicit bias in tabular data with Fuzzy Cognitive Maps',
    long_description='This python package includes the functions related to the papers "Modeling implicit bias with fuzzy cognitive maps" (Nápoles et al., 2022) and "Measuring Implicit Bias Using SHAP Feature Importance and Fuzzy Cognitive Maps" (Grau et al., 2023). An additional method included is using clustering to automatically discover the groups describing a numeric feature, which allows computing the association between numeric and categorical features using Cramer\'s V coefficient',
    packages=['bfcm'],
    license='MIT'
)
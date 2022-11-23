# Accenture Challenge: Supply Chain Resilience

## Table of Contents

[I. Introduction](#i-introduction)  
[II. Installation](#ii-installation)

Our pitch deck can be found [here](https://github.com/KensingtonOscupant/datathon-fme2022/blob/main/supplychain_presentation.pdf).

## I. Introduction

This repository details a case study on supply chain resilience using data from a European fashion retailer provided by Accenture. It aims to determine how likely it is for an order not to reach the customer on time. The project was created at [Datathon FME 2022](https://datathon.cat/). Our final model was too large to be deployed on GitHub, which is why we used a more lightweight version of it only containing the XGBoost model in the ensemble for deploying the app to production. **A live version is available [here](https://kensingtonoscupant-datathon-fme2022-srcstreamlit-streaml-p41g62.streamlit.app/).**

## II. Installation

After cloning the repository to your local machine, you first need to download the data from Accenture from [Kaggle](https://www.kaggle.com/competitions/datathon-2022-upc-accenture/data) (Kaggle account required). The path to cities_data.csv should then look something like data/datathon_SC_ACN_22/cities_data.csv. Then install all necessary dependencies (list can be found on the production branch [here](https://github.com/KensingtonOscupant/datathon-fme2022/blob/streamlit_prod/requirements.in)). After that, run the notebook "LF 002 Intial model exploration.ipynb", which creates the model and places it in the models directory. Then, head to the base directory of the project and run "streamlit run src/streamlit.py". This should run the project on your localhost. 

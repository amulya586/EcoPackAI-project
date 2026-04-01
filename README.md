EcoPackAI – Intelligent Sustainable Packaging Recommendation System

EcoPackAI is a machine learning powered web application that helps users select the most efficient and eco-friendly packaging materials. The system evaluates materials based on cost, carbon emissions, recyclability, and other sustainability factors to generate optimized recommendations.

The application integrates trained ML models with a Flask backend and interactive frontend to provide real-time insights and analytics for sustainable decision making.

Key Capabilities

AI-Based Material Recommendation
Takes product weight and fragility as input
Predicts cost and CO2 emissions
Ranks materials using a combined sustainability score

Interactive Dashboard
Displays CO2 reduction percentage
Shows estimated cost savings
Tracks material usage trends
Visualizes sustainability metrics using charts

User Management
Secure login and registration system
Session-based authentication

Data Persistence
Stores product details
Manages material dataset
Supports PostgreSQL integration

Core Features

Smart recommendation engine
Cost prediction model
CO2 emission prediction model
Material ranking system
Interactive dashboard with graphs
Downloadable reports
Web-based user interface

Project Structure

ecopackai
│
├── data
│   ├── cleaned_materials.csv
│   ├── materials dataset.csv
│   └── product dataset.csv
│
├── models
│   ├── co2_model.pkl
│   ├── cost_model.pkl
│   ├── ecopackai.ipynb
│   └── metrics.json
│
├── templates
│   ├── dashboard.html
│   ├── index.html
│   ├── login.html
│   └── register.html
│
├── app.py
├── Procfile
├── render.yaml
├── requirements.txt
├── runtime.txt
└── .gitignore

How the System Works

User logs into the application
User inputs product details such as weight and fragility
Frontend sends request to Flask backend
Machine learning models predict cost and CO2 emission
System evaluates and ranks materials
Best material recommendation is displayed
Dashboard visualizes sustainability insights
User can export reports

Technology Stack

Frontend
HTML CSS Bootstrap JavaScript

Backend
Python Flask

Machine Learning
Scikit-learn
Pandas NumPy

Database
PostgreSQL

Visualization
Matplotlib Chart.js

Deployment
Render

Installation Guide

Clone the repository

git clone https://github.com/amulya586/EcoPackAI-project.git

cd EcoPackAI-project

Install required packages

pip install -r requirements.txt

Run the application

python app.py

Access the application

http://127.0.0.1:5000

Application Modules

Data Processing
Cleaning and preparation of material datasets

Machine Learning
Training cost and CO2 prediction models
Model evaluation using performance metrics

Web Application
Flask API development
Frontend UI integration
Authentication system

Dashboard and Deployment
Visualization of analytics
Report generation
Cloud deployment using Render

API Overview

GET /
Loads homepage

POST /login
Handles user authentication

POST /register
Registers new users

GET /dashboard
Displays analytics dashboard

POST /predict
Returns material recommendations

Challenges Faced

Integrating ML models with Flask
Handling database connectivity
Maintaining user sessions
Generating dynamic charts
Implementing download features

Improvements Implemented

Optimized API response handling
Improved frontend interaction
Fixed authentication flow
Enhanced dashboard visualization
Stabilized deployment configuration

Future Scope

Increase dataset size for better accuracy
Add real-time recommendation updates
Improve UI/UX design
Integrate more sustainability metrics
Enable mobile-friendly interface
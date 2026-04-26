# Social Media Analytics Platform

## Overview
This project is a full-stack web application built with Python and Flask that dynamically ingests social media data, stores it in a NoSQL database, and processes it through multiple analytical modules. It features an interactive dashboard to visualize case study insights and includes an automated report generation tool.

## Key Features
* Dynamic Data Collection: Integrates with the Apify API to fetch live social media data.
* Database Integration: Stores and manages scraped data using MongoDB.
* Sentiment Analysis: Utilizes Natural Language Processing (TextBlob) to categorize post sentiment.
* Network Analysis & Influencer Detection: Uses NetworkX to map hashtag co-occurrences and Eigenvector Centrality to rank influencers.
* Content Evaluation: Includes heuristics for Fake News/Clickbait detection.
* Recommendation System: Employs Content-Based Filtering (Scikit-learn TF-IDF and Cosine Similarity) to recommend similar posts.
* Automated Reporting: Generates formatted, printable HTML/PDF reports of the analytics dashboard.

## Prerequisites
Before running this application, ensure you have the following installed on your system:
1. Python 3.8 or higher
2. MongoDB Community Server

## Installation & Setup Guide

### 1. Database Setup (MongoDB)
* Download and install MongoDB Community Server from the official MongoDB website.
* During the installation process, ensure the box for "Install MongoD as a Service" is checked. This allows the database engine to run automatically in the background.
* Note: The application connects to the default local MongoDB URI: mongodb://localhost:27017/

### 2. Application Setup
* Extract the project files into a dedicated directory.
* Open a terminal or command prompt and navigate to the project directory.
* Install the required Python dependencies by running the following command:
  pip install flask pandas textblob plotly networkx scikit-learn pymongo apify-client

### 3. API Configuration
* Open the `scraper.py` file in a text editor.
* Locate the `APIFY_TOKEN` variable at the top of the file.
* Replace the placeholder string with your actual Apify API token.

## Usage Instructions

### Step 1: Data Ingestion
To pull fresh data from the API and populate your MongoDB database, run the scraper script from your terminal:
`python scraper.py`
Wait for the terminal to confirm that the posts have been successfully injected into MongoDB.

### Step 2: Launch the Server
Start the Flask backend server by running:
`python app.py`

### Step 3: Access the Dashboard
* Open a web browser and navigate to: http://127.0.0.1:5000
* Log in using the default administrator credentials:
  * Username: admin
  * Password: password123
* Use the dashboard to explore the interactive visualizations.
* To export your findings, click the "Generate Final Report" button and use your browser's print function to save the page as a PDF.

## Directory Structure
* app.py          (Main Flask application backend)
* scraper.py      (Apify API data extraction script)
* templates/      (HTML user interface files)
  * login.html
  * dashboard.html
  * report.html

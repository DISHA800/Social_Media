from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import pandas as pd
from textblob import TextBlob
import plotly.express as px
import networkx as nx
from collections import Counter
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pymongo

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_project'
USER_DATA = {"admin": "password123"}

def analyze_data():
    items = []  # Explicitly define items first to prevent NameErrors!
    
    try:
        # Connect to MongoDB 
        mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = mongo_client["social_media_analytics"]
        collection = db["posts"]
        
        # Fetch all documents from the collection
        items = list(collection.find({}))
    except Exception as e:
        print(f"Database error: {e}")
        return None, None, None, None, None, None

    if not items: 
        return None, None, None, None, None, None

    sentiments = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    fake_news_stats = {'Real (Verified)': 0, 'Suspicious (Clickbait)': 0}
    all_hashtags = []
    G = nx.Graph() 
    all_texts = []

    # Fake news heuristic triggers for MVP
    suspicious_keywords = ['shocking', 'secret', 'hoax', 'miracle', 'conspiracy', 'banned', 'fake']

    for item in items:
        # Robust extraction for X or Facebook
        text = item.get('message', item.get('text', item.get('full_text', item.get('content', ''))))
        if not text: continue
        all_texts.append(text)
        
        # --- MODULE 1: Sentiment ---
        polarity = TextBlob(text).sentiment.polarity
        if polarity > 0.05: sentiments['Positive'] += 1
        elif polarity < -0.05: sentiments['Negative'] += 1
        else: sentiments['Neutral'] += 1
            
        # --- MODULE 2: Trends ---
        tags = [tag.lower() for tag in re.findall(r"#(\w+)", text)]
        all_hashtags.extend(tags)
        
        # --- MODULE 3: Network ---
        for i in range(len(tags)):
            for j in range(i+1, len(tags)):
                if G.has_edge(tags[i], tags[j]): G[tags[i]][tags[j]]['weight'] += 1
                else: G.add_edge(tags[i], tags[j], weight=1)

        # --- MODULE 5: Fake News Detection ---
        is_suspicious = any(word in text.lower() for word in suspicious_keywords)
        if is_suspicious: fake_news_stats['Suspicious (Clickbait)'] += 1
        else: fake_news_stats['Real (Verified)'] += 1

    # --- Charts Generation ---
    sentiment_chart = px.pie(values=list(sentiments.values()), names=list(sentiments.keys()), 
                             color=list(sentiments.keys()), color_discrete_map={'Positive':'#28a745', 'Negative':'#dc3545', 'Neutral':'#6c757d'}).to_html(full_html=False)

    top_tags = Counter(all_hashtags).most_common(10)
    trends_chart = px.bar(x=[t[0] for t in top_tags], y=[t[1] for t in top_tags], labels={'x':'Hashtag', 'y':'Count'}).to_html(full_html=False) if top_tags else "<p>No hashtags found.</p>"

    net_stats = f"<ul><li><strong>Nodes:</strong> {len(G.nodes)}</li><li><strong>Edges:</strong> {len(G.edges)}</li></ul>"

    influencer_chart = "<p class='text-muted'>Not enough hashtag connections.</p>"
    if len(G.nodes) > 2:
        try:
            centrality = nx.eigenvector_centrality(G, max_iter=1000)
            top_inf = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
            influencer_chart = px.bar(x=[i[1]*100 for i in top_inf], y=[i[0] for i in top_inf], orientation='h', labels={'x':'Score', 'y':'Node'}).to_html(full_html=False)
        except: pass

    # --- MODULE 5 Chart (Fake News) ---
    fake_news_chart = px.pie(values=list(fake_news_stats.values()), names=list(fake_news_stats.keys()), 
                             color=list(fake_news_stats.keys()), color_discrete_map={'Real (Verified)':'#0dcaf0', 'Suspicious (Clickbait)':'#ffc107'}).to_html(full_html=False)

    # --- MODULE 4: Recommendation System (Content-Based Filtering) ---
    recommendation_html = "<p class='text-muted'>Not enough text to recommend.</p>"
    if len(all_texts) > 3:
        # Using TF-IDF and Cosine Similarity from scikit-learn
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(all_texts)
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Recommend posts similar to the very first post
        sim_scores = list(enumerate(cosine_sim[0]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        top_indices = [i[0] for i in sim_scores[1:4]] # Get top 3 (excluding itself)
        
        rec_list = "".join([f"<li class='mb-2'><strong>Similarity Score {round(sim_scores[i][1]*100, 1)}%:</strong> {all_texts[idx][:100]}...</li>" for i, idx in enumerate(top_indices, 1)])
        
        recommendation_html = f"<div><p><strong>Target Post:</strong> {all_texts[0][:100]}...</p><h6>Top 3 Recommended Similar Posts:</h6><ul>{rec_list}</ul></div>"

    return sentiment_chart, trends_chart, net_stats, influencer_chart, fake_news_chart, recommendation_html

@app.route('/')
def home():
    if 'username' in session: return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.form.get('username') == "admin" and request.form.get('password') == "password123":
        session['username'] = "admin"
        return redirect(url_for('dashboard'))
    return render_template('login.html', error="Invalid Credentials.")

@app.route('/dashboard')
def dashboard():
    if 'username' not in session: return redirect(url_for('home'))
    sent, trends, net_stats, inf, fake, rec = analyze_data()
    return render_template('dashboard.html', username=session['username'],
                           sentiment_chart=sent, trends_chart=trends, 
                           network_stats=net_stats, influencer_chart=inf,
                           fake_news_chart=fake, recommendation_html=rec)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/report')
def generate_report():
    if 'username' not in session: return redirect(url_for('home'))
    
    # Grab the analyzed data again for the report
    sent, trends, net_stats, inf, fake, rec = analyze_data()
    
    return render_template('report.html', 
                           sentiment_chart=sent, 
                           trends_chart=trends, 
                           network_stats=net_stats, 
                           influencer_chart=inf,
                           fake_news_chart=fake,
                           recommendation_html=rec)
    
if __name__ == '__main__':
    app.run(debug=True)
import requests
import os
from datetime import datetime, timedelta

def fetch_trending_news(limit=10):
    """
    Fetch trending news articles from NewsAPI
    """
    api_key = os.getenv('NEWS_API_KEY')
    
    if not api_key:
        raise Exception("NEWS_API_KEY not found in environment variables")
    
    # Get news from last 24 hours
    from_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'apiKey': api_key,
        'language': 'en',
        'sortBy': 'popularity',
        'pageSize': limit,
        'from': from_date
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'ok':
            articles = []
            for article in data['articles']:
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'urlToImage': article.get('urlToImage', ''),
                    'publishedAt': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'content': article.get('content', '')
                })
            return articles
        else:
            raise Exception(f"NewsAPI error: {data.get('message', 'Unknown error')}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch news: {str(e)}")
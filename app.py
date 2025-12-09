from flask import Flask, render_template, request, jsonify, send_file
import os
from dotenv import load_dotenv
from modules.news_scraper import fetch_trending_news
from modules.script_generator import generate_script
from modules.scene_analyzer import analyze_scenes
from modules.media_fetcher import fetch_media
from modules.video_assembler import create_video
import json
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['TEMP_FOLDER'] = 'temp'

# Create necessary folders
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/trending-news', methods=['GET'])
def get_trending_news():
    try:
        articles = fetch_trending_news(limit=10)
        return jsonify({'success': True, 'articles': articles})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-video', methods=['POST'])
def generate_video():
    try:
        data = request.json
        article = data.get('article')
        
        if not article:
            return jsonify({'success': False, 'error': 'No article provided'}), 400
        
        # Step 1: Generate script using GROQ
        print("Generating script...")
        script = generate_script(article)
        
        # Step 2: Analyze scenes using Gemini
        print("Analyzing scenes...")
        scenes = analyze_scenes(script)
        
        # Step 3: Fetch media from Pexels
        print("Fetching media...")
        media_files = fetch_media(scenes)
        
        # Step 4: Create video
        print("Creating video...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'video_{timestamp}.mp4'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        create_video(script, scenes, media_files, output_path)
        
        return jsonify({
            'success': True,
            'video_url': f'/outputs/{output_filename}',
            'script': script,
            'scenes': scenes
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/outputs/<filename>')
def serve_video(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
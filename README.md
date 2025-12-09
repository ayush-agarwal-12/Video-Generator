# AI Video Generator

Automated video generation from trending news articles using AI-powered pipeline.

## Overview

This application transforms trending news articles into professional 30-60 second videos with AI-generated scripts, voiceovers, and relevant visuals.

## Tech Stack

### Backend
- **Python 3.9+** - Core programming language
- **Flask** - Web framework for API and routing
- **MoviePy** - Video editing and assembly
- **Pillow (PIL)** - Image processing and manipulation

### AI Services
- **GROQ API** - Script generation using Llama 3 (120B parameters)
- **Google Gemini API** - Scene analysis and visual recommendations
- **gTTS** - Text-to-speech for AI voiceover generation

### APIs & Data Sources
- **NewsAPI** - Trending news article aggregation
- **Pexels API** - Stock photos and videos

### Frontend
- **HTML5/CSS3** - User interface markup and styling
- **JavaScript (Vanilla)** - Client-side interactivity and AJAX

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                      Web Interface (Flask)                  │
│                     HTML/CSS/JavaScript                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask API Endpoints                       │
│              /api/trending-news                             │
│              /api/generate-video                            │
└──────┬──────┬──────────┬──────────┬──────────┬─────────────┘
       │      │           │          │          │
       ▼      ▼           ▼          ▼          ▼
   ┌─────┐┌──────┐  ┌────────┐ ┌──────┐  ┌────────┐
   │News ││Script│  │ Scene  │ │Media │  │ Video  │
   │Scrap││  Gen │  │Analysis│ │Fetch │  │Assembly│
   └─────┘└──────┘  └────────┘ └──────┘  └────────┘
```

### Pipeline Workflow

```
1. News Scraping
   ├─ Input: User request
   ├─ Process: NewsAPI fetches trending articles
   └─ Output: List of articles with metadata
   
2. Script Generation
   ├─ Input: Selected news article
   ├─ Process: GROQ AI generates 30-60s script
   └─ Output: Structured script with 3-4 scenes
   
3. Scene Analysis
   ├─ Input: Generated script with scene descriptions
   ├─ Process: Gemini analyzes visuals needed per scene
   └─ Output: Search keywords and media type per scene
   
4. Media Fetching
   ├─ Input: Scene keywords from analysis
   ├─ Process: Pexels API downloads stock media
   └─ Output: Images/videos saved to temp folder
   
5. Voiceover Generation
   ├─ Input: Full script text
   ├─ Process: gTTS converts text to speech
   └─ Output: MP3 audio file
   
6. Video Assembly
   ├─ Input: Media files + audio + timing data
   ├─ Process: MoviePy composites scenes with overlays
   └─ Output: Final MP4 video (1920x1080, 24fps)
```

## Project Structure

```
ai-video-generator/
│
├── app.py                      # Flask application & API routes
├── config.py                   # Configuration management
│
├── modules/
│   ├── news_scraper.py        # NewsAPI integration
│   ├── script_generator.py    # GROQ script generation
│   ├── scene_analyzer.py      # Gemini scene analysis
│   ├── media_fetcher.py       # Pexels media download
│   └── video_assembler.py     # MoviePy video creation
│
├── templates/
│   └── index.html             # Web UI
│
├── outputs/                   # Generated videos
├── temp/                      # Temporary files
│
├── requirements.txt           # Python dependencies
└── .env                       # API keys (user creates)
```

## Data Flow

```
User Selection → NewsAPI → Article Data
                              ↓
                         GROQ API
                              ↓
                    JSON Script Object
                    {script, scenes[]}
                              ↓
                        Gemini API
                              ↓
                 Enhanced Scene Data
                 {keywords, media_type}
                              ↓
                        Pexels API
                              ↓
                Downloaded Media Files
                 (images/videos)
                              ↓
        ┌────────────────────┴────────────────────┐
        ▼                                          ▼
    gTTS API                                  Media Files
   (Voiceover)                              (Images/Videos)
        │                                          │
        └────────────────────┬────────────────────┘
                             ▼
                        MoviePy Engine
                    (Composition & Rendering)
                             ▼
                     MP4 Video Output
                    (outputs/video_*.mp4)
```

## Module Responsibilities

### `news_scraper.py`
- **Purpose**: Fetch trending news articles
- **API**: NewsAPI
- **Returns**: Array of article objects with title, description, content, URL

### `script_generator.py`
- **Purpose**: Generate engaging video scripts
- **AI Model**: GROQ (openai/gpt-oss-120b)
- **Input**: Article metadata
- **Output**: JSON with script text and scene breakdowns

### `scene_analyzer.py`
- **Purpose**: Analyze scenes and suggest visuals
- **AI Model**: Google Gemini Pro
- **Input**: Script scenes with descriptions
- **Output**: Search keywords and media type per scene

### `media_fetcher.py`
- **Purpose**: Download relevant stock media
- **API**: Pexels
- **Input**: Scene keywords
- **Output**: Downloaded image/video files

### `video_assembler.py`
- **Purpose**: Composite final video
- **Library**: MoviePy
- **Input**: Media files, script, audio
- **Output**: MP4 video with overlays and transitions

## Technical Specifications

### Video Output
- **Resolution**: 1920x1080 (Full HD)
- **Frame Rate**: 24 fps
- **Codec**: H.264 (libx264)
- **Audio Codec**: AAC
- **Duration**: 30-60 seconds
- **Format**: MP4

### API Rate Limits (Free Tier)
- **NewsAPI**: 100 requests/day
- **GROQ**: Generous free tier
- **Gemini**: 60 requests/minute
- **Pexels**: 200 requests/hour
- **gTTS**: Unlimited

### Performance Metrics
- **Total Generation Time**: 60-120 seconds
- **Script Generation**: 5-10 seconds
- **Scene Analysis**: 10-15 seconds
- **Media Fetching**: 15-20 seconds
- **Video Assembly**: 20-30 seconds


import os
from groq import Groq
import json

def generate_script(article):
    """
    Generate a 30-60 second video script using GROQ API
    """
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        raise Exception("GROQ_API_KEY not found in environment variables")
    
    client = Groq(api_key=api_key)
    
    # Create prompt for script generation
    prompt = f"""
You are a professional video script writer. Create an engaging 30-60 second video script based on this news article:

Title: {article['title']}
Description: {article['description']}
Content: {article.get('content', '')}

Requirements:
1. Script should be exactly 30-60 seconds when read aloud (approximately 75-150 words)
2. Make it engaging and hook viewers in the first 3 seconds
3. Break the script into 3-4 scenes
4. Each scene should have a clear visual description
5. Use simple, conversational language
6. End with a compelling conclusion

Format your response as JSON:
{{
    "script_text": "Full script text here",
    "scenes": [
        {{
            "scene_number": 1,
            "duration": 10,
            "narration": "Text for this scene",
            "visual_description": "What should be shown on screen"
        }}
    ],
    "total_duration": 45
}}
"""
    
    try:
        # Available GROQ models (as of Dec 2024):
        # - llama-3.3-70b-versatile (recommended)
        # - llama-3.1-70b-versatile
        # - mixtral-8x7b-32768
        # - gemma2-9b-it
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Correct model name
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional video script writer who creates engaging, concise scripts for social media videos. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        
        script_data = json.loads(completion.choices[0].message.content)
        
        # Validate and fix script data if needed
        if not script_data.get('scenes'):
            raise Exception("No scenes generated in script")
        
        # Ensure scene numbers are set
        for i, scene in enumerate(script_data['scenes']):
            if 'scene_number' not in scene:
                scene['scene_number'] = i + 1
        
        return script_data
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse script JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to generate script: {str(e)}")
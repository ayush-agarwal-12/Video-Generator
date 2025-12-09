import os
import google.generativeai as genai

def analyze_scenes(script_data):
    """
    Analyze scenes and generate search keywords using Google Gemini
    """
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        raise Exception("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    scenes = script_data.get('scenes', [])
    
    enhanced_scenes = []
    
    for scene in scenes:
        prompt = f"""
Based on this video scene description, generate the best search keywords to find relevant stock footage or images:

Scene: {scene.get('visual_description', '')}
Narration: {scene.get('narration', '')}

Provide 3-5 specific search keywords that would find the most relevant visuals.
Also suggest the type of media needed (photo, video, graphic).

Format as JSON:
{{
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "media_type": "photo or video",
    "mood": "description of mood/tone"
}}
"""
        
        try:
            response = model.generate_content(prompt)
            
            # Parse JSON from response
            import json
            import re
            
            response_text = response.text
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                scene_analysis = json.loads(json_match.group())
            else:
                # Fallback if JSON parsing fails
                scene_analysis = {
                    "keywords": [scene.get('visual_description', 'news')[:30]],
                    "media_type": "photo",
                    "mood": "professional"
                }
            
            enhanced_scene = {
                **scene,
                "search_keywords": scene_analysis.get('keywords', []),
                "media_type": scene_analysis.get('media_type', 'photo'),
                "mood": scene_analysis.get('mood', 'neutral')
            }
            
            enhanced_scenes.append(enhanced_scene)
            
        except Exception as e:
            print(f"Warning: Failed to analyze scene {scene.get('scene_number')}: {str(e)}")
            # Fallback with basic keywords
            enhanced_scenes.append({
                **scene,
                "search_keywords": [scene.get('visual_description', 'news')[:30]],
                "media_type": "photo",
                "mood": "neutral"
            })
    
    return enhanced_scenes
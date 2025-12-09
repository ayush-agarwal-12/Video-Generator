import requests
import os
from urllib.request import urlretrieve
import time
from PIL import Image, ImageDraw, ImageFont

def create_fallback_image(text, scene_number, temp_folder):
    """
    Create a visually appealing fallback image when API fails
    """
    # Create gradient background
    colors = [
        ((41, 128, 185), (142, 68, 173)),   # Blue to Purple
        ((52, 152, 219), (46, 204, 113)),   # Blue to Green
        ((155, 89, 182), (52, 73, 94)),     # Purple to Dark
        ((230, 126, 34), (231, 76, 60)),    # Orange to Red
    ]
    
    color_pair = colors[scene_number % len(colors)]
    
    # Create image with gradient
    img = Image.new('RGB', (1280, 720))
    draw = ImageDraw.Draw(img)
    
    # Simple gradient
    for y in range(720):
        r = int(color_pair[0][0] + (color_pair[1][0] - color_pair[0][0]) * y / 720)
        g = int(color_pair[0][1] + (color_pair[1][1] - color_pair[0][1]) * y / 720)
        b = int(color_pair[0][2] + (color_pair[1][2] - color_pair[0][2]) * y / 720)
        draw.line([(0, y), (1280, y)], fill=(r, g, b))
    
    # Add text
    try:
        font_large = ImageFont.truetype("arial.ttf", 60)
        font_small = ImageFont.truetype("arial.ttf", 40)
    except:
        try:
            font_large = ImageFont.truetype("Arial.ttf", 60)
            font_small = ImageFont.truetype("Arial.ttf", 40)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # Scene number
    scene_text = f"Scene {scene_number + 1}"
    
    # Wrap text to multiple lines
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        try:
            bbox = draw.textbbox((0, 0), test_line, font=font_small)
            width = bbox[2] - bbox[0]
        except:
            width, _ = draw.textsize(test_line, font=font_small)
        
        if width > 1100:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw scene number
    try:
        bbox = draw.textbbox((0, 0), scene_text, font=font_large)
        text_width = bbox[2] - bbox[0]
    except:
        text_width, _ = draw.textsize(scene_text, font=font_large)
    
    draw.text(((1280 - text_width) // 2, 100), scene_text, fill='white', font=font_large)
    
    # Draw wrapped text
    y_offset = 300
    for line in lines[:3]:  # Max 3 lines
        try:
            bbox = draw.textbbox((0, 0), line, font=font_small)
            text_width = bbox[2] - bbox[0]
        except:
            text_width, _ = draw.textsize(line, font=font_small)
        
        draw.text(((1280 - text_width) // 2, y_offset), line, fill='white', font=font_small)
        y_offset += 60
    
    # Save image
    filename = f'{temp_folder}/fallback_scene_{scene_number}.jpg'
    img.save(filename, quality=85)
    return filename


def fetch_media(scenes):
    """
    Fetch media files from Pexels API based on scene keywords
    With robust fallback system
    """
    api_key = os.getenv('PEXELS_API_KEY')
    
    if not api_key:
        print("PEXELS_API_KEY not found in environment variables")
        print("Creating fallback images for all scenes...")
        return create_all_fallbacks(scenes)
    
    # Clean API key (remove any whitespace or quotes)
    api_key = api_key.strip().strip('"').strip("'")
    
    print(f"Using Pexels API key (length: {len(api_key)})")
    
    # Correct header format
    headers = {'Authorization': api_key}
    
    media_files = []
    temp_folder = 'temp'
    os.makedirs(temp_folder, exist_ok=True)
    
    # Test API connection first
    print("Testing Pexels API connection...")
    test_url = 'https://api.pexels.com/v1/search'
    test_params = {'query': 'technology', 'per_page': 1}
    
    try:
        test_response = requests.get(test_url, headers=headers, params=test_params, timeout=5)
        if test_response.status_code == 403:
            print("Pexels API returned 403 Forbidden - Invalid API key")
            print("Please check your API key at https://www.pexels.com/api/")
            print("Creating fallback images instead...")
            return create_all_fallbacks(scenes)
        elif test_response.status_code == 200:
            print("Pexels API connection successful")
        else:
            print(f"Unexpected status code: {test_response.status_code}")
    except Exception as e:
        print(f"API test failed: {e}")
        print("Creating fallback images...")
        return create_all_fallbacks(scenes)
    
    # Process each scene
    for idx, scene in enumerate(scenes):
        keywords = scene.get('search_keywords', ['news'])
        
        # Improve search query - use more generic terms if keywords are too long
        search_terms = []
        for keyword in keywords[:3]:
            # Clean up the keyword (remove partial text)
            if len(keyword) > 30:
                # Keyword seems truncated, use generic term
                continue
            search_terms.append(keyword)
        
        # Fallback to visual description if no good keywords
        if not search_terms:
            visual_desc = scene.get('visual_description', 'business news')
            # Extract first few words
            search_terms = visual_desc.split()[:3]
        
        search_query = ' '.join(search_terms)
        media_type = scene.get('media_type', 'photo')
        
        print(f"\nScene {idx}: Searching for '{search_query}' ({media_type})")
        
        # Add delay to avoid rate limiting
        if idx > 0:
            time.sleep(1.5)
        
        success = False
        
        try:
            # Try photo search (more reliable than video)
            url = 'https://api.pexels.com/v1/search'
            params = {
                'query': search_query,
                'per_page': 3,  # Get 3 results to have options
                'orientation': 'landscape'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('photos') and len(data['photos']) > 0:
                    # Try each photo until one downloads successfully
                    for photo_idx, photo in enumerate(data['photos'][:3]):
                        try:
                            image_url = photo['src'].get('large', photo['src']['medium'])
                            filename = f'{temp_folder}/scene_{idx}_image.jpg'
                            print(f"  Downloading image (attempt {photo_idx + 1})...")
                            
                            img_response = requests.get(image_url, headers={'User-Agent': 'Mozilla/5.0'})
                            with open(filename, 'wb') as f:
                                f.write(img_response.content)
                            
                            # Verify image was downloaded
                            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                                print(f"  Downloaded successfully")
                                media_files.append({
                                    'scene_number': scene.get('scene_number'),
                                    'path': filename,
                                    'type': 'image'
                                })
                                success = True
                                break
                        except Exception as download_error:
                            print(f"  Download attempt {photo_idx + 1} failed: {download_error}")
                            continue
                    
                    if not success:
                        print(f"  All download attempts failed")
                else:
                    print(f"  No photos found for query")
            else:
                print(f"  API returned status {response.status_code}")
                if response.status_code == 403:
                    print(f"  Response: {response.text}")
                    
        except Exception as e:
            print(f"  Error: {str(e)}")
        
        # Create fallback if download failed
        if not success:
            print(f"  Creating fallback image...")
            fallback_path = create_fallback_image(
                scene.get('visual_description', 'Scene'),
                idx,
                temp_folder
            )
            media_files.append({
                'scene_number': scene.get('scene_number'),
                'path': fallback_path,
                'type': 'image'
            })
    
    return media_files


def create_all_fallbacks(scenes):
    """
    Create fallback images for all scenes when API is unavailable
    """
    media_files = []
    temp_folder = 'temp'
    os.makedirs(temp_folder, exist_ok=True)
    
    for idx, scene in enumerate(scenes):
        fallback_path = create_fallback_image(
            scene.get('visual_description', f'Scene {idx + 1}'),
            idx,
            temp_folder
        )
        media_files.append({
            'scene_number': scene.get('scene_number'),
            'path': fallback_path,
            'type': 'image'
        })
    
    return media_files
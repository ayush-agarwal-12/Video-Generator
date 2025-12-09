import os
from moviepy.config import change_settings


IMAGEMAGICK_PATH = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

if os.path.exists(IMAGEMAGICK_PATH):
    change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_PATH})
else:
    print(f"⚠️ Warning: ImageMagick not found at {IMAGEMAGICK_PATH}. Text overlays might fail.")


from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np


import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS


from gtts import gTTS

def create_video(script_data, scenes, media_files, output_path):
    """
    Assemble the final video using MoviePy
    """
    clips = []
    temp_folder = 'temp'
    
    # Ensure temp folder exists
    os.makedirs(temp_folder, exist_ok=True)
    
    # Generate voiceover
    script_text = script_data.get('script_text', '')
    audio_path = f'{temp_folder}/voiceover.mp3'
    
    try:
        tts = gTTS(text=script_text, lang='en', slow=False)
        tts.save(audio_path)
    except Exception as e:
        print(f"Error generating TTS: {e}")
        return

    # Load audio to get duration
    try:
        audio_clip = AudioFileClip(audio_path)
        total_duration = audio_clip.duration
    except OSError:
        print("Error loading audio file.")
        return
    
    # Calculate duration per scene
    num_scenes = len(scenes)
    duration_per_scene = total_duration / num_scenes if num_scenes > 0 else 5
    
    # Target resolution (720p to save memory)
    # 1080p (1920x1080) requires 2x more RAM and often causes "Unable to allocate" errors
    TARGET_SIZE = (1280, 720)
    
    for idx, scene in enumerate(scenes):
        # Find corresponding media file
        media = next((m for m in media_files if m['scene_number'] == scene.get('scene_number')), None)
        
        img_clip = None
        
        if media and media['path'] and media['type'] in ['image', 'video']:
            if media['type'] == 'image':
                # Create clip from image
                img_clip = ImageClip(media['path']).set_duration(duration_per_scene)
                
                # Resize to cover 720p height
                img_clip = img_clip.resize(height=720) 
                img_clip = img_clip.margin(left=0, top=0, opacity=0).set_position("center")
                
                # Add zoom effect (Ken Burns)
                # Reduced zoom factor slightly to save processing time
                img_clip = img_clip.resize(lambda t: 1 + 0.02 * t / duration_per_scene)
                
            else:  # video
                video_clip = VideoFileClip(media['path'])
                
                # Resize video to standard height
                video_clip = video_clip.resize(height=720)
                
                # Loop or trim video to match scene duration
                if video_clip.duration < duration_per_scene:
                    video_clip = video_clip.loop(duration=duration_per_scene)
                else:
                    video_clip = video_clip.subclip(0, duration_per_scene)
                img_clip = video_clip
        else:
            # Create placeholder with text using PIL if no media found
            img_clip = create_text_clip(
                scene.get('narration', 'Scene ' + str(idx + 1)),
                duration_per_scene
            )
        
        # Ensure the clip is exactly the target size (centers it on black background if aspect ratio differs)
        img_clip = CompositeVideoClip([img_clip.set_position("center")], size=TARGET_SIZE)

        # Create Text Overlay (Captions)
        try:
            txt_clip = TextClip(
                scene.get('narration', '')[:100],  # Limit text length
                font='Arial',
                fontsize=40,  # Slightly smaller font for 720p
                color='white',
                stroke_color='black',
                stroke_width=2,
                size=(1100, None), # Wrap text (adjusted for 720p width)
                method='caption'
            ).set_duration(duration_per_scene).set_position(('center', 0.8), relative=True) # Position at bottom 80%
            
            # Composite video and text
            # We use 'use_bg_clip=True' to optimize composition
            composite = CompositeVideoClip([img_clip, txt_clip], size=TARGET_SIZE)
        except Exception as e:
            print(f"MoviePy TextClip error (likely font/imagemagick issue): {e}")
            composite = img_clip
            
        clips.append(composite)
    
    # Concatenate all clips
    try:
        # MEMORY FIX: Removed method='compose'. 
        # Default chaining uses much less RAM than composing everything at once.
        final_video = concatenate_videoclips(clips)
        
        # Add audio
        final_video = final_video.set_audio(audio_clip)
        
        # Write output
        final_video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=f'{temp_folder}/temp-audio.m4a',
            remove_temp=True,
            verbose=False,
            # threads=1 # Uncomment if memory errors persist (slower but safer)
        )
        
        print(f"Video created successfully: {output_path}")
        
    except Exception as e:
        print(f"Error assembling video: {e}")
    finally:
        # Cleanup
        try:
            audio_clip.close()
            final_video.close()
        except:
            pass

def create_text_clip(text, duration):
    """
    Create a simple colored background with text using PIL (Fallback if media fails)
    """
    # Create a colored background (Adjusted for 720p)
    img = Image.new('RGB', (1280, 720), color=(30, 30, 50))
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 50)
    except:
        font = ImageFont.load_default()
    
    # Add text (Basic centering)
    text_wrapped = text[:100]  # Limit text
    
    # Get text size
    try:
        bbox = draw.textbbox((0, 0), text_wrapped, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        # Older PIL versions
        text_width, text_height = draw.textsize(text_wrapped, font=font)
    
    position = ((1280 - text_width) // 2, (720 - text_height) // 2)
    draw.text(position, text_wrapped, fill='white', font=font)
    
    # Save temporary image
    temp_path = 'temp/placeholder.jpg'
    img.save(temp_path)
    
    return ImageClip(temp_path).set_duration(duration)
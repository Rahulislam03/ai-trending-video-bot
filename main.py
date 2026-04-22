import os
import asyncio
import requests
import random
import PIL.Image
import time
import google.generativeai as genai

# আধুনিক Pillow ভার্সনের জন্য ফিক্স
if not hasattr(PIL.Image, 'Resampling'):
    PIL.Image.Resampling = PIL.Image

from edge_tts import Communicate
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

# --- এপিআই কনফিগারেশন ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY missing in GitHub Secrets!")
else:
    genai.configure(api_key=GEMINI_API_KEY)

async def generate_viral_content():
    """Gemini এআই ট্রেন্ডিং স্টোরি ও সিনেমাটিক প্রম্পট বানাবে"""
    # মডেল নাম ফিক্স: অনেক সময় v1beta এ flash-001 বা শুধু flash কাজ ক
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    Identify a viral story for April 2026.
    1. Write a 50-60 second engaging video script in Bengali.
    2. Provide 6 high-quality cinematic image prompts in English.
    3. Suggest a Viral Title and Tags.
    Format:
    TITLE: [Title]
    TAGS: [Hashtags]
    STORY: [Bengali Script]
    PROMPTS:
    1. [Prompt 1] ... 6. [Prompt 6]
    """
    
    try:
        response = model.generate_content(prompt)
        content = response.text
        title = content.split("TITLE:")[1].split("TAGS:")[0].strip()
        tags = content.split("TAGS:")[1].split("STORY:")[0].strip()
        story = content.split("STORY:")[1].split("PROMPTS:")[0].strip()
        prompts_raw = content.split("PROMPTS:")[1].strip().split("\n")
        prompts = [p.split(".", 1)[1].strip() for p in prompts_raw if "." in p]
        return title, tags, story, prompts[:6] # ৬টি ছবি সেফ সাইড
    except Exception as e:
        print(f"⚠️ Gemini Error: {e}")
        return "Future Vision 2026", "#AI", "২০২৬ সালের নতুন জগত...", ["Futuristic city, 8k"]

async def create_voice(text):
    filename = "voice.mp3"
    communicate = Communicate(text, "bn-BD-PradeepNeural")
    await communicate.save(filename)
    return filename

def create_image(prompt, index):
    filename = f"img_{index}.jpg"
    seed = random.randint(1, 10**9)
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1080&height=1920&nologo=true&seed={seed}&model=flux"
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
            # মেমরি ফিক্সের জন্য ইমেজটি প্রি-প্রসেস করা
            with PIL.Image.open(filename) as img:
                img.convert("RGB").save(filename)
            return filename
    except: return None

def make_pro_max_video(image_paths, audio_path):
    output_path = "output/pro_max_video_2026.mp4"
    audio = AudioFileClip(audio_path)
    duration_per_img = audio.duration / len(image_paths)
    
    clips = []
    for i, img in enumerate(image_paths):
        # Resize লজিক পরিবর্তন করা হয়েছে Broken Pipe এরর এড়াতে
        clip = ImageClip(img).set_duration(duration_per_img).set_fps(30)
        
        # জুম ইফেক্টকে আরও স্থিতিশীল করা
        if i % 2 == 0:
            clip = clip.resize(lambda t: 1 + 0.04 * t)
        else:
            clip = clip.resize(lambda t: 1.1 - 0.04 * t)
        clips.append(clip.crossfadein(0.5))
    
    final_video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    
    # threads=1 এবং পিক্সেল ফরম্যাট ফিক্স যাতে FFMPEG ক্রাশ না করে
    final_video.write_videofile(
        output_path, 
        fps=30, 
        codec="libx264", 
        audio_codec="aac", 
        bitrate="5000k", # বিটরেট কিছুটা কমানো হয়েছে স্ট্যাবিলিটির জন্য
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        ffmpeg_params=["-pix_fmt", "yuv420p"]
    )
    return output_path

async def main():
    os.makedirs('output', exist_ok=True)
    title, tags, story, prompts = await generate_viral_content()
    voice_file = await create_voice(story)
    
    img_list = []
    for i, p in enumerate(prompts):
        img_path = create_image(p, i)
        if img_path: img_list.append(img_path)
    
    if img_list:
        make_pro_max_video(img_list, voice_file)
        print("🚀 ভিডিও তৈরি সম্পন্ন!")

if __name__ == "__main__":
    asyncio.run(main())
        

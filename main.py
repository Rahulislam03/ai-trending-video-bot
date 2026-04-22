import os
import asyncio
import requests
import random
import PIL.Image
import time
import google.generativeai as genai

# Pillow compatibility fix
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from edge_tts import Communicate
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

# --- এপিআই কনফিগারেশন (GitHub Secrets থেকে আসবে) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY missing in GitHub Secrets!")
else:
    genai.configure(api_key=GEMINI_API_KEY)

async def generate_viral_content():
    """Gemini এআই আজকের ট্রেন্ডিং টপিক নিয়ে ভিডিও স্ক্রিপ্ট ও প্রম্পট তৈরি করবে"""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    Identify a viral, emotional or technology-driven trending story for April 2026.
    1. Write a 50-60 second engaging video script in Bengali.
    2. Provide 8 high-quality cinematic image prompts in English (Flux-Pro style, 8k, realistic).
    3. Suggest a Viral Title and 5 Hashtags.
    
    Format:
    TITLE: [Title]
    TAGS: [Hashtags]
    STORY: [Bengali Script]
    PROMPTS:
    1. [Prompt 1] ... 8. [Prompt 8]
    """
    
    try:
        response = model.generate_content(prompt)
        content = response.text
        
        # ডাটা পার্সিং
        title = content.split("TITLE:")[1].split("TAGS:")[0].strip()
        tags = content.split("TAGS:")[1].split("STORY:")[0].strip()
        story = content.split("STORY:")[1].split("PROMPTS:")[0].strip()
        prompts_raw = content.split("PROMPTS:")[1].strip().split("\n")
        prompts = [p.split(".", 1)[1].strip() for p in prompts_raw if "." in p]
        
        return title, tags, story, prompts
    except Exception as e:
        print(f"⚠️ Gemini Error: {e}")
        # ফলব্যাক স্টোরি (যদি এপিআই কাজ না করে)
        return "Digital Bangladesh 2026", "#AI #Future", "২০২৬ সালের নতুন ডিজিটাল বাংলাদেশ আমাদের স্বপ্ন দেখাচ্ছে...", ["Futuristic city view, 8k, cinematic"]

async def create_voice(text):
    filename = "voice.mp3"
    # 'Pradeep' ভয়েসটি গম্ভীর এবং সিনেমাটিক ভিডিওর জন্য সেরা
    communicate = Communicate(text, "bn-BD-PradeepNeural")
    await communicate.save(filename)
    return filename

def create_image(prompt, index):
    filename = f"img_{index}.jpg"
    seed = random.randint(1, 10**9)
    # Flux-Pro স্টাইল হাই-কোয়ালিটি ইমেজ
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1080&height=1920&nologo=true&seed={seed}&model=flux&enhance=true"
    
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
            return filename
    except:
        return None

def make_pro_max_video(image_paths, audio_path):
    output_path = "output/viral_video_2026.mp4"
    audio = AudioFileClip(audio_path)
    duration_per_img = audio.duration / len(image_paths)
    
    clips = []
    for i, img in enumerate(image_paths):
        # প্রো-লেভেল সিনেমাটিক মোশন লজিক
        clip = ImageClip(img).set_duration(duration_per_img).crossfadein(0.5)
        
        # ডাইনামিক জুম (Ken Burns Effect)
        if i % 2 == 0:
            clip = clip.resize(lambda t: 1 + 0.07 * t) # Smooth Zoom In
        else:
            clip = clip.resize(lambda t: 1.2 - 0.07 * t) # Smooth Zoom Out
            
        clips.append(clip)
    
    final_video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    
    # হাই বিটরেট রেন্ডারিং (1080x1920 HD)
    final_video.write_videofile(
        output_path, 
        fps=30, 
        codec="libx264", 
        audio_codec="aac", 
        bitrate="8000k",
        threads=4,
        temp_audiofile='temp-audio.m4a',
        remove_temp=True
    )
    return output_path

async def main():
    os.makedirs('output', exist_ok=True)
    
    print("🧠 Gemini AI ট্রেন্ডিং আইডিয়া রিসার্চ করছে...")
    title, tags, story, prompts = await generate_viral_content()
    
    print(f"📌 টপিক: {title}")
    
    print("🎙️ প্রো-ভয়েসওভার তৈরি হচ্ছে...")
    voice_file = await create_voice(story)
    
    print("🎨 সিনেমাটিক ভিজ্যুয়াল জেনারেট হচ্ছে...")
    img_list = []
    for i, p in enumerate(prompts):
        img_path = create_image(p, i)
        if img_path:
            img_list.append(img_path)
    
    if img_list:
        print("🎬 ভিডিও প্রোডাকশন শুরু হচ্ছে (Pro Max Plus Engine)...")
        video_file = make_pro_max_video(img_list, voice_file)
        
        # মেটাডাটা ফাইল তৈরি (ইউটিউব/টিকটক আপলোডের জন্য)
        with open("output/metadata.txt", "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\nTags: {tags}\n\nStory:\n{story}")
            
        print(f"🔥 অভিনন্দন! ভিডিও তৈরি সম্পন্ন। ফাইলটি 'output' ফোল্ডারে আছে।")
    else:
        print("❌ ছবি তৈরিতে ব্যর্থ।")

if __name__ == "__main__":
    asyncio.run(main())

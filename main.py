import os
import asyncio
import requests
import random
import PIL.Image
import google.generativeai as genai
from edge_tts import Communicate
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

# Pillow Resampling Fix
if not hasattr(PIL.Image, 'LANCZOS'):
    PIL.Image.LANCZOS = PIL.Image.Resampling.LANCZOS

# --- API Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

async def generate_cartoon_story():
    """Gemini ২-৩টি চরিত্রের মজার কথোপকথন এবং ২ডি কার্টুন প্রম্পট বানাবে"""
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    prompt = """
    Create a funny 45-second Bengali conversation between 2 or 3 cartoon characters.
    Style: Minimalist 2D (like Stickman/Bangla Cartoon).
    Characters: Character A (Funny), Character B (Serious/Confused).
    
    Instructions:
    1. Write the script as a dialogue (e.g., A: [dialogue], B: [dialogue]).
    2. Provide 6 image prompts in English. 
       Crucially, each prompt must describe: "2D minimalist cartoon, two funny stickman-like characters with big eyes talking, thin black outlines, flat colors, white background, comic style."
    3. Suggest a Viral Title and Hashtags.
    
    Format:
    TITLE: [Title]
    TAGS: [Hashtags]
    STORY: [Bengali Dialogue Script]
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
        return title, tags, story, prompts[:6]
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return "Funny Talk", "#Cartoon", "চরিত্র ১: কিরে কি করিস? চরিত্র ২: এআই দিয়ে ভিডিও বানাই!", ["2D minimalist cartoon, two characters talking, white background"]

async def create_voice(text):
    filename = "voice.mp3"
    # সংলাপ থেকে নামগুলো বাদ দিয়ে শুধু কথাগুলো রেকর্ড করা
    clean_text = text.replace("Character A:", "").replace("Character B:", "").replace("চরিত্র ১:", "").replace("চরিত্র ২:", "")
    communicate = Communicate(clean_text, "bn-BD-PradeepNeural")
    await communicate.save(filename)
    return filename

def create_cartoon_image(prompt, index):
    filename = f"img_{index}.jpg"
    # Pollinations Flux Model for Clean 2D Look
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1080&height=1080&nologo=true&seed={random.randint(1,10**9)}&model=flux"
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
            # Resize and Clean
            with PIL.Image.open(filename) as img:
                img.convert("RGB").resize((1080, 1080)).save(filename)
            return filename
    except: return None

def make_cartoon_video(image_paths, audio_path):
    output_path = "output/funny_cartoon_2026.mp4"
    audio = AudioFileClip(audio_path)
    duration_per_img = audio.duration / len(image_paths)
    
    clips = []
    for img in image_paths:
        # কার্টুনের জন্য জুম ইফেক্ট ছাড়া ক্লিন কাট ভালো লাগে
        clip = ImageClip(img).set_duration(duration_per_img).set_fps(30)
        clips.append(clip)
    
    final_video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final_video.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac", bitrate="5000k")
    return output_path

async def main():
    os.makedirs('output', exist_ok=True)
    print("🎭 এআই কার্টুন স্টোরি ও সংলাপ তৈরি করছে...")
    title, tags, story, prompts = await generate_cartoon_story()
    
    print(f"🎙️ সংলাপ রেকর্ড হচ্ছে...")
    voice_file = await create_voice(story)
    
    print("🎨 ২ডি কার্টুন ক্যারেক্টার জেনারেট হচ্ছে...")
    img_list = []
    for i, p in enumerate(prompts):
        img_path = create_cartoon_image(p, i)
        if img_path: img_list.append(img_path)
    
    if img_list:
        print("🎬 কার্টুন ভিডিও রেন্ডার হচ্ছে...")
        make_cartoon_video(img_list, voice_file)
        print(f"✅ সম্পন্ন! টাইটেল: {title}")

if __name__ == "__main__":
    asyncio.run(main())

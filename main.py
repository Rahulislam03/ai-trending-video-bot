import os
import asyncio
import requests
import random
import PIL.Image
import time

if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from edge_tts import Communicate
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

def get_long_story():
    # ১ মিনিটের উপযোগী বড় গল্প এবং বেশি প্রম্পট
    stories = [
        {
            "text": """এক সময় এক সুন্দর পাহাড়ের পাদদেশে একটি ছোট্ট গ্রাম ছিল। সেই গ্রামে মিনু নামের একটি মেয়ে তার পোষা বিড়াল ছানার সাথে বাস করত। 
            একদিন তারা পাহাড়ের চূড়ায় একটি জাদুকরী ঝরনা খুঁজে পেল। সেই ঝরনার পানি ছিল নীল রঙের আর সেখান থেকে সুন্দর গান শোনা যেত। 
            মিনু যখন ঝরনার পানি স্পর্শ করল, হঠাৎ বনের সব ফুল কথা বলতে শুরু করল! প্রজাপতিরা নাচে মেতে উঠল। 
            মিনু বুঝতে পারল, প্রকৃতির সাথে বন্ধুত্ব করলে পৃথিবীটা কতই না সুন্দর হয়ে ওঠে। সে খুশিতে নেচে উঠল আর তার বিড়াল ছানাও মিউ মিউ করে গান গাইল।""",
            "prompts": [
                "cute girl with a small kitten in a beautiful village near mountains, 3d pixar style, vibrant, 8k",
                "girl and kitten walking towards a magical mountain, cartoon style, bright sunny day",
                "finding a magical blue waterfall in the forest, glowing water, 3d animation style, fantasy",
                "talking colorful flowers in a magical forest, whimsical atmosphere, pixar style",
                "cute girl dancing with butterflies in a flower garden, happy mood, vibrant colors",
                "girl and kitten sitting by the waterfall, sunset lighting, cinematic cartoon style"
            ]
        }
    ]
    return random.choice(stories)

async def create_voice(text, filename):
    # NabanitaNeutral এর ভয়েস বেশ স্পষ্ট এবং গল্পের জন্য ভালো
    communicate = Communicate(text, "bn-BD-NabanitaNeural")
    await communicate.save(filename)

def create_image(prompt, filename, retries=3):
    seed = random.randint(1, 999999)
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1080&height=1920&nologo=true&seed={seed}"
    
    for i in range(retries):
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(r.content)
                return True
        except Exception as e:
            print(f"⚠️ ইমেজ এরর: {e}, পুনরায় চেষ্টা চলছে...")
            time.sleep(5)
    return False

def make_video(image_paths, audio_path, output_path):
    print("🎬 ১ মিনিটের ভিডিও রেন্ডারিং শুরু হচ্ছে...")
    audio = AudioFileClip(audio_path)
    
    # অডিওর মোট দৈর্ঘ্যের ওপর ভিত্তি করে প্রতি ছবির সময় নির্ধারণ
    duration_per_img = audio.duration / len(image_paths)
    
    clips = []
    for img in image_paths:
        # একটু ধীরগতির জুম ইফেক্ট যাতে ভিডিও লম্বা হলেও স্মুথ থাকে
        clip = ImageClip(img).set_duration(duration_per_img).resize(lambda t: 1 + 0.05 * t)
        clips.append(clip)
    
    final_video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

async def main():
    os.makedirs('output', exist_ok=True)
    story_data = get_long_story()
    
    print("🔊 লং ভয়েসওভার তৈরি হচ্ছে...")
    await create_voice(story_data['text'], "voice.mp3")
    
    img_list = []
    print(f"🎨 {len(story_data['prompts'])}টি ছবি জেনারেট হচ্ছে...")
    for i, p in enumerate(story_data['prompts']):
        path = f"img_{i}.jpg"
        if create_image(p, path):
            img_list.append(path)
    
    if len(img_list) > 0:
        make_video(img_list, "voice.mp3", "output/final_video.mp4")
        print(f"🚀 ভিডিও তৈরি সম্পন্ন! দৈর্ঘ্য: {AudioFileClip('voice.mp3').duration:.2f} সেকেন্ড")
    else:
        print("❌ ছবি তৈরিতে ব্যর্থ।")

if __name__ == "__main__":
    asyncio.run(main())
    

import os
import asyncio
import requests
import random
import PIL.Image
import time

# Pillow ফিক্স
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from edge_tts import Communicate
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

def get_realistic_story():
    stories = [
        {
            "text": "ভবিষ্যতের এক ঢাকা শহর, যেখানে আকাশচুম্বী দালানের ফাঁক দিয়ে উড়ন্ত যান চলাচল করছে। রাস্তার ধারে রোবটরা মানুষের সাথে কেনাকাটা করছে। প্রযুক্তির এই চরম উৎকর্ষের মাঝেও একটি ছোট ছেলে পার্কে বসে একটি আসল গাছ লাগানোর চেষ্টা করছে। তার চোখে ছিল এক সুন্দর সবুজ পৃথিবীর স্বপ্ন।",
            "prompts": [
                "Hyper-realistic futuristic Dhaka city, neon lights, flying cars, cinematic 8k, photorealistic",
                "Advanced robots and humans interacting in a hi-tech marketplace, realistic textures, 8k",
                "Young boy planting a real tree in a futuristic metallic park, emotional lighting, hyper-detailed",
                "Cinematic sunset over a high-tech green city, nature and technology blending, 8k resolution"
            ]
        }
    ]
    return random.choice(stories)

# ভয়েস জেনারেশন (ভয়েস ফেইলর ফিক্স সহ)
async def create_voice(text, filename):
    # 'Bashkar' ফেইল করলে 'Pradeep' বা 'Nabanita' ব্যবহার করবে
    voices = ["bn-BD-BashkarNeural", "bn-BD-PradeepNeural", "bn-BD-NabanitaNeural"]
    
    for voice in voices:
        try:
            print(f"🎙️ {voice} ব্যবহার করে ভয়েস তৈরি করার চেষ্টা চলছে...")
            communicate = Communicate(text, voice)
            await communicate.save(filename)
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                print(f"✅ ভয়েস তৈরি সফল: {voice}")
                return True
        except Exception as e:
            print(f"⚠️ {voice} কাজ করেনি। পরবর্তী ভয়েস ট্রাই করা হচ্ছে...")
    return False

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
        except:
            time.sleep(5)
    return False

def make_advanced_video(image_paths, audio_path, output_path):
    print("🎬 ভিডিও রেন্ডারিং শুরু হচ্ছে...")
    audio = AudioFileClip(audio_path)
    duration_per_img = audio.duration / len(image_paths)
    
    clips = []
    for i, img in enumerate(image_paths):
        clip = ImageClip(img).set_duration(duration_per_img)
        # রিয়ালিস্টিক মোশন ডাইভার্সিটি
        if i % 2 == 0:
            clip = clip.resize(lambda t: 1 + 0.04 * t)
        else:
            clip = clip.resize(lambda t: 1.1 - 0.04 * t)
        clips.append(clip)
    
    final_video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

async def main():
    os.makedirs('output', exist_ok=True)
    story_data = get_realistic_story()
    
    # ভয়েস জেনারেশন
    voice_success = await create_voice(story_data['text'], "voice.mp3")
    
    if not voice_success:
        print("❌ কোনো ভয়েস ইঞ্জিন কাজ করছে না।")
        return

    img_list = []
    print(f"🎨 ছবি জেনারেট হচ্ছে...")
    for i, p in enumerate(story_data['prompts']):
        path = f"img_{i}.jpg"
        if create_image(p, path):
            img_list.append(path)
    
    if len(img_list) > 0:
        make_advanced_video(img_list, "voice.mp3", "output/final_video.mp4")
        print(f"🚀 ভিডিও তৈরি সম্পন্ন!")
    else:
        print("❌ ছবি তৈরিতে ব্যর্থ।")

if __name__ == "__main__":
    asyncio.run(main())
    

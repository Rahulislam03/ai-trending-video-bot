import os
import asyncio
import requests
import random
import PIL.Image
import time

# Pillow ভার্সন কনফ্লিক্ট ফিক্স
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from edge_tts import Communicate
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

def get_dynamic_story():
    stories = [
        {
            "text": "এক বনে একটি ছোট্ট লাল পাখি এবং তার বন্ধু নীল হাতি বাস করত। তারা প্রতিদিন একসাথে লুকোচুরি খেলত।",
            "prompts": [
                "cute red bird and blue elephant playing in colorful cartoon forest, 3d pixar style, vibrant, 8k",
                "cute elephant hiding behind a candy tree, cartoon style, bright colors, nursery background"
            ]
        },
        {
            "text": "একটি চালাক শিয়াল এক রাতে আঙ্গুর ফল খেতে বাগানে গেল। কিন্তু আঙ্গুরগুলো ছিল অনেক উঁচুতে।",
            "prompts": [
                "cute clever fox looking at grapes in a garden, cartoon style, 3d animation, bright lighting",
                "funny fox jumping to reach purple grapes, vibrant colors, nursery rhyme style, 8k"
            ]
        }
    ]
    return random.choice(stories)

async def create_voice(text, filename):
    communicate = Communicate(text, "bn-BD-NabanitaNeural")
    await communicate.save(filename)

# ইমেজ জেনারেশন (Retry লজিক সহ)
def create_image(prompt, filename, retries=3):
    seed = random.randint(1, 1000000)
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1080&height=1920&nologo=true&seed={seed}"
    
    for i in range(retries):
        try:
            print(f"🎨 ছবি তৈরি হচ্ছে (চেষ্টা {i+1})...")
            # টাইমআউট ৬০ সেকেন্ড করা হয়েছে
            r = requests.get(url, timeout=60) 
            if r.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(r.content)
                print(f"✅ ছবি সফলভাবে সেভ হয়েছে: {filename}")
                return True
        except Exception as e:
            print(f"⚠️ চেষ্টা {i+1} ব্যর্থ হয়েছে: {e}")
            time.sleep(5) # ৫ সেকেন্ড অপেক্ষা করে আবার চেষ্টা করবে
    return False

def make_video(image_paths, audio_path, output_path):
    print("🎬 ভিডিও রেন্ডারিং শুরু হচ্ছে...")
    audio = AudioFileClip(audio_path)
    duration_per_img = audio.duration / len(image_paths)
    
    clips = []
    for img in image_paths:
        clip = ImageClip(img).set_duration(duration_per_img).resize(lambda t: 1 + 0.04 * t)
        clips.append(clip)
    
    final_video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

async def main():
    os.makedirs('output', exist_ok=True)
    story_data = get_dynamic_story()
    text = story_data['text']
    prompts = story_data['prompts']
    
    print(f"📖 আজকের গল্প: {text[:40]}...")
    await create_voice(text, "voice.mp3")
    
    img_list = []
    for i, p in enumerate(prompts):
        path = f"img_{i}.jpg"
        if create_image(p, path):
            img_list.append(path)
    
    if len(img_list) > 0:
        make_video(img_list, "voice.mp3", "output/final_video.mp4")
        print("🚀 ভিডিও তৈরি সম্পন্ন!")
    else:
        print("❌ কোনো ছবি জেনারেট করা সম্ভব হয়নি।")

if __name__ == "__main__":
    asyncio.run(main())
            

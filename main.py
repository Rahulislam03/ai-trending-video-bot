import os
import asyncio
import requests
import random
import PIL.Image

# Pillow ভার্সন কনফ্লিক্ট ফিক্স
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from edge_tts import Communicate
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, TextClip, CompositeVideoClip

# ১. আলাদা আলাদা গল্পের ডাটাবেস (এখান থেকে প্রতিবার র‍্যান্ডমলি একটি বেছে নেবে)
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
        },
        {
            "text": "একটি ছোট বিড়াল ছানা একটি রঙিন প্রজাপতির পিছু পিছু ছুটছিল। শেষ পর্যন্ত তারা খুব ভালো বন্ধু হয়ে গেল।",
            "prompts": [
                "cute small kitten chasing a colorful butterfly in a flower garden, pixar style, 3d render",
                "kitten and butterfly sitting on a flower together, happy mood, bright cartoon colors"
            ]
        }
    ]
    return random.choice(stories)

# ২. ভয়েসওভার তৈরি (বাংলা)
async def create_voice(text, filename):
    communicate = Communicate(text, "bn-BD-NabanitaNeural") # মেয়েলি কণ্ঠ বাচ্চাদের জন্য ভালো
    await communicate.save(filename)

# ৩. টেক্সট টু ইমেজ
def create_image(prompt, filename):
    # প্রতিবার আলাদা ছবি পেতে র‍্যান্ডম সীড (Seed) ব্যবহার
    seed = random.randint(1, 1000000)
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1080&height=1920&nologo=true&seed={seed}"
    r = requests.get(url, timeout=30)
    with open(filename, 'wb') as f:
        f.write(r.content)

# ৪. ভিডিও রেন্ডারিং (অ্যাডভান্সড মোশন ও সাবটাইটেল)
def make_video(image_paths, audio_path, story_text, output_path):
    audio = AudioFileClip(audio_path)
    duration_per_img = audio.duration / len(image_paths)
    
    clips = []
    for img in image_paths:
        # ৪% জুম-ইন মোশন
        clip = ImageClip(img).set_duration(duration_per_img).resize(lambda t: 1 + 0.04 * t)
        clips.append(clip)
    
    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio)
    
    # লিনাক্স সার্ভারে সাপোর্টের জন্য আউটপুট
    video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

async def main():
    os.makedirs('output', exist_ok=True)
    
    # প্রতিবার আলাদা গল্প নেওয়া
    story_data = get_dynamic_story()
    text = story_data['text']
    prompts = story_data['prompts']
    
    print(f"📖 আজকের গল্প: {text[:30]}...")
    
    await create_voice(text, "voice.mp3")
    
    img_list = []
    for i, p in enumerate(prompts):
        path = f"img_{i}.jpg"
        create_image(p, path)
        img_list.append(path)
    
    make_video(img_list, "voice.mp3", text, "output/final_video.mp4")
    print("🚀 ভিডিও তৈরি সম্পন্ন!")

if __name__ == "__main__":
    asyncio.run(main())
    

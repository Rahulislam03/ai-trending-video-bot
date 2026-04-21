import os
import asyncio
import requests
import PIL.Image

# Pillow ভার্সন কনফ্লিক্ট ফিক্স
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from edge_tts import Communicate
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

# ১. ট্রেন্ডিং স্টোরি ও ইমেজ প্রম্পট (এখানে নিজের পছন্দমতো পরিবর্তন করতে পারবে)
def get_story():
    story_text = "২০২৬ সালে কৃত্রিম বুদ্ধিমত্তা আমাদের জীবনকে বদলে দিচ্ছে। মানুষ এবং রোবট এখন কাঁধে কাঁধ মিলিয়ে কাজ করছে প্রযুক্তির এক নতুন যুগে।"
    
    # ছবির জন্য প্রম্পট (প্রতিটি সিনের জন্য আলাদা)
    image_prompts = [
        "futuristic city in 2026 with robots and humans walking together, cinematic lighting, 8k, anime style",
        "human hands shaking with a robotic hand, high tech laboratory background, detailed texture, realistic"
    ]
    return story_text, image_prompts

# ২. ভয়েসওভার তৈরি (বাংলা)
async def create_voice(text, filename):
    communicate = Communicate(text, "bn-BD-PradeepNeural")
    await communicate.save(filename)

# ৩. টেক্সট টু ইমেজ (Pollinations AI)
def create_image(prompt, filename):
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1080&height=1920&nologo=true&seed=123"
    try:
        r = requests.get(url, timeout=30)
        with open(filename, 'wb') as f:
            f.write(r.content)
        print(f"✅ ইমেজ তৈরি হয়েছে: {filename}")
    except Exception as e:
        print(f"❌ ইমেজ তৈরিতে সমস্যা: {e}")

# ৪. ভিডিও রেন্ডারিং (অ্যাডভান্সড মোশন ইফেক্টসহ)
def make_video(image_paths, audio_path, output_path):
    print("🎬 ভিডিও রেন্ডারিং শুরু হচ্ছে...")
    audio = AudioFileClip(audio_path)
    duration_per_img = audio.duration / len(image_paths)
    
    clips = []
    for img in image_paths:
        # প্রতিটি ইমেজে ২% জুম-ইন ইফেক্ট যোগ করা হয়েছে
        clip = ImageClip(img).set_duration(duration_per_img).resize(lambda t: 1 + 0.02 * t)
        clips.append(clip)
    
    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.set_audio(audio)
    
    # লিনাক্স সার্ভারে সাপোর্টের জন্য নির্দিষ্ট কোডেক ব্যবহার
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

# ৫. মেইন ফাংশন
async def main():
    # ফোল্ডার তৈরি
    os.makedirs('output', exist_ok=True)
    
    # ডেটা সংগ্রহ
    text, prompts = get_story()
    
    # অডিও তৈরি
    print("🔊 ভয়েস তৈরি হচ্ছে...")
    await create_voice(text, "voice.mp3")
    
    # ছবি তৈরি
    img_list = []
    print("🎨 ছবি জেনারেট হচ্ছে...")
    for i, p in enumerate(prompts):
        path = f"img_{i}.jpg"
        create_image(p, path)
        img_list.append(path)
    
    # ভিডিও তৈরি
    if os.path.exists("voice.mp3") and len(img_list) > 0:
        make_video(img_list, "voice.mp3", "output/final_video.mp4")
        print(f"🚀 অভিনন্দন! ভিডিও তৈরি হয়েছে: output/final_video.mp4")
    else:
        print("❌ অডিও বা ইমেজ ফাইল খুঁজে পাওয়া যায়নি!")

if __name__ == "__main__":
    asyncio.run(main())
                  

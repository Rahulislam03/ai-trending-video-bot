import os
import time
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip

# --- কনফিগারেশন ---
CHARACTER_DIR = "Characters"
OUTPUT_DIR = "output_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ক্যারেক্টার লিস্ট (আপনার আপলোড করা ফাইলের নামের সাথে মিলিয়ে নিন)
CHARACTERS = {
    "hashem": os.path.join(CHARACTER_DIR, "hashem.png"),
    "kasem": os.path.join(CHARACTER_DIR, "kasem.png"),
    "kuddus": os.path.join(CHARACTER_DIR, "kuddus.png")
}

class AIVideoBot:
    def __init__(self):
        print("🤖 AI Trending Video Bot স্টার্ট হচ্ছে...")

    def generate_audio(self, text, filename):
        """টেক্সট থেকে বাংলা ভয়েস তৈরি করে"""
        tts = gTTS(text=text, lang='bn')
        audio_path = os.path.join(OUTPUT_DIR, f"{filename}.mp3")
        tts.save(audio_path)
        return audio_path

    def create_video(self, char_name, script_text, output_name):
        """ছবি এবং অডিও মিলিয়ে ভিডিও তৈরি করে"""
        if char_name not in CHARACTERS or not os.path.exists(CHARACTERS[char_name]):
            print(f"❌ এরর: {char_name} এর ছবি Characters ফোল্ডারে পাওয়া যায়নি!")
            return

        print(f"🎬 {char_name} এর জন্য ভিডিও তৈরি হচ্ছে...")
        
        # ১. অডিও তৈরি
        audio_path = self.generate_audio(script_text, output_name)
        audio_clip = AudioFileClip(audio_path)

        # ২. ভিডিও ক্লিপ তৈরি (অডিওর দৈর্ঘ্য অনুযায়ী)
        img_clip = ImageClip(CHARACTERS[char_name]).set_duration(audio_clip.duration)
        video = img_clip.set_audio(audio_clip)

        # ৩. সেভ করা
        final_output = os.path.join(OUTPUT_DIR, f"{output_name}.mp4")
        video.write_videofile(final_output, fps=24, codec="libx264")
        print(f"✅ ভিডিও রেডি: {final_output}")

# --- মেইন প্রোগ্রাম ---
if __name__ == "__main__":
    bot = AIVideoBot()

    # আপনার গল্পের স্ক্রিপ্ট এখানে লিখুন
    story_script = [
        {"char": "hashem", "text": "কিরে কাশেম, তোর নাকি নতুন চশমা খুব ট্রেন্ডিং এ আছে?"},
        {"char": "kasem", "text": "আরে হাসেম ভাই, এই চশমা পরলে নাকি এ আই ভিডিও ভাইরাল হয়!"}
    ]

    # প্রতিটি লাইনের জন্য আলাদা ভিডিও তৈরি (পরে আপনি চাইলে সব জোড়া দিতে পারেন)
    for i, line in enumerate(story_script):
        bot.create_video(line["char"], line["text"], f"scene_{i}")

    print("\n🚀 সব ভিডিও তৈরি শেষ! output_videos ফোল্ডার চেক করুন।")
    

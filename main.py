import os
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip

# --- সঠিক কনফিগারেশন (আপনার স্ক্রিনশট অনুযায়ী) ---
CHARACTER_DIR = "characters"  # ছোট হাতের অক্ষরে
OUTPUT_DIR = "output_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ক্যারেক্টার লিস্ট (আপনার ফাইলের সঠিক বানান অনুযায়ী)
CHARACTERS = {
    "hasem": os.path.join(CHARACTER_DIR, "hasem.png"),
    "kasem": os.path.join(CHARACTER_DIR, "kasem.png"),
    "mojnu": os.path.join(CHARACTER_DIR, "mojnu.png")
}

class AIVideoBot:
    def __init__(self):
        print("🤖 AI Trending Video Bot স্টার্ট হচ্ছে...")

    def generate_audio(self, text, filename):
        tts = gTTS(text=text, lang='bn')
        audio_path = os.path.join(OUTPUT_DIR, f"{filename}.mp3")
        tts.save(audio_path)
        return audio_path

    def create_video(self, char_name, script_text, output_name):
        # বানান এবং পাথ চেক
        char_path = CHARACTERS.get(char_name)
        if not char_path or not os.path.exists(char_path):
            print(f"❌ এরর: {char_name} এর ছবি '{char_path}' পাথে পাওয়া যায়নি!")
            return

        print(f"🎬 {char_name} এর জন্য ভিডিও তৈরি হচ্ছে...")
        audio_path = self.generate_audio(script_text, output_name)
        audio_clip = AudioFileClip(audio_path)

        img_clip = ImageClip(char_path).set_duration(audio_clip.duration)
        video = img_clip.set_audio(audio_clip)

        final_output = os.path.join(OUTPUT_DIR, f"{output_name}.mp4")
        video.write_videofile(final_output, fps=24, codec="libx264")
        print(f"✅ ভিডিও রেডি: {final_output}")

if __name__ == "__main__":
    bot = AIVideoBot()

    # আপনার স্ক্রিপ্ট (ক্যারেক্টারের নামের বানান ঠিক রাখবেন)
    story_script = [
        {"char": "hasem", "text": "কিরে কাসেম, আমাদের নতুন এ আই ভিডিও বট কেমন কাজ করছে?"},
        {"char": "kasem", "text": "অসাম হাসেম ভাই! এখন মজনুও আমাদের সাথে ভিডিওতে আছে।"},
        {"char": "mojnu", "text": "আমিও রেডি ভাই, ফাটিয়ে দেব এবার!"}
    ]

    for i, line in enumerate(story_script):
        bot.create_video(line["char"], line["text"], f"scene_{i}")

    print("\n🚀 সব ভিডিও তৈরি শেষ! output_videos ফোল্ডার চেক করুন।")
        

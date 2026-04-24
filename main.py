import os
import asyncio
import requests
import random
import PIL.Image
import google.generativeai as genai
from edge_tts import Communicate
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

# Pillow compatibility fix
if not hasattr(PIL.Image, 'LANCZOS'):
    PIL.Image.LANCZOS = PIL.Image.Resampling.LANCZOS

# --- API Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ==========================================
# --- স্থায়ী চরিত্রদের প্রোফাইল (The Squad) ---
# ==========================================
CHARACTERS_INFO = """
1. Hashem (হাশেম): Short, fat, round face, small tuft of hair, wearing lungi and punjabi.
2. Kasem (কাশেম): Very tall and skinny, wearing big round glasses and a red t-shirt.
3. Montu (মন্টু): Kid-like short character, wearing a bright yellow t-shirt, messy hair.
4. Kuddus (কুদ্দুস): Elderly man with a white beard, wearing a skullcap (topi), holding a walking stick.
"""

VISUAL_STYLE = "Minimalist 2D cartoon, simple stickman-like characters, thin black outlines, flat colors, white background, funny Bengali aesthetics."

async def generate_cartoon_content():
    """Gemini এখন স্থায়ী চরিত্রদের নিয়ে গল্প ও প্রম্পট বানাবে"""
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    prompt = f"""
    Characters List:
    {CHARACTERS_INFO}
    
    Task:
    1. Create a 45-second funny Bengali comedy script using any 2 or 3 characters from the list above.
    2. The script should be a dialogue: (e.g. হাশেম: [কথা], কাশেম: [কথা]).
    3. Provide 6 image prompts in English. 
       Each prompt MUST describe the characters exactly as defined above in a "{VISUAL_STYLE}" setting.
    4. Suggest a Viral Title and 5 Hashtags.
    
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
        return title, tags, story, prompts[:6]
    except Exception as e:
        print(f"⚠️ Gemini Error: {e}")
        return "Bangla Comedy", "#Funny", "হাশেম: কিরে কাশেম, তুই কি করিস? কাশেম: ভাই এআই দিয়ে কার্টুন বানাই!", ["2D minimalist funny characters, white background"]

async def create_voice(text):
    filename = "voice.mp3"
    # সংলাপ থেকে নামগুলো বাদ দিয়ে পরিষ্কার টেক্সট তৈরি
    clean_text = text.replace("হাশেম:", "").replace("কাশেম:", "").replace("মন্টু:", "").replace("কুদ্দুস:", "")
    communicate = Communicate(clean_text, "bn-BD-PradeepNeural")
    await communicate.save(filename)
    return filename

def create_image(prompt, index):
    filename = f"img_{index}.jpg"
    # Pollinations Flux Model for Clean 2D Look
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1080&height=1080&nologo=true&seed={random.randint(1,10**9)}&model=flux"
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
            with PIL.Image.open(filename) as img:
                img.convert("RGB").resize((1080, 1080)).save(filename)
            return filename
    except: return None

def make_video(image_paths, audio_path):
    output_path = "output/bangla_cartoon_final.mp4"
    audio = AudioFileClip(audio_path)
    duration_per_img = audio.duration / len(image_paths)
    
    clips = []
    for img in image_paths:
        clip = ImageClip(img).set_duration(duration_per_img).set_fps(30)
        clips.append(clip)
    
    final_video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final_video.write_videofile(
        output_path, 
        fps=30, 
        codec="libx264", 
        audio_codec="aac", 
        bitrate="5000k",
        ffmpeg_params=["-pix_fmt", "yuv420p"]
    )
    return output_path

async def main():
    os.makedirs('output', exist_ok=True)
    print("🎭 হাশেম-কাশেমের নতুন গল্প তৈরি হচ্ছে...")
    title, tags, story, prompts = await generate_cartoon_content()
    
    print("🎙️ ভয়েসওভার রেকর্ড হচ্ছে...")
    voice_file = await create_voice(story)
    
    print("🎨 ২ডি ক্যারেক্টার জেনারেট হচ্ছে...")
    img_list = []
    for i, p in enumerate(prompts):
        img_path = create_image(p, i)
        if img_path: img_list.append(img_path)
    
    if img_list:
        print("🎬 ভিডিও রেন্ডার হচ্ছে...")
        make_video(img_list, voice_file)
        with open("output/metadata.txt", "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\nTags: {tags}\n\nStory:\n{story}")
        print(f"✅ সম্পন্ন! টাইটেল: {title}")

if __name__ == "__main__":
    asyncio.run(main())
    

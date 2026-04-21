import os
import asyncio
import requests
from edge_tts import Communicate
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

# ১. ট্রেন্ডিং স্ক্রিপ্ট (এখানে ডামি দেওয়া, জেমিনি এপিআই দিয়ে অটো করা যায়)
def get_story():
    story = "২০২৬ সালে রোবটরা আমাদের দৈনন্দিন কাজে সাহায্য করছে। এটি প্রযুক্তির এক নতুন যুগ।"
    prompts = ["futuristic robot helping human in kitchen anime style", "high tech city 2026 cinematic"]
    return story, prompts

# ২. ভয়েস জেনারেশন
async def create_voice(text, filename):
    communicate = Communicate(text, "bn-BD-PradeepNeural")
    await communicate.save(filename)

# ৩. টেক্সট টু ইমেজ
def create_image(prompt, filename):
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1080&height=1920&nologo=true"
    r = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(r.content)

# ৪. ইমেজ টু ভিডিও (উইথ মোশন)
def make_video(images, audio_path, output_path):
    audio = AudioFileClip(audio_path)
    dur = audio.duration / len(images)
    clips = [ImageClip(img).set_duration(dur).resize(lambda t: 1 + 0.02 * t) for img in images]
    video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

async def main():
    os.makedirs('output', exist_ok=True)
    text, prompts = get_story()
    await create_voice(text, "voice.mp3")
    img_list = []
    for i, p in enumerate(prompts):
        path = f"img_{i}.jpg"
        create_image(p, path)
        img_list.append(path)
    make_video(img_list, "voice.mp3", "output/final_video.mp4")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

# Paths to our files
title_img = "goldenhar_title.jpg"
symptoms_img = "goldenhar_symptoms.jpg"
hope_img = "goldenhar_hope.jpg"
audio_file = "goldenhar_voice.mp3"
output_file = "goldenhar_reel.mp4"

# Create image clips (10 seconds each)
title_clip = ImageClip(title_img).with_duration(10)
symptoms_clip = ImageClip(symptoms_img).with_duration(10)
hope_clip = ImageClip(hope_img).with_duration(10)

# Resize all clips to 1080x1920 (Instagram Reels format)
title_clip = title_clip.resized((1080, 1920))
symptoms_clip = symptoms_clip.resized((1080, 1920))
hope_clip = hope_clip.resized((1080, 1920))

# Concatenate the clips
final_clip = concatenate_videoclips([title_clip, symptoms_clip, hope_clip])

# Add audio
audio_clip = AudioFileClip(audio_file)
final_clip = final_clip.with_audio(audio_clip)

# Trim to exactly 30 seconds
final_clip = final_clip.subclipped(0, 30)

# Write the result
final_clip.write_videofile(
    output_file,
    fps=24,
    codec="libx264",
    audio_codec="aac",
    bitrate="5000k",
    threads=4,
    preset="ultrafast"
)

print(f"Reel created successfully: {output_file}")

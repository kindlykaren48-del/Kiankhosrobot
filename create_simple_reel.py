#!/usr/bin/env python3
import sys
sys.path.insert(0, '/usr/local/lib/python3.11/dist-packages')

from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

# Create simple test clips
title_clip = ImageClip("goldenhar_title.jpg").with_duration(10)
symptoms_clip = ImageClip("goldenhar_symptoms.jpg").with_duration(10)
hope_clip = ImageClip("goldenhar_hope.jpg").with_duration(10)

# Resize
title_clip = title_clip.resized((1080, 1920))
symptoms_clip = symptoms_clip.resized((1080, 1920))
hope_clip = hope_clip.resized((1080, 1920))

# Concatenate
final_clip = concatenate_videoclips([title_clip, symptoms_clip, hope_clip])

# Add audio
audio_clip = AudioFileClip("goldenhar_voice.mp3")
final_clip = final_clip.with_audio(audio_clip)

# Trim to 30 seconds
final_clip = final_clip.subclipped(0, 30)

# Write with better settings
final_clip.write_videofile(
    "goldenhar_reel_final.mp4",
    fps=24,
    codec="libx264",
    audio_codec="aac",
    bitrate="8000k",
    threads=4,
    preset="ultrafast",
    logger=None
)

print("Video created successfully!")

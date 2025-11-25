# importing required libraries
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume


def merge_complex_audio():

    # File Configurations
    VIDEO_FILE = "final_submission_alive_prominent.mp4"
    BG_AUDIO_FILE = "background_sound.mp3" 
    WHISPER_FILE = "cropped_audio.mp3"     
    OUTPUT_FILE = "Final_Level2_Complex_Audio.mp4"
    
    # Timing & Mixing
    WHISPER_START_TIME = 1.0 
    BG_VOLUME = 0.5           
    
    # Check files
    for f in [VIDEO_FILE, BG_AUDIO_FILE, WHISPER_FILE]:
        if not os.path.exists(f):
            print(f"Error: Missing file: {f}")
            return

    print("Loading assets...")
    video_clip = VideoFileClip(VIDEO_FILE)
    bg_clip = AudioFileClip(BG_AUDIO_FILE)
    whisper_clip = AudioFileClip(WHISPER_FILE)

    print(f"Video Duration: {video_clip.duration}s")


    # Trim it to match the video length
    if hasattr(bg_clip, 'with_duration'): # MoviePy 2.0
        bg_clip = bg_clip.with_duration(video_clip.duration)
    else:
        bg_clip = bg_clip.set_duration(video_clip.duration)

    
    # (This try/except handles different MoviePy versions of volume control)
    try:
        if hasattr(bg_clip, 'with_effects'):
            bg_clip = bg_clip.with_effects([MultiplyVolume(BG_VOLUME)])
        else:
            bg_clip = bg_clip.volumex(BG_VOLUME)
    except Exception as e:
        print(f"⚠️ Could not adjust volume (ignoring): {e}")

    
    # Delay the start to 1.0 seconds
    if hasattr(whisper_clip, 'with_start'): # MoviePy 2.0
        whisper_positioned = whisper_clip.with_start(WHISPER_START_TIME)
    else:
        whisper_positioned = whisper_clip.set_start(WHISPER_START_TIME)

    
    # CompositeAudioClip layers them on top of each other
    final_mixed_audio = CompositeAudioClip([bg_clip, whisper_positioned])

    # Attach to Video
    if hasattr(video_clip, 'with_audio'): 
        final_video = video_clip.with_audio(final_mixed_audio)
    else:
        final_video = video_clip.set_audio(final_mixed_audio)

    # Save
    print("Rendering final complex composite...")
    final_video.write_videofile(OUTPUT_FILE, codec='libx264', audio_codec='aac')
    
    print(f"SUCCESS! Final video saved as: {OUTPUT_FILE}")

if __name__ == "__main__":
    merge_complex_audio()
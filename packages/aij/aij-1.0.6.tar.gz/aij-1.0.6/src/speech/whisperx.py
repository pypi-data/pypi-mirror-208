import os
from pathlib import Path
import whisper

# find all the videos in the data directory using the glob module
videos = [str(video) for video in Path('data').glob('*.mp4')]

print(
    f"Found {len(videos)} videos:"
)

# load the model
model = whisper.load_model('base.en')

# transcribe each video
for video in videos:
    #  ffmpeg data conversion from mp4 to wav
    audio = video.replace('.mp4', '.wav')
    if not os.path.exists(audio):
        os.system(f"ffmpeg -i {video} -vn -acodec pcm_s16le -ar 16000 -ac 1 {video.replace('.mp4', '.wav')}")
   
    result = whisper.transcribe(model, audio)
    print(f"Transcription for {audio}:")
   
    # print to a file with the same name as the audio (wav) but with a .txt extension
    with open(audio.replace('.wav', '.txt'), 'w', encoding="utf-8") as f:
        f.write(result['text'])

print(
    result['text']
)
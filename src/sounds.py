import simpleaudio as sa
from pathlib import Path

def ding():
    song = sa.WaveObject.from_wave_file(str(Path("sounds/ding.wav")))
    play_object = song.play()
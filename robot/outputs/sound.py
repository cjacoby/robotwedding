import asyncio
import logging
import numpy as np
import pathlib
import pygame
import subprocess
import tempfile
import uuid

logger = logging.getLogger(__name__)

RESOURCES = pathlib.Path(__file__).resolve().parent.parent.parent / "resources"
wav_files = [RESOURCES / "dt01_stab_britelite_16.wav"]


def speak(text):
    """Sends text to the speaker"""
    subprocess.run(["flite", "-t", text])


def speech_to_wav(text, output_file):
    try:
        subprocess.run(["flite", "-t", text, "-o", output_file])
    except FileNotFoundError:
        logger.error("No flite to run")
    return pathlib.Path(output_file).exists()


class SoundResource(object):
    def __init__(self):
        self.speech_dir = tempfile.TemporaryDirectory()
        self.speech_map = dict()
        self.sr = 44010

    def setup(self):
        pygame.mixer.pre_init(self.sr, -16, 1)
        pygame.mixer.init()

    def play_speech(self, text):
        if text in self.speech_map:
            output_path = self.speech_map[hash(text)]
        else:
            filename = f"{str(uuid.uuid4()).replace('-', '')}.wav"
            output_path = pathlib.Path(self.speech_dir.name) / filename

            speech_to_wav(text, output_path)
            self.speech_map[hash(text)] = output_path

        self.play_file(output_path)

    async def aplay_speech(self, text):
        if text in self.speech_map:
            output_path = self.speech_map[hash(text)]
        else:
            filename = f"{str(uuid.uuid4()).replace('-', '')}.wav"
            output_path = pathlib.Path(self.speech_dir.name) / filename

            speech_to_wav(text, output_path)
            self.speech_map[hash(text)] = output_path

        await self.aplay_file(output_path)

    def play_init_sound(self):
        # if wav_files[0].exists():
            # pygame.mixer.music.load(str(wav_files[0]))
            # pygame.mixer.music.play()

            # # milliseconds wait for each sound to finish
            # pygame.time.wait(500)

        # else:
        #     logger.info("failed to play; file does not exist")
        self.play_file(wav_files[0])

    async def aplay_init_sound(self):
        await self.aplay_file(wav_files[0])

    def play_file(self, path):
        if path.exists():
            sound = pygame.mixer.Sound(str(path))
            duration = sound.get_length()
            sound.play()
            pygame.time.wait(int(duration * 1000))

        else:
            logger.info("failed to play; file does not exist")

    async def aplay_file(self, path):
        if path.exists():
            sound = pygame.mixer.Sound(str(path))
            duration = sound.get_length()
            sound.play()
            await asyncio.sleep(duration)

        else:
            logger.info("failed to play; file does not exist")

    def play_sin(self, freq=440, dur=1):
        arr = np.array([
            4096 * np.sin(2.0 * np.pi * freq * x / self.sr)
            for x in range(0, self.sr)]).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        sound.play()
        pygame.time.delay(dur * 1000)
        sound.stop()

    async def aplay_sin(self, freq=440, dur=1):
        arr = np.array([
            4096 * np.sin(2.0 * np.pi * freq * x / self.sr)
            for x in range(0, self.sr)]).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        sound.play()
        await asyncio.sleep(dur)
        sound.stop()

    def play_noise(self):
        arr = np.array([
            4096 * np.random.random()
            for x in range(0, self.sr)]).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        sound.play()
        pygame.time.delay(1000)
        sound.stop()

    async def aplay_noise(self, ):
        """play noise with async wait"""
        arr = np.array([
            4096 * np.random.random()
            for x in range(0, self.sr)]).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        sound.play()
        await asyncio.sleep(dur)
        sound.stop()


def run_test():
    sound = SoundResource()
    sound.setup()
    sound.play_init_sound()
    sound.play_sin()
    sound.play_sin(880)
    sound.play_sin(880 * 2)
    sound.play_noise()
    sound.play_speech("This is a test")
    sound.play_speech("I am robot.")
    sound.play_speech("Hear me roar.")
    sound.play_init_sound()


if __name__ == "__main__":
    run_test()

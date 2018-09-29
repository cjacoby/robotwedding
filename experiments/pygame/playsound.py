import click
import numpy as np
import pathlib
import pygame
from pygame.mixer import Sound, get_init, pre_init
import os
import time

RESOURCES = pathlib.Path(__file__).resolve().parent.parent.parent / "resources"
wav_file = RESOURCES / "dt01_stab_britelite_16.wav"


class Note(Sound):

    def __init__(self, frequency, volume=.8, sample_rate=44100):
        self.frequency = frequency
        self.sr = sample_rate
        Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        sample_rate = pygame.mixer.get_init()[0]
        period = int(round(sample_rate / self.frequency))
        amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1

        def frame_value(i):
            return amplitude * np.sin(
                2.0 * np.pi * self.frequency * i / self.sr)

        return np.array([
            frame_value(x) for x in range(0, period)]).astype(np.int16)


@click.command()
def main():
    print(str(RESOURCES))
    os.chdir(RESOURCES)
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(wav_file.name)
        pygame.mixer.music.play()

        # milliseconds wait for each sound to finish
        pygame.time.wait(2000)

        # pre_init(44100, -16, 1, 1024)
        Note(440).play(-1)
        pygame.time.wait(2000)

    except KeyboardInterrupt:
        pass
    finally:
        print("Done")


if __name__ == "__main__":
    main()

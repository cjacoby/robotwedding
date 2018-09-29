import click
import pathlib
import pygame
import os
import time

RESOURCES = pathlib.Path(__file__).resolve().parent.parent.parent / "resources"
wav_file = RESOURCES / "dt01_stab_britelite_16.wav"


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

        while pygame.mixer.music.get_busy() is True:
            continue
    except KeyboardInterrupt:
        pass
    finally:
        print("Done")


if __name__ == "__main__":
    main()

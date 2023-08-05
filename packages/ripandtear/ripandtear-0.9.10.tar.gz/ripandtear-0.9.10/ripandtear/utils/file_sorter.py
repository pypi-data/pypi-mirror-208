import logging
import shutil
import re

from pathlib import Path

log = logging.getLogger(__name__)

audio_suffix = re.compile(r"\.(mp3|wav|m4a|)")
gif_suffix = re.compile(r"\.(gif|)")
image_suffix = re.compile(r"\.(jpg|jpeg|png|bmp|webp|)")
text_suffix = re.compile(r"\.(txt|)")
video_suffix = re.compile(r"\.(mp4|webm|mkv|mov|m4v|wmv|avi|flv|mpg|3gp|)")


async def sort():

    files = [file for file in Path().cwd().iterdir() if file.is_file()]

    log.info("Sorting files...")
    for file in files:

        try:
            source = Path(file).name

            if image_suffix.match(Path(file).suffix).group(1):

                destination = (f"pics/{Path(file).name}")
                dir = 'pics'
                await move_file(source, destination, dir)

            elif video_suffix.match(Path(file).suffix).group(1):

                destination = (f"vids/{Path(file).name}")
                dir = 'vids'
                await move_file(source, destination, dir)

            elif gif_suffix.match(Path(file).suffix).group(1):

                destination = (f"gifs/{Path(file).name}")
                dir = 'gifs'
                await move_file(source, destination, dir)

            elif audio_suffix.match(Path(file).suffix).group(1):

                destination = (f"audio/{Path(file).name}")
                dir = 'audio'
                await move_file(source, destination, dir)

            elif text_suffix.match(Path(file).suffix).group(1):

                destination = (f"text/{Path(file).name}")
                dir = 'text'
                await move_file(source, destination, dir)

        except AttributeError:
            log.info(f"Did not find mattching pattern for: {Path(file).name}")


async def file_size(source_file, destination_file):

    source_file_bytes = Path(source_file).stat().st_size

    destination_file_bytes = Path(destination_file).stat().st_size

    return (source_file_bytes, destination_file_bytes)


async def move_file(source, destination, dir):

    if not Path(destination).exists():

        Path(dir).mkdir(exist_ok=True)
        shutil.move(source, dir)

    else:

        file_sizes = await file_size(source, destination)

        if file_sizes[0] > file_sizes[1]:
            Path(destination).unlink()
            shutil.move(source, destination)

        else:
            Path(source).unlink()

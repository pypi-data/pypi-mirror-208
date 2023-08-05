from typing import List

import ffmpeg

from lecture_automator.gen_video.utils import get_codecs


def generate_video(path_images: List[str], path_wavs: List[str],
                   output_name: str, vformat: str='mp4') -> None:
    """Генерация видео на основе изображений и звука к каждому из них.

    Args:
        path_images (List[str]): список путей к изображениям в файловой системе.
        path_wavs (List[str]): список путей к звукам в файловой системе (каждый звук
        соответствует изображению с таким же индексом).
        output_name (str): название выходного видео.
    """

    files = []
    for path_image, path_wav in zip(path_images, path_wavs):
        files.extend([ffmpeg.input(path_image), ffmpeg.input(path_wav)])

    vcodec, acodec = get_codecs(vformat)

    joined = ffmpeg.concat(*files, v=1, a=1).node
    ffmpeg.output(
        joined[0], joined[1], output_name,
        f=vformat, vcodec=vcodec, acodec=acodec
    ).run(overwrite_output=True)

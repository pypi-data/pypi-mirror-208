from typing import Tuple

from lecture_automator.gen_video.exceptions import IncorrectVideoFormat


def get_codecs(vformat: str) -> Tuple[str, str]:
    if vformat == 'mp4':
        vcodec = 'libx264'
        acodec = 'aac'
    elif vformat == 'webm':
        vcodec = 'libvpx-vp9'
        acodec = 'libvorbis'
    else:
        raise IncorrectVideoFormat(
            'Некорректный формат видео: {}.'.format(vformat))

    return vcodec, acodec

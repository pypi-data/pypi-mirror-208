import glob
import os
import tempfile

from lecture_automator.gen_speech.gen_speech import texts_to_speeches
from lecture_automator.gen_video.gen_video import generate_video
from lecture_automator.marp_api import generate_marp_slides
from lecture_automator.parser.parser import parse_md


def compile_text_md(input_text_md: str, out_path: str,
                    vformat: str='mp4', scale: int=1) -> None:
    md_data = parse_md(input_text_md)

    with tempfile.TemporaryDirectory() as tmpdirname:
        generate_marp_slides(tmpdirname, md_data['md_text'], scale=scale)
        slide_images = glob.glob(os.path.join(tmpdirname, 'Slide.*'))
        audio_paths = texts_to_speeches(md_data['speech'], tmpdirname)
        generate_video(slide_images, audio_paths, out_path, vformat=vformat)

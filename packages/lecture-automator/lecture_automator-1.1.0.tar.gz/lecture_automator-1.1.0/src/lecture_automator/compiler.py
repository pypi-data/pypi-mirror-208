import glob
import os
import tempfile

from tqdm import tqdm

from lecture_automator.gen_speech.gen_speech import texts_to_speeches
from lecture_automator.gen_video.gen_video import generate_video
from lecture_automator.marp_api.marp_api import generate_marp_slides
from lecture_automator.parser.parser import parse_md


def compile_text_md(input_text_md: str, out_path: str,
                    vformat: str='mp4', scale: int=1,
                    verbose_progress: bool=False) -> None:
    md_data = parse_md(input_text_md)

    with tqdm(total=3, desc='Генерируем видео',
              bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}',
              disable=not verbose_progress) as bar:
        with tempfile.TemporaryDirectory() as tmpdirname:
            generate_marp_slides(tmpdirname, md_data['md_text'], scale=scale)
            slide_images = glob.glob(os.path.join(tmpdirname, 'Slide.*'))
            bar.update(1)

            audio_paths = texts_to_speeches(md_data['speech'], tmpdirname)
            bar.update(1)

            generate_video(slide_images, audio_paths, out_path, vformat=vformat)
            bar.update(1)

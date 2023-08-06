import os
import subprocess
import tempfile

from lecture_automator.marp_api.exceptions import MarpError


def generate_marp_slides(outdir: str, md_text: str, type_images: str = 'png', scale: float = 2.0) -> None:
    """Генерация слайдов презентации Marp в виде набора изображений.

    Args:
        outdir (str): директория для сохранения изображений.
        md_text (str): текст файла Markdown презентации Marp.
        type_images (str, optional): Формат изображений (png или jpeg). Defaults to 'png'.
    """

    with tempfile.TemporaryDirectory() as tmpdirname:
        path_to_md = os.path.join(tmpdirname, "input.md")
        with open(path_to_md, "w") as file:
            file.write(md_text)

        process = subprocess.Popen(
            ['marp', '--images', type_images, '--image-scale', str(scale),
             '-o', 'Slide.png', path_to_md],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=outdir
        )

        out, err = process.communicate()
        retcode = process.poll()
        if retcode:
            raise MarpError(out, err)


if __name__ == '__main__':
    with open('examples/Example.md') as file:
        text = file.read()

    generate_marp_slides('examples', text, scale=1.5)

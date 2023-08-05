import re
from typing import List, Tuple

from lecture_automator.parser.command_handler import CommandHandler
from lecture_automator.parser.exceptions import SpeechNotFound


def join_slides(slides: List[str], metaslide=None):
    md_text = '---\n'.join(slides)
    if metaslide:
        metaslide = '---\n{}---\n'.format(metaslide)
        md_text = '{}{}'.format(metaslide, md_text)

    return md_text


def parse_commands(slide: str) -> List[Tuple[str, str, int, int]]:
    """Парсинг управляющих конструкций для каждого слайда в презентации Markdown.

    Args:
        slide (str): текст слайда Markdown.

    Returns:
        List[Tuple[str, str, int, int]]: список кортежей
            (название команды, ее аргумент,
            начальная позиция в файле, конечная позиция в файле).
    """

    commands = []
    p = re.compile(r'/([a-z]+) *\{([^\{\}]+)\}')

    for match in p.finditer(slide):
        name_command = match.group(1)
        arg = match.group(2)
        start_pos = match.start()
        end_pos = match.end()

        if len(re.findall(r'(?m)\`{3}', slide[:start_pos])) % 2 != 0:
            continue

        commands.append(
            (name_command, arg, start_pos, end_pos)
        )

    return commands


def process_commands(slides: List[str]) -> Tuple[list, dict]:
    """Обработка управляющих конструкций.

    Args:
        slides (List[str]): список текстов слайдов Markdown.

    Returns:
        Tuple[str, dict]: кортеж (список обработанных текстов Markdown для каждого
            слайда, словарь метаданных для каждого слайда).
    """

    metadata = dict()
    processed_slides = []
    for idx, slide in enumerate(slides, start=1):
        metadata[idx] = dict()
        parsed_commands = parse_commands(slide)

        for name_command, arg, start_pos, end_pos in parsed_commands:
            command_replacer = CommandHandler.process(
                slide, name_command,
                arg, start_pos,
                end_pos, metadata[idx]
            )

            slide = "{}{}{}".format(
                slide[:start_pos],
                command_replacer,
                slide[end_pos:]
            )

        if 'speech' not in metadata[idx]:
            raise SpeechNotFound('Каждый слайд должен иметь описание речи.')

        processed_slides.append(slide)

    return processed_slides, metadata


def parse_slides(text: str) -> tuple:
    """Парсинг слайдов.

    Args:
        text (str): текст Markdown.

    Returns:
        tuple: метаданные презентации, список текстов слайдов.
    """

    metaslide = None
    slides = re.split(r'(?m)^\-{3}\n', text)
    if slides[0] == '':
        metaslide = slides[1]
        slides = slides[2:]

    # Обработка случаев, когда "---" находится во вложенных строках.
    idx = 0
    while True:
        if len(re.findall(r'(?m)\`{3}', slides[idx])) % 2 != 0:
            next_slide = slides.pop(idx + 1)
            slides[idx] = '{}---\n{}'.format(slides[idx], next_slide)
            continue

        if idx == len(slides) - 1:
            break

        idx += 1

    return metaslide, slides

def parse_md(md_text: str) -> dict:
    """Парсинг Markdown презентации формата Marp с дополнительными управляющими
    командами (/speech и т.д.)

    Args:
        path (str): путь к файлу Markdown.

    Returns:
        dict: словарь, содержащий текст Markdown для Marp
            (с удаленными управляющими командами) и метаданные.
    """

    metaslide, slides = parse_slides(md_text)
    processed_slides, metadata = process_commands(slides)
    processed_marp_text = join_slides(processed_slides, metaslide=metaslide)

    speech_metadata = [metadata[slide]['speech'] for slide in metadata]

    return {
        'md_text': processed_marp_text,
        'speech': speech_metadata
    }

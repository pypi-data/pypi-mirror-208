import click
from ffmpeg._run import Error as FFmpegError

from lecture_automator.compiler import compile_text_md
from lecture_automator.marp_api.exceptions import MarpError
from lecture_automator.web import run_web


@click.group()
def cli():
    pass


@cli.command()
@click.argument(
    'input_md',
    type=click.STRING,
)
@click.argument(
    'out_path',
    type=click.STRING,
)
@click.option(
    '--vformat',
    type=click.Choice(['mp4', 'webm']),
    default='mp4',
    help=(
        'Формат генерируемого видео.'
    )
)
@click.option(
    '--scale',
    type=click.FLOAT,
    default=1.5,
    help=(
        'Коэффициент масштабирования генерируемого видео, '
        'по умолчанию равен 1.5, что соответствует разрешению 1920x1080,'
        'значение 1 соответствует разрешению 1280x720.'
    )
)
def convert(input_md, out_path, scale, vformat):
    with open(input_md) as file:
        md_text = file.read()

    try:
        compile_text_md(
            md_text, out_path=out_path,
            vformat=vformat, scale=scale,
            verbose_progress=True
        )
    except FFmpegError as e:
        print('Ошибка ffmpeg:')
        print(e.stderr.decode())
    except MarpError as e:
        print('Ошибка Marp:')
        print(e.stderr.decode())


@cli.command()
def web():
    run_web()


if __name__ == '__main__':
    cli()

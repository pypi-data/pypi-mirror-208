# -*- coding: utf-8 -*-

import os
import tempfile

import torch

from lecture_automator.gen_speech.utils import concat_wavs, divide_text
from lecture_automator.settings import get_app_dir

MODEL_URL = 'https://models.silero.ai/models/tts/ru/v3_1_ru.pt'
MODEL_FILENAME = 'v3_1_ru.pt'
SPEAKER = 'xenia'
SAMPLE_RATE = 48000
MAX_SYMBOLS = 1000


def generate_speech(model, text: str, out_path: str, device: str = 'cpu') -> str:
    """Синтез речи.

    Args:
        model (_type_): модель для синтеза речи.
        text (str): текст для синтеза речи.
        out_path (str): полный путь к файлу для сохранения синтезированной речи.
        device (str, optional): устройство для вычислений модели. Defaults to 'cpu'.

    Returns:
        str: путь к синтезированной речи.
    """

    model.to(device)

    model.save_wav(
        text=text,
        speaker=SPEAKER,
        audio_path=out_path,
        sample_rate=SAMPLE_RATE
    )

    return out_path


def get_model(model_name: str):
    """Загрузка модели.

    Args:
        model_name (str): название модели для загрузки.

    Returns:
        _type_: _description_
    """

    model_path = os.path.join(get_app_dir(), model_name)

    if not os.path.exists(model_path):
        torch.hub.download_url_to_file(
            MODEL_URL,
            model_path
        )

    model = torch.package.PackageImporter(model_path).load_pickle(
        "tts_models", "model"
    )

    return model


def text_to_speech(text: str, out_path: str, device: str = 'cpu') -> str:
    """Синтез речи.

    Args:
        text (str): текст для синтеза речи.
        out_path (str): путь для сохранения сгенерированной речи.
        device (str, optional): устройство для вычислений (cuda, cpu и т.д.).
            Defaults to 'cpu'.

    Returns:
        str: название файла формата wav со сгенерированной речью по тексту.
    """

    model = get_model(MODEL_FILENAME)

    if len(text) > MAX_SYMBOLS:
        texts = divide_text(text, max_length=MAX_SYMBOLS)
    else:
        texts = [text]

    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_wavs = []
        for i, t in enumerate(texts):
            temp_out_path = os.path.join(tmpdirname, 'speech_{}'.format(str(i)))
            generate_speech(model, t, temp_out_path)
            temp_wavs.append(temp_out_path)
        concat_wavs(temp_wavs, out_path)

    return out_path


def texts_to_speeches(texts: list, out_dir: str, basename: str = 'Sound') -> list:
    audio_paths = []
    for index, text in enumerate(texts, start=1):
        audio_path = os.path.join(out_dir, '{}_{}.wav'.format(basename, index))
        text_to_speech(
            text, audio_path
        )
        audio_paths.append(audio_path)

    return audio_paths

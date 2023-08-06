import re
import wave
from typing import List


def divide_text(text: str, max_length: int = 1000) -> List[str]:
    """Разделение текста по точкам таким образом, чтобы каждая часть текста не превышала
    указанный максимум.
    Args:
        text (str): текст для разделения.
        max_length (int, optional): максимальная длина одной части текста. Defaults to
            1000.
    Raises:
        Exception: _description_
    Returns:
        List[str]: список частей текста.
    """

    split_texts = re.split(r'\.', text)
    result_texts = []

    symbols = 0
    last_processed_index_text = 0
    for i, t in enumerate(split_texts):
        if symbols + len(t) >= max_length or i == len(split_texts) - 1:
            if i == 0:
                raise Exception('Текст невозможно разделить!')
            result_texts.append(".".join(split_texts[last_processed_index_text:i]).strip())
            symbols = len(t)
            last_processed_index_text = i
        else:
            symbols += len(t)

    return result_texts


def concat_wavs(input_wavs: List[str], output_wav: str) -> str:
    """Объединение несколько wav-файлов в один.
    Args:
        input_wavs (List[str]): список путей к объединяемым wav-файлам.
        output_wav (str): путь к выходному wav-файлу.
    Returns:
        str: путь к выходному wav-файлу.
    """

    data = []
    for infile in input_wavs:
        with wave.open(infile, 'rb') as w:
            data.append([w.getparams(), w.readframes(w.getnframes())])

    with wave.open(output_wav, 'wb') as output:
        output.setparams(data[0][0])
        for i in range(len(data)):
            output.writeframes(data[i][1])

    return output_wav

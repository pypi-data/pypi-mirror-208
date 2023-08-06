import os
import subprocess

import streamlit as st

from lecture_automator.compiler import compile_text_md
from lecture_automator.settings import get_cache_dir


def run_web() -> None:
    subprocess.run([
        'streamlit', 'run', os.path.realpath(__file__)
    ])


def main_page() -> None:
    storage_path = get_cache_dir()

    st.markdown('# Lecture Automator')
    text = st.text_area('Текст генерируемой лекции:', height=500)

    if text:
        with st.spinner('Генерируем...'):
            out_path = os.path.join(storage_path, 'Video.webm')
            compile_text_md(
                text, out_path=out_path, vformat='webm')
        st.video(out_path)



if __name__ == '__main__':
    main_page()

import re
from abc import ABC, abstractmethod


class CommandHandler(ABC):
    def __init__(self, handler = None) -> None:
        self._next: CommandHandler = handler

    @abstractmethod
    def handle(self, slide, name_command, arg, start_pos, end_pos, metadata) -> str:
        if self._next is None:
            raise Exception('Неизвестная команда: {}'.format(slide[start_pos:end_pos]))
        return self._next.handle(slide, name_command, arg, start_pos, end_pos)

    @staticmethod
    def process(slide, name_command, arg, start_pos, end_pos, metadata):
        handler = SpeechHandler()
        return handler.handle(slide, name_command, arg, start_pos, end_pos, metadata)


class SpeechHandler(CommandHandler):
    def handle(self, slide, name_command, arg, start_pos, end_pos, metadata) -> str:
        if name_command == 'speech':
            print(slide[end_pos:])
            if re.sub(r'(?m)[ \n\t]+', '', slide[end_pos:]):
                raise Exception(
                    'Управляющая конструкция /speech должна находиться в конце описания слайда!'
                )
            metadata.update(
                {
                    'speech': arg
                }
            )
            return ''
        else:
            return super().handle(slide, name_command, arg, start_pos, end_pos)

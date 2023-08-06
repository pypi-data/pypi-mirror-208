import collections
import dataclasses
import typing

import kurses.colors


@dataclasses.dataclass
class CharacterAttribute:
    code: chr = ''
    x: int = 0
    y: int = 0
    foreign: kurses.colors.TupleColor = (255, 255, 255)
    background: kurses.colors.TupleColor = (0, 0, 0)
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    blink: int = 0

    def __eq__(self, other):
        return self.code == other.code

    def __hash__(self):
        _hash_tuple = (
            self.code, self.foreign, self.background, self.bold, self.italic, self.underline, self.strikethrough)

        return hash(_hash_tuple)

    def __bool__(self):
        return not self.code == ' '


@dataclasses.dataclass
class RectangleAttribute:
    x: int
    y: int
    w: int
    h: int
    color: kurses.colors.TupleColor


class BufferTerm:
    def __init__(self, columns: int, rows: int):
        self.resetall()
        self.__current_position = 0, 0
        self.__shape = rows, columns
        self.__queue = collections.deque()

    def __iter__(self):
        while len(self.__queue) != 0:
            yield self.__queue.pop()

    def resize(self, columns: int, rows: int) -> None:
        self.__shape = rows, columns

    def getbuffersize(self) -> typing.Tuple[int, int]:
        return self.__shape

    @property
    def buffersize(self) -> typing.Tuple[int, int]:
        return self.getbuffersize()

    @buffersize.setter
    def buffersize(self, shape: typing.Tuple[int, int]):
        self.resize(*shape)

    def clreol(self) -> None:
        ...

    def clrscr(self) -> None:
        self.__queue.clear()

    def wherex(self):
        return self.__current_position[0]

    def wherey(self):
        return self.__current_position[1]

    @property
    def current_cursor(self):
        return self.__current_position

    def gotoxy(self, x: int, y: int) -> None:
        self.__current_position = x, y

    def resetall(self):
        self.__current_position = 0, 0
        self.__bold = False
        self.__italic = False
        self.__underline = False
        self.__strikethrough = False
        self.__foreign_color = (255, 255, 255)
        self.__background_color = (0, 0, 0)

    def set_background_color(self, color: kurses.colors.Color) -> None:
        if isinstance(color, int):
            color = kurses.colors.hex_to_rgb(color)

        self.__background_color = color

    def set_foreign_color(self, color: kurses.colors.Color) -> None:
        if isinstance(color, int):
            color = kurses.colors.hex_to_rgb(color)

        self.__foreign_color = color

    def bold(self, _bool: bool):
        self.__bold = _bool

    def italic(self, _bool: bool):
        self.__italic = _bool

    def underline(self, _bool: bool):
        self.__underline = _bool

    def strikethrough(self, _bool: bool):
        self.__strikethrough = _bool

    def __create_character_attr(self, _chr, x, y):
        return CharacterAttribute(
            _chr, x, y,
            self.__foreign_color,
            self.__background_color,
            self.__bold,
            self.__italic,
            self.__underline,
            self.__strikethrough
        )

    def cputs(self, _chr: chr):
        x, y = self.__current_position
        self.__queue.appendleft(self.__create_character_attr(_chr, x, y))

    def print(self, _str: str):
        x, y = self.wherex(), self.wherey()
        for _chr in _str:
            self.gotoxy(x, y)
            self.cputs(_chr)
            x += 1

    def putchxy(self, x: int, y: int, _chr: chr) -> None:
        self.__current_position = x, y
        self.__queue.appendleft(self.__create_character_attr(_chr, x, y))

    def cputsxy(self, x: int, y: int, _str: str) -> None:
        for _chr in _str:
            self.putchxy(x, y, _chr)
            x += 1

    def putrect(self, x: int, y: int, w: int, h: int):
        self.__queue.appendleft(
            RectangleAttribute(
                x, y,
                w, h,
                self.__background_color
            )
        )

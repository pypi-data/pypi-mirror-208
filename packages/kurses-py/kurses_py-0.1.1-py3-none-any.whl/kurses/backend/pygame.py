import kurses.virtual_console
from kurses.virtual_console import T


class PygameVirtualConsole(kurses.virtual_console.VirtualConsole):
    def keyspressed(self) -> list[chr]:
        pass

    @property
    def window(self) -> T:
        pass

    @property
    def surface(self) -> T:
        pass

    @property
    def font(self) -> T:
        pass

    def clear_cache(self):
        pass

    def present(self):
        pass

    def push_events(self):
        pass

    def quit(self):
        pass

    @property
    def buffer(self) -> kurses.buffer_matrix.BufferTerm:
        pass

    def set_target(self, target):
        pass

    def main_loop(self):
        pass

    def set_title(self, _str: str):
        pass

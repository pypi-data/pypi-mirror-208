import random

from kurses import Console

if __name__ == "__main__":
    console = Console()
    console.set_font("ModernDOS8x16.ttf", 16)
    console.set_resizable(True)

    def main():
        term = console.buffer

        term.set_background_color((0, 255, 0))
        term.set_foreign_color((225, 23, 155))
        term.putrect(0, 0, 5, 30)
        term.cputsxy(0, 0, "Hello world")

        term.italic(True)
        term.bold(True)
        term.set_background_color((255, 255, 255))
        term.set_foreign_color((0, 0, 0))
        term.cputsxy(6, 1, "Italic and bold text")

        term.resetall()

        term.underline(True)
        term.cputsxy(16, 16, "Underline text")

        term.resetall()

        x = 3
        for _c in "Random color":
            term.set_foreign_color(tuple(random.randint(0, 255) for _ in range(3)))
            term.set_background_color(tuple(random.randint(0, 255) for _ in range(3)))
            term.gotoxy(x, 12)
            term.cputs(_c)
            x += 1

        term.resetall()

        term.strikethrough(True)
        term.set_foreign_color((255, 0, 0))
        term.cputsxy(24, 24, "Strikethrough text")

        term.resetall()


    console.set_target(main)
    console.main_loop()

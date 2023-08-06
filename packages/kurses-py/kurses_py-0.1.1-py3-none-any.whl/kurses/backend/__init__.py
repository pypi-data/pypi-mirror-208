# So, I need work her

try:
    import sdl2
    from kurses.backend.sdl2 import SDL2VirtualConsole

    Console = SDL2VirtualConsole

except ImportError:
    try:
        import pygame
        from kurses.backend.pygame import PygameVirtualConsole

        Console = PygameVirtualConsole
    except ImportError:
        raise ImportError("You need install pySDL2 or Pygame for this module work!")

__all__ = ["Console"]

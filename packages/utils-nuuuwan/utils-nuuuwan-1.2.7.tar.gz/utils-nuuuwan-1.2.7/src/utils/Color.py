import random


class Color:
    @staticmethod
    def _8bit():
        return random.randint(0, 255)

    @staticmethod
    def _4bit_hex():
        return random.choice('0123456789abcdef')

    @staticmethod
    def _8bit_hex():
        return Color._4bit_hex() + Color._4bit_hex()

    @staticmethod
    def _360():
        return random.randint(0, 355)

    @staticmethod
    def _float():
        return random.random()

    @staticmethod
    def _percent():
        return random.randint(0, 100)

    @staticmethod
    def rgba(r=None, g=None, b=None, a=None):
        r = r or Color._8bit()
        g = g or Color._8bit()
        b = b or Color._8bit()
        a = a or Color._float()
        return f'rgba({r:d},{g:d},{b:d},{a:.2f})'

    @staticmethod
    def hsla(h=None, s=None, light=None, a=None):
        h = h or Color._360()
        s = s or Color._percent()
        light = light or Color._percent()
        a = a or Color._float()
        return f'hsla({h:d},{s:d}%,{light:d}%,{a:.2f})'

    @staticmethod
    def hex():
        return '#' + ''.join([Color._8bit_hex() for _ in range(3)])

# coding: utf-8
# Copyright (c) 2023 Vlad Bilskiy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.
#
# Github: https://github.com/hittiks

"""ANSII Color formatting for output in terminal."""

__ALL__ = [ "RGBColor", "colorize" ]

class RGBColor():
    color_names = {
            "red": [255, 0, 0],
            "green": [0, 255, 0],
            "blue": [0, 100, 255],
            "white": [255, 255, 255],
            "black": [0, 0, 0],
            "orange": [255, 153, 0],
            "yellow": [255, 255, 0],
            "cyan": [0, 255, 255],
            "lightblue": [0, 200, 255],
            "violet": [120, 70, 200],
        }

    def __init__(self, red: int = -1, green: int = -1, blue: int = -1, color_name: str = "") -> None:
        if color_name:
            assert isinstance(color_name, str), f"Type of color_name must be str but now is {type(color_name).__name__}"

            if not self.color_names.get(color_name):
                raise ValueError((
                    f"Invalid color name '{color_name}'."
                    f" Use {__name__}.{__class__.__name__}.get_color_names() and choose one of them or"
                    f" set new by metod {__name__}.{__class__.__name__}.set_color_name()"
                ))
            
            self.init(*self.color_names[color_name])
        else:
            self.init(red, green, blue)

    def init(self, red: int, green: int, blue: int) -> None:
        assert isinstance(red, int), f"Type of red must be int but now is {type(red).__name__}"
        assert isinstance(green, int), f"Type of green must be int but now is {type(green).__name__}"
        assert isinstance(blue, int), f"Type of blue must be str int now is {type(blue).__name__}"

        for x in [red, green, blue]:
            if x < 0 or x > 255:
                raise ValueError("Use integer from 0 to 255")

        self.red = red
        self.green = green
        self.blue = blue

    @staticmethod
    def get_color_names() -> tuple:
        return tuple(__class__.color_names.keys())

    @staticmethod
    def set_color_name(red: int, green: int, blue: int, color_name: str) -> None:
        if not color_name:
            raise ValueError("Param color_name must not be empty")
        
        assert isinstance(red, int), f"Type of red must be int but now is {type(red).__name__}"
        assert isinstance(green, int), f"Type of green must be int but now is {type(green).__name__}"
        assert isinstance(blue, int), f"Type of blue must be str int now is {type(blue).__name__}"
        assert isinstance(color_name, str), f"Type of color_name must be str but now is {type(color_name).__name__}"

        for x in [red, green, blue]:
            if x < 0 or x > 255:
                raise ValueError("Use integer from 0 to 255")
        __class__.color_names[color_name] = [red, green, blue]


def colorize(text: str, color: RGBColor, on_color: RGBColor = None) -> str:
    assert isinstance(text, str), f"Type of text must be str but now is {type(text).__name__}"
    assert isinstance(color, RGBColor), f"Type of color must be RGBColor but now is {type(color).__name__}"

    bg = ""
    if on_color:
        assert isinstance(color, RGBColor), f"Type of color must be RGBColor but now is {type(color).__name__}"
        bg = f"48;2;{on_color.red};{on_color.green};{on_color.blue};"

    return (f"\033[{bg}38;2;{color.red};{color.green};{color.blue}m{text}\033[0m")


if __name__ == "__main__":
    print(colorize("Here a simple usage of red color by name", RGBColor(color_name="red")))
    print(colorize("Here a simple usage of red color by rgb params", RGBColor(255, 0, 0)))
    
    RGBColor.set_color_name(120, 70, 200, "my_color")

    print(colorize("Here a simple usage of custom color by name", RGBColor(color_name="my_color")))
    print(colorize("But note that two names can have same rgb params (here use violet color name)\n", RGBColor(color_name="violet")))

    print(colorize("Also you can get color names that available", RGBColor(color_name="green")))

    for __color in RGBColor.get_color_names():
        print(colorize(f"This text have {__color} color", RGBColor(color_name=__color)))
    
    print(colorize("\nAnd you can set background color with on_color param (by name or rgb values), but it's not necessary\n", RGBColor(color_name="blue")))

    print(colorize("For example this text has red color on yellow background", RGBColor(color_name="red"), RGBColor(color_name="yellow")))

    print(colorize("\nSometimes for some reason on different platform colors may look different", RGBColor(color_name="blue")))

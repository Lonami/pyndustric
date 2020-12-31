from typing import Union

class Resource:
    pass

class Screen:
    @staticmethod
    def clear(r: int, g: int, b: int):
        """Clear the entire display buffer to the given RGB values."""

    @staticmethod
    def color(r: int, g: int, b: int, a: int = 255):
        """Set the current brush color to the given RGBA values."""

    @staticmethod
    def stroke(width: int):
        """Set the current brush stroke width to the given value."""

    @staticmethod
    def line(x0: int, y0: int, x1: int, y1: int):
        """
        Draw a line from `(x0, y0)` towards `(x1, y1)`.

        The line will be as wide as previously defined by `stroke`, and the ends will be straight.

        You may use it to make rotated rectangles by setting a big enough stroke.
        """

    @staticmethod
    def rect(x: int, y: int, width: int, height: int):
        """
        Draw a filled rectangle with its bottom-left corner at `(x, y)` and size `(width, height)`.
        """

    @staticmethod
    def hollow_rect(x: int, y: int, width: int, height: int):
        """
        Like `rect`, but hollow. This border width considers the `stroke`.
        """

    @staticmethod
    def poly(x: int, y: int, radius: int, sides: int, rotation: int = 0):
        """
        Draw a polygon centered at `(x, y)` with the specified `radius` and `sides`.

        For example, 3 sides make a triangle, while a high number like 20 make it look like a circle.

        The rotation is optional and specified in degrees.
        """

    @staticmethod
    def hollow_poly(x: int, y: int, radius: int, sides: int, rotation: int = 0):
        """
        Like `poly`, but hollow. This border width considers the `stroke`.
        """

    @staticmethod
    def triangle(x0: int, y0: int, x1: int, y1: int, x2: int, y2: int):
        """
        Draw a triangle with corners at `(x0, y0)`, `(x1, y1)` and `(x2, y2)`.
        """

    @staticmethod
    def image(x: int, y: int, image: Resource, size: int, rotation: int = 0):
        """
        Draw the image resource centered at `(x, y)` with `size` and optional `rotation`.
        """

    @staticmethod
    def flush(display: str = None):
        """Flush the screen buffer to the display."""


def print(message: str, flush: Union[bool, str] = True):
    """
    Print a message. f-strings are supported and encouraged to do string formatting.

    `flush` may be a boolean indicating whether to emit `printflush` or not, or the name of the message.
    """

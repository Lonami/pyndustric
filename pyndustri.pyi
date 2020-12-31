from typing import Iterator, Optional, Union


class Link:
    """Represents a link."""


class Env:
    """
    Access to special environmental variables.
    """

    @staticmethod
    def this():
        """Return the `Building` object representing this logic processor."""

    @staticmethod
    def x():
        """Return the `x` coordinate where `this` is located."""

    @staticmethod
    def y():
        """Return the `y` coordinate where `this` is located."""

    @staticmethod
    def counter():
        """
        Return the Program Counter (also known as Instruction Pointer).

        The value is a number representing the index of the *next* instruction.
        """

    @staticmethod
    def links() -> Iterator[Link]:
        """Used to iterate over all the links."""

    @staticmethod
    def link_count():
        """Return how many links there are connected to `this` logic processor."""

    @staticmethod
    def time():
        """Return the current UNIX timestamp, in milliseconds."""

    @staticmethod
    def width():
        """Return the width of the entire map, in tiles."""

    @staticmethod
    def height():
        """Return the height of the entire map, in tiles."""


# https://github.com/Anuken/Mindustry/blob/e714d44/core/assets/bundles/bundle.properties#L979-L998
# https://github.com/Anuken/Mindustry/blob/8bc349b/core/src/mindustry/logic/LAccess.java#L6-L47
class Sensor:
    """
    Access to a property of a given link.
    """
    @staticmethod
    def copper(link: Link) -> int:
        """Amount of Copper stored or carried by the link."""
    @staticmethod
    def lead(link: Link) -> int:
        """Amount of Lead stored or carried by the link."""
    @staticmethod
    def coal(link: Link) -> int:
        """Amount of Coal stored or carried by the link."""
    @staticmethod
    def graphite(link: Link) -> int:
        """Amount of Graphite stored or carried by the link."""
    @staticmethod
    def titanium(link: Link) -> int:
        """Amount of Titanium stored or carried by the link."""
    @staticmethod
    def thorium(link: Link) -> int:
        """Amount of Thorium stored or carried by the link."""
    @staticmethod
    def silicon(link: Link) -> int:
        """Amount of Silicon stored or carried by the link."""
    @staticmethod
    def plastanium(link: Link) -> int:
        """Amount of Plastanium stored or carried by the link."""
    @staticmethod
    def phase_fabrix(link: Link) -> int:
        """Amount of Phase Fabric stored or carried by the link."""
    @staticmethod
    def surge_alloy(link: Link) -> int:
        """Amount of Surge Alloy stored or carried by the link."""
    @staticmethod
    def spore_pod(link: Link) -> int:
        """Amount of Spore Pod stored or carried by the link."""
    @staticmethod
    def sand(link: Link) -> int:
        """Amount of Sand stored or carried by the link."""
    @staticmethod
    def blast_compound(link: Link) -> int:
        """Amount of Blast Compound stored or carried by the link."""
    @staticmethod
    def pyratite(link: Link) -> int:
        """Amount of Pyratite stored or carried by the link."""
    @staticmethod
    def metaglass(link: Link) -> int:
        """Amount of Metaglass stored or carried by the link."""
    @staticmethod
    def scrap(link: Link) -> int:
        """Amount of Scrap stored or carried by the link."""
    @staticmethod
    def water(link: Link) -> int:
        """Amount of Water stored or carried by the link."""
    @staticmethod
    def slag(link: Link) -> int:
        """Amount of Slag stored or carried by the link."""
    @staticmethod
    def oil(link: Link) -> int:
        """Amount of Oil stored or carried by the link."""
    @staticmethod
    def cryofluid(link: Link) -> int:
        """Amount of Cryofluid stored or carried by the link."""
    @staticmethod
    def items(link: Link) -> int:
        """The sum of all items contained or carried by the link."""
    @staticmethod
    def first_item(link: Link) -> Optional[Link]:
        """A link to the first contained item carried by the link, if any."""
    @staticmethod
    def liquids(link: Link) -> int:
        """The sum of all liquids contained or carried by the link."""
    @staticmethod
    def power(link: Link) -> int:
        """The current total power consumption by the link."""
    @staticmethod
    def max_items(link: Link) -> int:
        """How maximum amount of items the link can contain or carry."""
    @staticmethod
    def max_liquids(link: Link) -> int:
        """How maximum amount of liquids the link can contain or carry."""
    @staticmethod
    def max_power(link: Link) -> int:
        """The maximum amount of power the link can store."""
    @staticmethod
    def power_stored(link: Link) -> int:
        """The amount of power stored in the link."""
    @staticmethod
    def power_capacity(link: Link) -> int:
        """The amount of power the link can store."""
    @staticmethod
    def power_in(link: Link) -> int:
        """The net amount of power goiong into the link."""
    @staticmethod
    def power_out(link: Link) -> int:
        """The net amount of power goiong out of the link."""
    @staticmethod
    def ammo(link: Link) -> int:
        """The current amount of ammunition the current link has."""
    @staticmethod
    def max_ammo(link: Link) -> int:
        """The maximum amount of ammunition the current link has."""
    @staticmethod
    def health(link: Link) -> int:
        """The current health of the link."""
    @staticmethod
    def max_health(link: Link) -> int:
        """The maximum health of the link."""
    @staticmethod
    def heat(link: Link) -> int:
        """The current heat of the link."""
    @staticmethod
    def efficiency(link: Link) -> int:
        """The current efficiency of the link (base and boosts)."""
    @staticmethod
    def rotation(link: Link) -> int:
        """The current rotation of the link."""
    @staticmethod
    def x(link: Link) -> int:
        """The X logic tile coordinate of the link. Whole numbers are at the center of the tile."""
    @staticmethod
    def y(link: Link) -> int:
        """The Y logic tile coordinate of the link. Whole numbers are at the center of the tile."""
    @staticmethod
    def shoot_x(link: Link) -> int:
        """The X coordinate where the link is shooting to."""
    @staticmethod
    def shoot_y(link: Link) -> int:
        """The Y coordinate where the link is shooting to."""
    @staticmethod
    def shooting(link: Link) -> bool:
        """True if the link is currently shooting."""
    @staticmethod
    def mine_x(link: Link) -> int:
        """The X coordinate where the link is currently mining at."""
    @staticmethod
    def mine_y(link: Link) -> int:
        """The Y coordinate where the link is currently mining at."""
    @staticmethod
    def mining(link: Link) -> bool:
        """True if the link is currently mining"""
    @staticmethod
    def team(link: Link) -> int:
        """The team identifier to which the link belongs."""
    @staticmethod
    def type(link: Link) -> int:
        """The type of the link."""
    @staticmethod
    def flag(link: Link) -> int:
        """The custom flag variable stored in the link."""
    @staticmethod
    def controlled(link: Link) -> bool:
        """Is this link being controlled?"""
    @staticmethod
    def commanded(link: Link) -> bool:
        """Is this link being commanded?"""
    @staticmethod
    def name(link: Link) -> int:
        """The name of the link."""
    @staticmethod
    def config(link: Link) -> bool:
        """The configuration of the link."""
    @staticmethod
    def payload(link: Link) -> int:
        """The amount of payload the link is carrying."""
    def payload_type(link: Link) -> int:
        """The type of the payload."""
    @staticmethod
    def enabled(link: Link) -> bool:
        """Is this link enabled?"""


class Control:
    """
    Lets you control a given link.
    """
    @staticmethod
    def enabled(link: Link, enabled: bool):
        """Sets the link enabled or disabled, based on the given value."""

    def shoot(link: Link, x: int, y: int, enabled: bool = True):
        """Sets the link to shoot or not, and if shooting, the position."""

    def ceasefire(link: Link):
        """Shorthand to stop firing."""


class Screen:
    """
    Method interface to the `draw` and `drawflush` command.
    """

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

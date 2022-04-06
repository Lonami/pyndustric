from abc import ABC
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
class Senseable(ABC):
    """
    Type hints for things that can be sensed.
    """

    def copper(self) -> int:
        """Amount of Copper stored or carried by the link."""
    def lead(self) -> int:
        """Amount of Lead stored or carried by the link."""
    def coal(self) -> int:
        """Amount of Coal stored or carried by the link."""
    def graphite(self) -> int:
        """Amount of Graphite stored or carried by the link."""
    def titanium(self) -> int:
        """Amount of Titanium stored or carried by the link."""
    def thorium(self) -> int:
        """Amount of Thorium stored or carried by the link."""
    def silicon(self) -> int:
        """Amount of Silicon stored or carried by the link."""
    def plastanium(self) -> int:
        """Amount of Plastanium stored or carried by the link."""
    def phase_fabric(self) -> int:
        """Amount of Phase Fabric stored or carried by the link."""
    def surge_alloy(self) -> int:
        """Amount of Surge Alloy stored or carried by the link."""
    def spore_pod(self) -> int:
        """Amount of Spore Pod stored or carried by the link."""
    def sand(self) -> int:
        """Amount of Sand stored or carried by the link."""
    def blast_compound(self) -> int:
        """Amount of Blast Compound stored or carried by the link."""
    def pyratite(self) -> int:
        """Amount of Pyratite stored or carried by the link."""
    def metaglass(self) -> int:
        """Amount of Metaglass stored or carried by the link."""
    def scrap(self) -> int:
        """Amount of Scrap stored or carried by the link."""
    def water(self) -> int:
        """Amount of Water stored or carried by the link."""
    def slag(self) -> int:
        """Amount of Slag stored or carried by the link."""
    def oil(self) -> int:
        """Amount of Oil stored or carried by the link."""
    def cryofluid(self) -> int:
        """Amount of Cryofluid stored or carried by the link."""
    def items(self) -> int:
        """The sum of all items contained or carried by the link."""
    def first_item(self) -> Optional[Link]:
        """A link to the first contained item carried by the link, if any."""
    def liquids(self) -> int:
        """The sum of all liquids contained or carried by the link."""
    def power(self) -> int:
        """The current total power consumption by the link."""
    def max_items(self) -> int:
        """How maximum amount of items the link can contain or carry."""
    def max_liquids(self) -> int:
        """How maximum amount of liquids the link can contain or carry."""
    def max_power(self) -> int:
        """The maximum amount of power the link can store."""
    def power_stored(self) -> int:
        """The amount of power stored in the link."""
    def power_capacity(self) -> int:
        """The amount of power the link can store."""
    def power_in(self) -> int:
        """The net amount of power goiong into the link."""
    def power_out(self) -> int:
        """The net amount of power goiong out of the link."""
    def ammo(self) -> int:
        """The current amount of ammunition the current link has."""
    def max_ammo(self) -> int:
        """The maximum amount of ammunition the current link has."""
    def health(self) -> int:
        """The current health of the link."""
    def max_health(self) -> int:
        """The maximum health of the link."""
    def heat(self) -> int:
        """The current heat of the link."""
    def efficiency(self) -> int:
        """The current efficiency of the link (base and boosts)."""
    def rotation(self) -> int:
        """The current rotation of the link."""
    def x(self) -> int:
        """The X logic tile coordinate of the link. Whole numbers are at the center of the tile."""
    def y(self) -> int:
        """The Y logic tile coordinate of the link. Whole numbers are at the center of the tile."""
    def shoot_x(self) -> int:
        """The X coordinate where the link is shooting to."""
    def shoot_y(self) -> int:
        """The Y coordinate where the link is shooting to."""
    def shooting(self) -> bool:
        """True if the link is currently shooting."""
    def mine_x(self) -> int:
        """The X coordinate where the link is currently mining at."""
    def mine_y(self) -> int:
        """The Y coordinate where the link is currently mining at."""
    def mining(self) -> bool:
        """True if the link is currently mining"""
    def team(self) -> int:
        """The team identifier to which the link belongs."""
    def type(self) -> int:
        """The type of the link."""
    def flag(self) -> int:
        """The custom flag variable stored in the link."""
    def controlled(self) -> bool:
        """Is this link being controlled?"""
    def commanded(self) -> bool:
        """Is this link being commanded?"""
    def name(self) -> int:
        """The name of the link."""
    def config(self) -> bool:
        """The configuration of the link."""
    def payload(self) -> int:
        """The amount of payload the link is carrying."""
    def payload_type(self) -> int:
        """The type of the payload."""
    def enabled(self) -> bool:
        """Is this link enabled?"""

class Controllable(ABC):
    """
    Type hints for things that can be controlled.
    """

    def enabled(self, enabled: bool):
        """Sets the link enabled or disabled, based on the given value."""
    def shoot(self, x: int, y: int, enabled: bool = True):
        """Sets the link to shoot or not, and if shooting, the position."""
    def ceasefire(self):
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

class Unit(Senseable):
    """
    The bound unit.

    By default, this is not bound to anything. You should `bind` before using the other methods.

    This unit should be used as a singleton. It is also senseable (you can use `Unit.x`, etc.).
    """

    @staticmethod
    def bind(unit: str):
        """
        Bind to the next unit of the given type.

        The available units types are:

        * Mechas: mace, dagger, crawler, fortress, scepter, reign, vela, nova, pulsar, quasar.
        * Legged: corvus, atrax, spiroct, arkyid, toxopid.
        * Airborne: flare, eclipse, horizon, zenith, antumbra, mono, poly, mega, quad, oct.
        * Naval: risso, minke, bryde, sei, omura, retusa, oxynoe, cyerce, aegires, navanax.
        * Player: alpha, beta, gamma.
        """

Unit = Unit()

def print(message: str, flush: Union[bool, str] = True):
    """
    Print a message. f-strings are supported and encouraged to do string formatting.

    `flush` may be a boolean indicating whether to emit `printflush` or not, or the name of the message.
    """

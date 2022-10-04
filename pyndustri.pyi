from abc import ABC
from typing import Iterator, Optional, Union

class Link:
    """Represents a link."""

class Env:
    """
    Access to special environmental variables.
    """

    @property
    def this():
        """Return the `Building` object representing this logic processor."""
    @property
    def x():
        """Return the `x` coordinate where `this` is located."""
    @property
    def y():
        """Return the `y` coordinate where `this` is located."""
    @property
    def counter():
        """
        Return the Program Counter (also known as Instruction Pointer).

        The value is a number representing the index of the *next* instruction.
        """
    @staticmethod
    def links() -> Iterator[Link]:
        """Used to iterate over all the links."""
    @property
    def link_count():
        """Return how many links there are connected to `this` logic processor."""
    @property
    def time():
        """Return the current UNIX timestamp, in milliseconds."""
    @property
    def width():
        """Return the width of the entire map, in tiles."""
    @property
    def height():
        """Return the height of the entire map, in tiles."""
    @property
    def ips():
        # https://github.com/Anuken/Mindustry/blob/b7f030eb1342fc4fd7c46274bfa9ed7af25f5829/core/src/mindustry/world/blocks/logic/LogicBlock.java#L128
        """Return the amount of instructions per second this processor is capable of executing."""

Env = Env()

# https://github.com/Anuken/Mindustry/blob/e714d44/core/assets/bundles/bundle.properties#L979-L998
# https://github.com/Anuken/Mindustry/blob/8bc349b/core/src/mindustry/logic/LAccess.java#L6-L47
class Senseable(ABC):
    """
    Type hints for things that can be sensed.
    """

    @property
    def copper(self) -> int:
        """Amount of Copper stored or carried by the link."""
    @property
    def lead(self) -> int:
        """Amount of Lead stored or carried by the link."""
    @property
    def coal(self) -> int:
        """Amount of Coal stored or carried by the link."""
    @property
    def graphite(self) -> int:
        """Amount of Graphite stored or carried by the link."""
    @property
    def titanium(self) -> int:
        """Amount of Titanium stored or carried by the link."""
    @property
    def thorium(self) -> int:
        """Amount of Thorium stored or carried by the link."""
    @property
    def silicon(self) -> int:
        """Amount of Silicon stored or carried by the link."""
    @property
    def plastanium(self) -> int:
        """Amount of Plastanium stored or carried by the link."""
    @property
    def phase_fabric(self) -> int:
        """Amount of Phase Fabric stored or carried by the link."""
    @property
    def surge_alloy(self) -> int:
        """Amount of Surge Alloy stored or carried by the link."""
    @property
    def spore_pod(self) -> int:
        """Amount of Spore Pod stored or carried by the link."""
    @property
    def sand(self) -> int:
        """Amount of Sand stored or carried by the link."""
    @property
    def blast_compound(self) -> int:
        """Amount of Blast Compound stored or carried by the link."""
    @property
    def pyratite(self) -> int:
        """Amount of Pyratite stored or carried by the link."""
    @property
    def metaglass(self) -> int:
        """Amount of Metaglass stored or carried by the link."""
    @property
    def scrap(self) -> int:
        """Amount of Scrap stored or carried by the link."""
    @property
    def water(self) -> int:
        """Amount of Water stored or carried by the link."""
    @property
    def slag(self) -> int:
        """Amount of Slag stored or carried by the link."""
    @property
    def oil(self) -> int:
        """Amount of Oil stored or carried by the link."""
    @property
    def cryofluid(self) -> int:
        """Amount of Cryofluid stored or carried by the link."""
    @property
    def items(self) -> int:
        """The sum of all items contained or carried by the link."""
    @property
    def first_item(self) -> Optional[Link]:
        """A link to the first contained item carried by the link, if any."""
    @property
    def liquids(self) -> int:
        """The sum of all liquids contained or carried by the link."""
    @property
    def power(self) -> int:
        """The current total power consumption by the link."""
    @property
    def max_items(self) -> int:
        """How maximum amount of items the link can contain or carry."""
    @property
    def max_liquids(self) -> int:
        """How maximum amount of liquids the link can contain or carry."""
    @property
    def max_power(self) -> int:
        """The maximum amount of power the link can store."""
    @property
    def power_stored(self) -> int:
        """The amount of power stored in the link."""
    @property
    def power_capacity(self) -> int:
        """The amount of power the link can store."""
    @property
    def power_in(self) -> int:
        """The net amount of power goiong into the link."""
    @property
    def power_out(self) -> int:
        """The net amount of power goiong out of the link."""
    @property
    def ammo(self) -> int:
        """The current amount of ammunition the current link has."""
    @property
    def max_ammo(self) -> int:
        """The maximum amount of ammunition the current link has."""
    @property
    def health(self) -> int:
        """The current health of the link."""
    @property
    def max_health(self) -> int:
        """The maximum health of the link."""
    @property
    def heat(self) -> int:
        """The current heat of the link."""
    @property
    def efficiency(self) -> int:
        """The current efficiency of the link (base and boosts)."""
    @property
    def rotation(self) -> int:
        """The current rotation of the link."""
    @property
    def x(self) -> int:
        """The X logic tile coordinate of the link. Whole numbers are at the center of the tile."""
    @property
    def y(self) -> int:
        """The Y logic tile coordinate of the link. Whole numbers are at the center of the tile."""
    @property
    def shoot_x(self) -> int:
        """The X coordinate where the link is shooting to."""
    @property
    def shoot_y(self) -> int:
        """The Y coordinate where the link is shooting to."""
    @property
    def shooting(self) -> bool:
        """True if the link is currently shooting."""
    @property
    def mine_x(self) -> int:
        """The X coordinate where the link is currently mining at."""
    @property
    def mine_y(self) -> int:
        """The Y coordinate where the link is currently mining at."""
    @property
    def mining(self) -> bool:
        """True if the link is currently mining"""
    @property
    def team(self) -> int:
        """The team identifier to which the link belongs."""
    @property
    def type(self) -> int:
        """The type of the link."""
    @property
    def flag(self) -> int:
        """The custom flag variable stored in the link."""
    @property
    def controlled(self) -> bool:
        """Is this link being controlled?"""
    @property
    def commanded(self) -> bool:
        """Is this link being commanded?"""
    @property
    def name(self) -> int:
        """The name of the link."""
    @property
    def config(self) -> bool:
        """The configuration of the link."""
    @property
    def payload(self) -> int:
        """The amount of payload the link is carrying."""
    @property
    def payload_type(self) -> int:
        """The type of the payload."""
    @property
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
    @staticmethod
    def idle():
        """
        Command the bound unit to remain idle.
        """
    @staticmethod
    def stop():
        """
        Command the bound unit to stop.
        """
    @staticmethod
    def move(x: int, y: int):
        """
        Command the bound unit to move to the given coordinates.
        """
    @staticmethod
    def approach(x: int, y: int, radius: int):
        """
        Command the bound unit to approach the given coordinates, around a desired radius.
        """
    @staticmethod
    def within(x: int, y: int, radius: int):
        """
        Return true if the bound unit is within the radius around the specified coordinates.
        """
    @staticmethod
    def boost(amount: int):
        """
        Enable or disable the boost of the bound unit. The amount of boost is either 0 to disable or 1 to enable.
        """
    @staticmethod
    def pathfind():
        """
        Command the bound unit to pathfind to the enemy core.
        """
    @staticmethod
    def shoot(self, x: int = None, y: int = None):  # target
        """
        Command the unit to shoot to the specified coordinates. Won't do anything if the coordinates are out of reach.

        If no coordinates are given, the unit will shoot at its feet (useful for units such as horizon which drop bombs).
        Note that horizon must be in movement for it to shoot.
        """
    @staticmethod
    def target(self, x: int = None, y: int = None, shoot: bool = False):  # target
        """
        Command the unit to target (rotate to) the specified coordinates.
        If shoot is set to `True`, it will behave same as `shoot(x, y)`.
        """
    @staticmethod
    def target_unit(self, unit, shoot: bool = True):  # targetp
        """
        Command the unit to target another unit with velocity prediction.
        If shoot is set to `True`, the bound unit will shoot as well.
        """
    @staticmethod
    def ceasefire(self):  # target
        """
        Command the unit to stop firing immediately.
        """
    @staticmethod
    def fetch(container, item, amount=1):  # itemTake
        """
        Command the unit to fetch (take out) an item from the specified container.
        """
    @staticmethod
    def store(container, amount=1):  # itemDrop
        """
        Command the unit to store (put) an item into the specified container.
        """
    @staticmethod
    def lift():  # payTake with takeUnits 0
        """
        Command the unit to lift a block.
        """
    @staticmethod
    def carry():  # payTake with takeUnits 1
        """
        Command the unit to lift a unit (or block if there is no unit).
        """
    @staticmethod
    def drop():  # payDrop
        """
        Command the unit to drop the currently-held payload (a block or unit).
        """
    @staticmethod
    def mine(x, y):
        """
        Command the unit to mine at the specified coordinates.
        """
    @property
    def flag():
        """
        Store a user-provided number in the unit for later use (for example, to "flag" this unit already was used).
        """
    @staticmethod
    def locate(team: str, *, building=None, ore=None, spawn=None, damaged=None):
        """
        Locate an `'ally'` or '`enemy`' structure near the bound unit.

        The return value accomodates to the left-hand side as follows:

        found, = Unit.locate('ally', building='core')  # was the ally core found?
        #    ^ this comma is important! locate always returns a tuple and we need to unpack it

        found, x = Unit.locate('enemy', building='core')  # the x coordinate of the enemy core if found
        found, x, y = Unit.locate('enemy', building='core')  # the x and y coordinate of the enemy core if found
        found, x, y, building = Unit.locate('enemy', building='core')  # the x and y coordinate of the enemy core if found, and specific building type

        Exactly one keyword argument is allowed.

        Building can be any literal of: core, storage, generator, turret, factory, repair, rally (command center), battery, resupply, reactor.
        Ore can be one of those in `Env` or in a variable.
        Both spawn and damaged can only be set to `True`.
        """

Unit = Unit()

class Mem:
    """
    Access to memory.

    Note that `cell1` is used for function calls (but is unused otherwise).
    """

def print(message: str, flush: Union[bool, str] = True):
    """
    Print a message. f-strings are supported and encouraged to do string formatting.

    `flush` may be a boolean indicating whether to emit `printflush` or not, or the name of the message.
    """

def sleep(ms: int):
    """
    Sleep for the given amount of milliseconds.

    This is a processor-independant way of delaying execution for an exact amount of time.
    """

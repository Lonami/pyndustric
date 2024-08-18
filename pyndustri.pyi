from abc import ABC
from typing import Iterator

class Link:
    """Represents a link."""

    def __getitem__(self, n) -> Building | None:
        """Gets the nth link"""

class Content:
    """A fundemental resource identifier"""

class Env:
    """
    Access to special environmental variables.
    """

    copper: Content
    lead: Content
    metaglass: Content
    graphite: Content
    sand: Content
    coal: Content
    titanium: Content
    thorium: Content
    scrap: Content
    silicon: Content
    plastanium: Content
    phase_fabric: Content
    surge_alloy: Content
    spore_pod: Content
    blast_compound: Content
    pyratite: Content
    beryllium: Content
    tungsten: Content
    oxide: Content
    carbide: Content

    water: Content
    slag: Content
    oil: Content
    cryofluid: Content
    neoplasm: Content
    arkycite: Content
    ozone: Content
    hydrogen: Content
    nitrogen: Content
    cyanogen: Content

    null: None

    @property
    def this(self) -> Building:
        """Return the `Building` object representing this logic processor."""
    @property
    def x(self) -> int:
        """Return the `x` coordinate where `this` is located."""
    @property
    def y(self) -> int:
        """Return the `y` coordinate where `this` is located."""
    @property
    def counter(self) -> int:
        """
        Return the Program Counter (also known as Instruction Pointer).

        The value is a number representing the index of the *next* instruction.
        """
    @staticmethod
    def links() -> Iterator[Link]:
        """Used to iterate over all the links."""
    @property
    def link_count(self) -> int:
        """Return how many links there are connected to `this` logic processor."""
    @property
    def time(self) -> float:
        """Return the current UNIX timestamp, in milliseconds."""
    @property
    def width(self) -> int:
        """Return the width of the entire map, in tiles."""
    @property
    def height(self) -> int:
        """Return the height of the entire map, in tiles."""
    @property
    def ips(self) -> float:
        # https://github.com/Anuken/Mindustry/blob/b7f030eb1342fc4fd7c46274bfa9ed7af25f5829/core/src/mindustry/world/blocks/logic/LogicBlock.java#L128
        """Return the amount of instructions per second this processor is capable of executing."""
    def __getattr__(self, name) -> Content:
        """
        Return an arbitrary `@variable`.

        For example, `Env.titanium` can be used to refer to Mindustry's `@titanium`.
        Underscores become dashes (e.g. `Env.titanium_conveyor` becomes `@titanium-conveyor`).
        """

class World:
    """
    World processor specific items
    """

    class blocks:
        @staticmethod
        def count(type: str, team: str) -> int:
            """
            Get the block count of type type (eg "Env.conveyor").
            Type can also be "core"
            """
        @staticmethod
        def index(type: str, team: str, index: int) -> Content:
            """
            Get the block of type type (eg "Env.conveyor") at index index.
            Type can also be "core"
            """
        @staticmethod
        def set(ore: str, floor: str, block: str, block_team: str, block_rotation: int = 0):
            """
            Sets the block.
            Usage: World.blocks[x][y].set(ore=Env.titanium_ore)
            """
        @staticmethod
        def get_block() -> Senseable:
            """Get block. Usage: block = World.blocks[x][y].get_block()"""
        @staticmethod
        def get_build() -> Senseable:  # tbh not sure what the difference between a block and a building is
            """Get building. Usage: build = World.blocks[x][y].get_build()"""
        @staticmethod
        def get_ore() -> Content:
            """Get ore. Usage: ore = World.blocks[x][y].get_ore()"""
        @staticmethod
        def get_floor() -> Content:
            """Get floor. Usage: floor = World.blocks[x][y].get_floor()"""
    @staticmethod
    def fetch_player(team: str, index: int):
        """Fetches the player at a certain index."""
    @staticmethod
    def fetch_unit(team: str, index: int):
        """Fetches the unit at a certain index."""
    @staticmethod
    def unit_count(team: str) -> int:  # could change this to Teams.sharded.units() hmm
        """Get the unit (all types) count of a team."""
    @staticmethod
    def player_count(team: str) -> int:
        """Get the player count of a team."""
    @staticmethod
    def spawn_unit(type: str, x: int, y: int, team: str, rot: int):
        """Spawns a unit at (x, y), then returns it."""
    @staticmethod
    def spawn_natural_wave():
        """Spawns the next wave set by the map at a spawn point i think????"""
    @staticmethod
    def spawn_wave(x: int, y: int):
        """Spawns the next wave set by the map at (x, y) (?)"""
    @staticmethod
    def apply_status(unit: Unit, status: str, length: float):
        """Applys a status to a unit for a certain length"""
    @staticmethod
    def clear_status(unit: Unit, status: str):
        """Clear status from unit"""
    @staticmethod
    def set_rate(ipt: int):
        """Sets the instructions per tick for this processor (note, uses ticks instead of seconds (1 tick = 1/60))"""
    @staticmethod
    def camera_pan(x: int, y: int, speed: float):
        """
        Pan the player camera
        """
    @staticmethod
    def camera_zoom(level: float):
        """
        Zoom the player camera
        """
    @staticmethod
    def camera_stop():
        """
        Stops any camera efects
        """
    @staticmethod
    def create_explosion(
        team: str,
        x: int,
        y: int,
        radius: float,
        damage: float,
        hits_air: bool = True,
        hits_ground: bool = True,
        piercing: bool = False,
    ):
        """
        Cause a explosion. hits_air, hits_ground and piercing are kwargs.
        """
    @staticmethod
    def set_flag(ident: str):
        """Sets a flag that is globally acessible (via get_flag) from all world processors"""
    @staticmethod
    def unset_flag(ident: str):
        """Unsets a flag previously set by set_flag"""
    @staticmethod
    def get_flag(ident: str) -> bool:
        """Checks if a flag is set (set flag via set_flag)"""

Env = Env()

# https://github.com/Anuken/Mindustry/blob/e714d44/core/assets/bundles/bundle.properties#L979-L998
# https://github.com/Anuken/Mindustry/blob/8bc349b/core/src/mindustry/logic/LAccess.java#L6-L47

class Senseable(ABC):
    """
    Type hints for things that can be sensed.
    """

    @property
    def copper(self) -> int:
        """The amount of copper stored or carried by the link"""
    @property
    def lead(self) -> int:
        """The amount of lead stored or carried by the link"""
    @property
    def metaglass(self) -> int:
        """The amount of metaglass stored or carried by the link"""
    @property
    def graphite(self) -> int:
        """The amount of graphite stored or carried by the link"""
    @property
    def sand(self) -> int:
        """The amount of sand stored or carried by the link"""
    @property
    def coal(self) -> int:
        """The amount of coal stored or carried by the link"""
    @property
    def titanium(self) -> int:
        """The amount of titanium stored or carried by the link"""
    @property
    def thorium(self) -> int:
        """The amount of thorium stored or carried by the link"""
    @property
    def scrap(self) -> int:
        """The amount of scrap stored or carried by the link"""
    @property
    def silicon(self) -> int:
        """The amount of silicon stored or carried by the link"""
    @property
    def plastanium(self) -> int:
        """The amount of plastanium stored or carried by the link"""
    @property
    def phase_fabric(self) -> int:
        """The amount of phase_fabric stored or carried by the link"""
    @property
    def surge_alloy(self) -> int:
        """The amount of surge_alloy stored or carried by the link"""
    @property
    def spore_pod(self) -> int:
        """The amount of spore_pod stored or carried by the link"""
    @property
    def blast_compound(self) -> int:
        """The amount of blast_compound stored or carried by the link"""
    @property
    def pyratite(self) -> int:
        """The amount of pyratite stored or carried by the link"""
    @property
    def beryllium(self) -> int:
        """The amount of beryllium stored or carried by the link"""
    @property
    def tungsten(self) -> int:
        """The amount of tungsten stored or carried by the link"""
    @property
    def oxide(self) -> int:
        """The amount of oxide stored or carried by the link"""
    @property
    def carbide(self) -> int:
        """The amount of carbide stored or carried by the link"""
    @property
    def water(self) -> int:
        """The amount of water stored or carried by the link"""
    @property
    def slag(self) -> int:
        """The amount of slag stored or carried by the link"""
    @property
    def oil(self) -> int:
        """The amount of oil stored or carried by the link"""
    @property
    def cryofluid(self) -> int:
        """The amount of cryofluid stored or carried by the link"""
    @property
    def neoplasm(self) -> int:
        """The amount of neoplasm stored or carried by the link"""
    @property
    def arkycite(self) -> int:
        """The amount of arkycite stored or carried by the link"""
    @property
    def ozone(self) -> int:
        """The amount of ozone stored or carried by the link"""
    @property
    def hydrogen(self) -> int:
        """The amount of hydrogen stored or carried by the link"""
    @property
    def nitrogen(self) -> int:
        """The amount of nitrogen stored or carried by the link"""
    @property
    def cyanogen(self) -> int:
        """The amount of cyanogen stored or carried by the link"""
    @property
    def items(self) -> int:
        """The sum of all items contained or carried by the link."""
    @property
    def first_item(self) -> Link | None:
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
    def id(self) -> int:
        """The ID of a unit/block/item/liquid. The inverse of the lookup operation."""
    @property
    def enabled(self) -> bool:
        """Is this link enabled?"""
    @property
    def color(self):
        """Illuminator color."""

class Controllable(ABC):
    """
    Type hints for things that can be controlled.
    """

    @staticmethod
    def enabled(enabled: bool):
        """Sets the link enabled or disabled, based on the given value."""
    @staticmethod
    def shoot(x: int, y: int, enabled: bool = True):
        """Sets the link to shoot or not, and if shooting, the position."""
    @staticmethod
    def ceasefire():
        """Shorthand to stop firing."""
    @staticmethod
    def color():
        """Control color of an illuminator"""
    @staticmethod
    def config(config: Content = None):
        """Configure this block. config = eg Env.titanium for sorter1"""

class Building(ABC, Senseable, Controllable):
    pass

class UnitType(ABC, Senseable, Controllable):
    pass

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
    def image(x: int, y: int, image: Content, size: int, rotation: int = 0):
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

    This should be used as a singleton. It is also senseable (you can use `Unit.x`, etc.).
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
    def within(x: int, y: int, radius: int) -> bool:
        """
        Return true if the bound unit is within the radius around the specified coordinates.
        """
    @staticmethod
    def boost(enabled: bool):
        """
        Enable or disable the boost of the bound unit. The amount of boost is either 0 to disable or 1 to enable.
        """
    @staticmethod
    def pathfind(x: int, y: int):
        """
        Command the bound unit to pathfind to the x and y coordinates.
        """
    @staticmethod
    def shoot(x: int = None, y: int = None):  # target
        """
        Command the unit to shoot to the specified coordinates. Won't do anything if the coordinates are out of reach.

        If no coordinates are given, the unit will shoot at its feet (useful for units such as horizon which drop bombs).
        Note that horizon must be in movement for it to shoot.
        """
    @staticmethod
    def target(x: int = None, y: int = None, shoot: bool = False):  # target
        """
        Command the unit to target (rotate to) the specified coordinates.
        If shoot is set to `True`, it will behave same as `shoot(x, y)`.
        """
    @staticmethod
    def target_unit(unit, shoot: bool = True):  # targetp
        """
        Command the unit to target another unit with velocity prediction.
        If shoot is set to `True`, the bound unit will shoot as well.
        """
    @staticmethod
    def ceasefire():  # target
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
    def flag(self) -> int:
        """
        Store a user-provided number in the unit for later use (for example, to "flag" this unit already was used).
        """
    @staticmethod
    def locate(
        team: str,
        *,
        building: Content = None,
        ore: Content = None,
        spawn: bool = None,
        damaged: bool = None,
    ) -> tuple[bool, int, int, Building | None]:
        """
        Locate an `'ally'` or '`enemy`' structure near the bound unit.

        The return value accomodates to the left-hand side as follows:

        found, = Unit.locate('ally', building='core')  # was the ally core found?
        #    ^ this comma is important! locate always returns a tuple and we need to unpack it

        found, x = Unit.locate('enemy', building='core')  # the x coordinate of the enemy core if found
        found, x, y = Unit.locate('enemy', building='core')  # the x and y coordinate of the enemy core if found
        found, x, y, building = Unit.locate('enemy', building='core')  # the x and y coordinate of the enemy core if found, and specific building

        Exactly one keyword argument is allowed.

        Building can be any literal of: core, storage, generator, turret, factory, repair, rally (command center), battery, resupply, reactor.
        Ore can be one of those in `Env` or in a variable.
        Both spawn and damaged can only be set to `True`.
        """
    @staticmethod
    def build(x: int, y: int, block_type: Content, rotation=0, config=0):  # build
        """
        Build a block at position `(x, y)` with rotation (0, 1, 2 or 3, the values indicating the number of 90º counter-clockwise steps).
        For example, conveyors start facing east with a rotation of 0, north with 1, west with 2, and south with 3.

        Block represents the type of the block (e.g. Env.router, Env.sorter...).
        Config is configuration for block (e.g. Env.titanium for Env.sorter).
        You can pass another block variable as config to copy the configuration of that block.
        """
    @staticmethod
    def get_block(x, y) -> Building:  # getBlock
        """
        Return the building and optionally its type located at `(x, y)`:

        building, = get_block(x, y)
        building, building_type = get_block(x, y)

        The building type can then be used as the `block_type` in `build()` and building may be used as the `config`.
        """
    @staticmethod
    def unbind():
        """
        Unbinds the currently bound unit
        """
    @staticmethod
    def radar(*args, order=max, key="distance") -> UnitType | None:
        """Locate units around the currently bound unit"""

Unit = Unit()

class Mem:
    """
    Access to memory.

    Note that `cell1` is used for function calls (but is unused otherwise).
    """

def print(message: str, flush: bool | str = True, time: float = 0.0):
    """
    Print a message. f-strings are supported and encouraged to do string formatting.

    Note `flush` must be specified as a keyword arg.
    `flush` may be a boolean indicating whether to emit `printflush` or not, or the name of the message.

    For world procesors,
    Flush can be:
    - `notify`:
        Puts the print buffer on the top of the screen with a fancy panel.
    - `announce`:
        Puts the print buffer in the center of the screen for a certain amount of time.
        Set time with `print(flush='announce', time=3.0)`.
    - `toast`:
        Puts the print buffer slightly lower than the top of the screen with no fancy panel
        Set time as with announce.
    - `mission`:
        Changes the "mission" from Wave 1... waiting (etc) to the print buffer
    """

def sleep(secs: float):
    """
    Sleep for the given amount of seconds.
    """

def flip(a: int) -> int:
    """Bitwise complement"""

def max(a: float, b: float) -> float:
    """Maximum of 2 numbers"""

def min(a: float, b: float) -> float:
    """Minimum of 2 numbers"""

def xor(a: int, b: int) -> int:
    """Bitwise XOR"""

def atan2(a: float, b: float) -> float:
    """Arc tangent, in degrees"""

def noise(a: float, b: float) -> float:
    """2D simplex noise"""

def abs(a: float) -> float:
    """Absolute Value"""

def len(a) -> float:
    """The magnitude of a vector"""

def log(a: float) -> float:
    """Natural Logarithm"""

def log10(a: float) -> float:
    """Base 10 logarithm"""

def sin(a: float) -> float:
    """Sine, in degrees"""

def cos(a: float) -> float:
    """Cosine, in degrees"""

def tan(a: float) -> float:
    """Tangent, in degrees"""

def floor(a: float) -> float:
    """Round down"""

def ceil(a: float) -> float:
    """Round up"""

def sqrt(a: float) -> float:
    """Square root"""

def rand(range: float) -> float:
    """Random decimal in range [0, range)"""

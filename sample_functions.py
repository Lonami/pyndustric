# These are sample functions, written in Python, whose contents can be compiled to mindustry mlog code.
# TODO not all of these are compilable yet, but the goal is to make them be!

# For debugging purposes, e.g., in PyCharm, it will be useful to declare arguments to the function
# corresponding to whatever mindustry blocks you expect to be linked to the processor running this code.
# These should typically be annotated as type Block.


# TODO  The following should eventually be moved to a separate file (pyndustry.pyi) and imported


class Vector:
    """A Vector is a very general superclass that is used to represent anything that has .x and .y coordinates,
    including Mindustry blocks, Mindustry units, and variables that are used to represent x,y coordinates.
    You can access any vector V's .x and .y components with V.x and V.y, though it will often be more convenient to
    use vectorized operations that operate on .x and .y together, just like vectorized operations on NumPy arrays.
    E.g., adding Vector(x1,y1) + Vector(x2,y2) yields Vector(x1+x2,y1+y2).  When a scalar is mathematically combined
    with a Vector, as in Vector(x1,y1)*2, that scalar is "broadcast" NumPy-style to interact with each component of
    the vector, yielding Vector(x1*2, y1*2). In Pyndustric, Vectors are the default arguments to give for any mlog
    function or operation that requires x and y components, e.g. dst( V ) returns the distance (or magnitude) of
    vector V, and Unit.move_to( V ) directs the currently bound Unit to approach the location specified by vector V.
    Pyndustric automatically interprets any list [x,y] as Vector(x,y) (since Mindustry's mlog does not provide
    any native operations involving lists)."""

    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def __add__(self, other: float | list | "Vector") -> "Vector":
        """This would be called whenever someone tries to add a vector + something else.  If a vector is added
        to another vector or to a two-element list, the x-components and y-components are added separately.
        If a vector is added to a scalar, the scalar is added to each component."""

    def __radd__(self, other: float | list | "Vector") -> "Vector":
        """This would be called whenever someone tries to something else + a vector.  If a vector is added
        to another vector or to a two-element list, the x-components and y-components are added separately.
        If a vector is added to a scalar, the scalar is added to each component."""

    def __sub__(self, other: float | list | "Vector") -> "Vector":
        """This would be called whenever someone tries to subtract a vector - something else.  If other is
        another vector or to a two-element list, the x-components and y-components are subtracted separately.
        If the other is a scalar, the scalar is subtracted from each component."""

    def __rsub__(self, other: float | list | "Vector") -> "Vector":
        """This would be called whenever someone tries to subtract something else - a vector.  If other is
        another vector or to a two-element list, the x-components and y-components are subtracted separately.
        If the other is a scalar, each component is subtracted from that scalar."""

    # TODO include dummy interface definitions for other vectorized overloaded operations


class SensableAttribute:
    """This is an attribute of some unit/block that can be read by an mlog sensor.
    In Pyndustric these can be referred to via object.attribute, e.g. vault1.copper or Unit.shooting.
    In Pyndustric, SensableAttribute names mirror those in Mindustry mlog, *except* Python does not
    use the leading @, and hyphens are transformed to underscores, e.g., @phase-fabric becomes .phase_fabric"""


class SensableObject(Vector):
    """This umbrella class can represent any block or unit that mlog sensor instructions can read attributes from.
    This is a subclass of Vector since all such objects have x,y locations that can participate in vectorized
    computations.  In Pyndustric, attributes of a SensableObject may be accessed as .attributes,
    e.g., vault1.copper or Unit.shooting"""

    # TODO determine if any of the following attributes are unit-only or block-only, and if so move to subclass
    copper: SensableAttribute  #  '@copper',
    lead: SensableAttribute  #  '@lead',
    coal: SensableAttribute  #  '@coal',
    graphite: SensableAttribute  #  '@graphite',
    titanium: SensableAttribute  #  '@titanium',
    thorium: SensableAttribute  #  '@thorium',
    silicon: SensableAttribute  #  '@silicon',
    plastanium: SensableAttribute  #  '@plastanium',
    phase_fabric: SensableAttribute  #  '@phase-fabric',
    surge_alloy: SensableAttribute  #  '@surge-alloy',
    spore_pod: SensableAttribute  #  '@spore-pod',
    sand: SensableAttribute  #  '@sand',
    blast_compound: SensableAttribute  #  '@blast-compound',
    pyratite: SensableAttribute  #  '@pyratite',
    metaglass: SensableAttribute  #  '@metaglass',
    scrap: SensableAttribute  #  '@scrap',
    water: SensableAttribute  #  '@water',
    slag: SensableAttribute  #  '@slag',
    oil: SensableAttribute  #  '@oil',
    cryofluid: SensableAttribute  #  '@cryofluid',
    totalItems: SensableAttribute  #  '@totalItems',
    firstItem: SensableAttribute  #  '@firstItem',
    totalLiquids: SensableAttribute  #  '@totalLiquids',
    totalPower: SensableAttribute  #  '@totalPower',
    itemCapacity: SensableAttribute  #  '@itemCapacity',
    liquidCapacity: SensableAttribute  #  '@liquidCapacity',
    powerCapacity: SensableAttribute  #  '@powerCapacity',
    powerNetStored: SensableAttribute  #  '@powerNetStored',
    powerNetCapacity: SensableAttribute  #  '@powerNetCapacity',
    powerNetIn: SensableAttribute  #  '@powerNetIn',
    powerNetOut: SensableAttribute  #  '@powerNetOut',
    ammo: SensableAttribute  #  '@ammo',
    ammoCapacity: SensableAttribute  #  '@ammoCapacity',
    health: SensableAttribute  #  '@health',
    maxHealth: SensableAttribute  #  '@maxHealth',
    heat: SensableAttribute  #  '@heat',
    efficiency: SensableAttribute  #  '@efficiency',
    rotation: SensableAttribute  #  '@rotation',
    x: SensableAttribute  #  '@x',   # should vectorize!
    y: SensableAttribute  #  '@y',
    shootX: SensableAttribute  #  '@shootX',   # should vectorize!
    shootY: SensableAttribute  #  '@shootY',
    shooting: SensableAttribute  #  '@shooting',
    mineX: SensableAttribute  #  '@mineX', # should vectorize!
    mineY: SensableAttribute  #  '@mineY',
    mining: SensableAttribute  #  '@mining',
    team: SensableAttribute  #  '@team',
    type: SensableAttribute  #  '@type',
    flag: SensableAttribute  #  '@flag',
    controlled: SensableAttribute  #  '@controlled',
    commanded: SensableAttribute  #  '@commanded',
    name: SensableAttribute  #  '@name',
    config: SensableAttribute  #  '@config',
    payload: SensableAttribute  #  '@payloadCount',
    payloadType: SensableAttribute  #  '@payloadType',
    enabled: SensableAttribute  #  '@enabled',  # could treat as settable property?

    pos: Vector  # [@x , @y]
    shootPos: Vector  # [@shootX, @shootY]
    minePos: Vector  # [@mineX, @mineY]


class UnitType(Vector):
    """This is used to represent any type of mindustry unit, e.g. manufactured units like mono or poly,
    or player-controlled units, like alpha, beta, or gamma.  A UnitType is used as an argument for
    Unit.bind_next( unittype ) to specify which type of unit you want the processor to bind/control."""


alpha = beta = gamma = flare = UnitType()
# TODO include remaining unit types


class AnyUnit(Vector):
    """This is used to represent any mindustry unit, e.g. the currently bound unit, called Unit, previously bound
    units which have been stored as the value of a variable, or units detected by radar.
    As a subclass of Vector, this automatically inherits .x and .y coordinates, and various vectorized operations
    that will operate on this unit's location"""

    # TODO include dummy interface definitions for various unit attributes


class BoundUnit(AnyUnit):
    """This is used to handle the mlog built-in variable @unit, which always represents the currently bound unit.
    Pyndustric compilable programs will typically refer to this as Unit.
    This is a subclass of AnyUnit and hence of Vector, so inherits the ability to refer to various attributes
    of the bound Unit, including its .x and .y coordinates (and allowing vectorized operations on those),
    and various other unit attributes.  In addition this subclass allows various methods for controlling the
    bound Unit."""

    def bind_next(self, unittype: UnitType):
        """In pyndustric, unit binding can be done with Unit.bind_next( unittype ).
        This binds this processor to the next friedly unit of unittype.  Subsequent references to 'Unit' will
        refer to this unit, until a new unit is bound.  If your program loops back up to bind another unit,
        (e.g., by concluding and starting over), a new unit will be bound on the next iteration, so eventually
        you will have gone through all the units of unittype and automatically start over with the first.
        If you don't want all units of this type to do the same thing, you'll need to either (a) not iterate through
        all the units, and/or (b) refrain from giving the same commands to all the units you do iterate through."""

    # TODO include dummy interface definitions for various methods for controlling bound Unit


Unit = BoundUnit()  # Pyndustric programs will refer mlog's @unit as Unit


class Block(SensableObject):
    """This represents a block located somewhere on the map, e.g., a turret, vault, memory processor, or conveyer belt.
    If your processor will be linked to blocks, like vault1 or ripple1, it is recommended that you declare these
    as arguments of type : Block for the function that you want to compile to be the mlog code for that processor.
    Blocks can also be found using TODO the following mlog functions
    In Pyndustric, attributes of a block may be accessed as .attributes,  e.g., vault1.copper"""

    def __getitem__(self, index):
        pass  # You can read a slot of a memory block, e.g., with memory1[0]

    def __setitem__(self, index, value):
        pass  # You can write to a slot of a memory block, e.g., with memory1[0]=1


# ------------------------


def dst(vector_or_x: float | list | Vector, y: float = None) -> float:
    """This built-in Mindustry mlog function computes the distance (or magnitude) along a 2D vector.
    In Pyndustric the argument can either be any Vector (including a unit or block) or separate
    specification of .x and .y components.  The distance between two objects, is the dst of their difference,
    e.g., the distance between the currently bound Unit and This processor is dst(Unit - This)."""


def label(name: str):
    """This marks a location in the code, so that jump commands can be used to move the point of execution here.
    This does not compile to an instruction, but instead is just is used to calculate which line-number
    should be used with jump commands."""


def jump(label: str):
    """This unconditionally jumps the flow of execution to the corresponding label, defined with label(name),
    using Mindustry's jump always command.  Be cautious using this with other flow-of-control mechanisms like
    functions or for or while loops. Mindustry's jump command allows conditional jumps (rather than jump always).
    To create conditional jumps in pyndustric, simply embed the jump command within a Python if statement, as this
    will compile to a mindustry conditional jump."""


# ------------------------------------------------------------


def findPlayer(memory1: MemoryBlock):
    """This compilable function finds the (or a) player and stores a reference to it in slot 1 of memory1.
    This is useful if other logic processors want to know where the player is, e.g., to direct units to
    follow the player."""
    Unit.bind_next(gamma)
    if Unit:
        jump("found it")
    Unit.bind_next(beta)
    if Unit:
        jump("found it")
    Unit.bind_next(alpha)
    label("found it")
    memory1[1] = Unit


def stayNearPlayer(memory1: MemoryBlock):
    """This compilable function goes through all units of the type specified at beginning of loop, checks if they are
    more than maxD away from the player. If so it controls them to approach to approachD from the player, otherwise
    lets them continue path-finding on their own.  This presumes a reference to the player is stored in memory1[1],
    e.g by another processor running findPlayer."""
    maxD = 25  # maximum distance units are allowed to depart from player
    approachD = 20  # target distance from player units are ordered to approach
    while True:
        Unit.bind_next(flare)
        player = memory1[1]
        if dst(Unit - player) > maxD:
            Unit.approach(player, approachD)
        else:
            Unit.pathfind()


def ammo_feeder(container1: Block, ripple1: Block):
    """This simple compilable function flags an unflagged flare and has it forever ferry ammo from container1 to ripple1."""
    while not (Unit and Unit.flag == 0):
        Unit.bind_next(flare)  # find a flare whose flag is 0
    Unit.flag = 1  # set its flag to 1, so other processors will know not to take control of it
    while Unit:  # so long as this unit survives...
        while dst(Unit - container1) > 5:
            Unit.move_to(container1)
        Unit.get_item(container1, graphite, 20)
        while dst(Unit - ripple1) > 5:
            Unit.move_to(ripple1)
        Unit.put_item(ripple1, graphite, 20)

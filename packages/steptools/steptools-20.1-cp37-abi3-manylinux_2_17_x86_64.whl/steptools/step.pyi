# 
# Copyright (c) 1991-2023 by STEP Tools Inc.
# All Rights Reserved
# 
# Author: David Loffredo (loffredo@steptools.com)
# 
# Stub file for typing and intellisense documentation.  Unfortunately,
# since our step native extension has one file, these definitions must
# follow that pattern and can not be split into more managable chunks.
#
# Also, be aware that there can be no tool tips for the EXPRESS or ARM
# attributes because those are made available at run time based on the
# underlying step data, and the IDEs seem to only use the static type
# files, not anything at runtime.

from typing import overload, Set, List, Union, Optional, Sequence, Callable
from enum import IntEnum

from _typeshed import (
    StrOrBytesPath
    )

# ==================================================
# MODULE FUNCTIONS
#
def keystone() -> Design:
    '''
    Return keystone schema design, initializes library.
    '''
    pass

@overload    
def verbose() -> bool: ...
@overload    
def verbose(yn: bool) -> None:
    '''Get or set verbose flag'''
    pass

def find_design(filename: StrOrBytesPath) -> Design:
    '''
    Read STEP file into memory, return design object.
    '''
    pass

def type(obj: Object) -> str:
    '''
    Returns the AIM (EXPRESS) typename of an object.
    '''
    pass

def aim_type(obj: Object) -> str:
    '''
    Return the AIM (EXPRESS) type of an object.
    '''
    pass

def arm_type(obj: Object) -> str:
    '''
    Return the ARM typename of an object.
    '''
    pass

def arm(obj: Object) -> ArmObject:
    '''
    Return the ARM object, if any, for a STEP data object.
    '''
    pass

def arm_recognize(obj: Design) -> int:
    '''
    Recognize ARM objects in STEP data set, return count of ARM objects found.
    '''
    pass


def isinstance(obj: Object, typename: str) -> bool:
    '''
    Is object an instance of EXPRESS type.
    '''
    pass

@overload    
def schema_type(d: Design) -> SchemaType: ...
@overload    
def schema_type(d: Design, schema: SchemaType) -> None:
    '''Get or set design schema type enum'''
    pass

@overload    
def schema_name(d: Design) -> str: ...
@overload    
def schema_name(d: Design, name: str) -> None:
    '''Get or set design schema type name string'''
    pass



class SchemaType(IntEnum,auto):
    '''
    Identifies the STEP protocol that is declared in the header of an
    exchange file.
    '''
    NONE = auto()
    AP203 = auto()
    AP203E2 = auto()
    AP214 = auto()
    AP224 = auto()
    AP232 = auto()
    AP238 = auto()
    AP238E2 = auto()
    AP240 = auto()
    AP242 = auto()
    OTHER = auto()


# ==================================================
# STEP OBJECT CLASS
#
class Object:
    '''
    STEP data object class.  All ARM and EXPRESS AIM attributes in the
    underlying STEP data are automatically available.

    '''
    @overload    
    def entity_id(self) -> int: ...
    @overload    
    def entity_id(self, id: int) -> None:
        '''Get or set exchange file entity id #123'''
        pass

    def keys(self) -> Set[str]:
        '''Get STEP ARM and AIM object attribute keys'''
        pass
    
    def aim(self) -> AimView:
        '''STEP AIM object view'''
        pass


# ==================================================
# STEP DESIGN CLASS
#
class Design:
    '''
    Class containing all data from a STEP exchange file.
    '''
    @overload    
    def name(self) -> str: ...
    @overload    
    def name(self, nm: StrOrBytesPath) -> None:
        '''Get or set design name'''
        pass

    @overload    
    def path(self) -> str: ...
    @overload    
    def path(self, nm: StrOrBytesPath) -> None:
        '''Get or set design file path'''
        pass
    
    def header_name(self) -> Object:
        '''Get header name object'''
        pass

    def header_description(self) -> Object:
        '''Get header description object'''
        pass

    def find(self, id: str | int) -> Object:
        '''Find an object by ANCHOR name or #123 entity id'''
        pass

    def keys() -> Set[str]:
        '''Design name table keys'''
        pass


class DesignCursor(Iterator[Object]):
    '''
    Iterator over the STEP AIM instances in a design.

    '''
    def __init__(self, d: Design, typename: str = 'RoseStructure' ):
        '''
        Cursor over all instances of a given typename in a design object.
        Looks at all entity instances by default

        '''
        pass
    
    def __next__(self) -> Object:
        '''
        Return next STEP object in the design.

        '''
        pass

    def __iter__(self) -> 'DesignCursor': ...


# ==================================================
# AIM and ARM CLASSES
#
    
class AimView:
    '''
    STEP AIM data object view class.  All EXPRESS AIM attributes in the
    underlying STEP data are automatically available.

    '''
    @overload    
    def entity_id(self) -> int: ...
    @overload    
    def entity_id(self, id: int) -> None:
        '''Get or set exchange file entity id #123'''
        pass

    def keys(self) -> Set[str]:
        '''Get AIM object attribute keys'''
        pass


class ArmObject:
    '''
    STEP ARM data object view class.  All ARM attributes in the
    underlying STEP data are automatically available.

    '''
    def root(self) -> Object:
        '''Get ARM root object'''
        pass
    def keys(self) -> Set[str]:
        '''Get ARM object attribute keys'''
        pass


# ==================================================
# ADAPTIVE PROCESS CURSOR CLASS
#
# 
class RoseUnit(IntEnum,auto):
    '''Enumeration that identifies common units'''
    UNKNOWN = auto()
    AS_IS = auto()
    
    MM = auto()
    CM = auto()
    M = auto()
    IN = auto()
    FT = auto()
    MICROMETRE = auto()
    NANOMETRE = auto()
    MILLIINCH = auto()
    MICROINCH = auto()
    
    MM2 = auto()
    CM2 = auto()
    M2 = auto()
    IN2 = auto()
    FT2 = auto()
    
    MM3 = auto()
    CM3 = auto()
    M3 = auto()
    IN3 = auto()
    FT3 = auto()
    
    DEG = auto()
    RAD = auto()
    
    STERADIAN = auto()

    SEC = auto()
    MIN = auto()
    HOUR = auto()

    MMPS = auto()
    MMPM = auto()
    CMPS = auto()
    MPS = auto()
    IPS = auto()
    IPM = auto()
    FPS = auto()
    FPM = auto()

    MMPREV = auto()
    IPREV = auto()
    MMPTOOTH = auto()
    IPTOOTH = auto()

    HERTZ = auto()
    RPM = auto()

    PA = auto()
    KPA = auto()
    MPA = auto()
    PSI = auto()

    NEWTON = auto()
    LBF = auto()

    WATT = auto()
    KW = auto()
    HP = auto()

    NEWTON_METER = auto()
    POUND_FOOT = auto()

    CELSIUS = auto()
    KELVIN = auto()
    FAHRENHEIT = auto()
    RANKINE = auto()

    COUNT = auto()
    PARAMETER = auto()
    RATIO = auto()
    REVOLUTION = auto()
    TOOTH = auto()

    MAX_VALUE = AUTO()
    def fullname(self) -> str:
        '''Return full descriptive name of unit enum''' 
        pass

    @classmethod
    def find(cls, name:str) -> 'RoseUnit':
        '''Return unit enum for full or abbreviated name'''
        pass


class CtlEvent(IntEnum,auto):
    '''
    Identifies the different process conditions (Tool move,
    workingstep change, etc) encountered by the cursor

    '''
    DONE = auto()
    ERROR = auto()
    MOVE = auto()
    TOOL_CHANGE = auto()
    PROJECT_START = auto()
    PROJECT_END = auto()
    SETUP_START = auto()
    SETUP_END = auto()
    EXEC_WORKPLAN_START = auto()
    EXEC_WORKPLAN_NEXT = auto()
    EXEC_WORKPLAN_END = auto()
    EXEC_SELECT_START = auto()
    EXEC_SELECT_NEXT = auto()
    EXEC_SELECT_END = auto()
    EXEC_WORKSTEP_START = auto()
    EXEC_WORKSTEP_END = auto()
    EXEC_OTHER_START = auto()
    EXEC_OTHER_END = auto()
    EXEC_NCFUN = auto()
    OPERATION_START = auto()
    OPERATION_NEXTPATH = auto()
    OPERATION_END = auto()
    TOOLPATH_START = auto()
    TOOLPATH_END = auto()
    CURVE_START = auto()
    CURVE_END = auto()
    DWELL = auto()
    LAST_EVENT = auto()


class CtlType(IntEnum,auto):
    '''
    Identifies the different kinds of STEP-NC elements that can appear
    on the process stack.

    '''
    UNKNOWN = auto()
    PROJECT = auto()
    EXEC = auto()
    EXEC_ASSIGN = auto()
    EXEC_IF = auto()
    EXEC_NONSEQ = auto()
    EXEC_PARALLEL = auto()
    EXEC_SELECT = auto()
    EXEC_WHILE = auto()
    EXEC_WORKPLAN = auto()
    EXEC_WORKSTEP = auto()
    EXEC_NCFUN = auto()
    EXEC_OP_COMBO = auto()
    
    OP = auto()
    OP_MILL = auto()
    OP_TURN = auto()
    OP_DRILL = auto()
    OP_BORE = auto()
    OP_BACK_BORE = auto()
    OP_TAP = auto()
    OP_RAPID = auto()
    
    OP_PROBE = auto()
    OP_PROBE_COMPLETE = auto()
    OP_PROBE_TLEN = auto()
    OP_PROBE_TRAD = auto()
    
    TP = auto()
    TP_FEEDSTOP = auto()
    TP_CUTLOC = auto()
    TP_CUTCON = auto()
    TP_AXIS = auto()
    TP_ANGLE = auto()
    TP_TAN = auto()
    TP_CONSEC = auto()
    TP_CONDIR = auto()

    CURVE = auto()

    MOVE = auto()
    MOVE_ARC = auto()
    MOVE_HELIX = auto()
    LAST_TYPE = auto()

class CtlPosType(IntEnum,auto):
    '''
    Identifies the different kinds of position information at a given
    point in the process.

    '''
    END = auto()
    START = auto()
    ARC = auto()
    VIA1 = auto()
    VIA2 = auto()
    PROBE = auto()
    RETRACT = auto()


class CtlCsys(IntEnum,auto):
    '''
    Identifies the coordinate system associated with a position
    '''
    WCS = auto()
    PART = auto()
    RAW = auto()

    
class CtlStatus(IntEnum,auto):
    '''
    Identifies the low-level state of each stack frame as you advance
    through the process.

    '''
    UNSEEN = auto()
    START = auto()
    START_BODY = auto()
    START_STEP = auto()
    WORKING = auto()
    END_STEP = auto()
    END_BODY = auto()
    END = auto()
    ERROR = auto()


    
class Adaptive:
    '''
    Cursor to iterate through STEP-NC process and pause at events
    '''
    def error_msg(self) -> str:
        '''Return error message for ERROR event'''
        pass
    
    def next(self) -> CtlEvent:
        '''Move forward in the process and return the next event'''
        pass
    
    def event(self) -> CtlEvent:
        '''Return the event at the current location in the process'''
        pass

    def reset(self) -> None:
        '''Reset the adaptive cursor, call start_project() to begin again'''
        pass

    def start_project(self, d: Design) -> None:
        '''Start traversal over machining project in design'''
        pass

    def start_exec(self, mpe: Object) -> None:
        '''Start traversal over individual machining_process_executable object'''
        pass

    def set_visit_all_execs(self, yn: bool) -> None:
        '''Force traversal over all execs, not just enabled ones'''
        pass

    def get_visit_all_execs(self) -> bool:
        '''Will traversal visit all execs or just enabled ones'''
        pass

    def set_wanted_all(self, yn: bool = True) -> None:
        '''Set all events as wanted or not'''
        pass

    def set_wanted(self, event: CtlEvent, yn: bool = True) -> None:
        '''Set an individual event as wanted or not'''
        pass
    
    def get_wanted(self, event: CtlEvent) -> bool:
        '''Return whether an individual event as wanted or not'''
        pass

    
    def get_active_project(self) -> Object:
        '''Get project for current process'''
        pass
    def get_active_exec(self) -> Object:
        '''Get executable at current process location'''
        pass
    def get_active_workplan(self) -> Object:
        '''Get workplan at current process location'''
        pass
    def get_active_workingstep(self) -> Object:
        '''Get workingstep at current process location'''
        pass
    def get_active_feature(self) -> Object:
        '''Get feature at current process location'''
        pass
    def get_active_operation(self) -> Object:
        '''Get operation at current process location'''
        pass
    def get_active_toolpath(self) -> Object:
        '''Get toolpath at current process location'''
        pass
    def get_active_tool(self) -> Object:
        '''Get cutting tool at current process location'''
        pass
    def get_active_tech(self) -> Object:
        '''Get technology settings at current process location'''
        pass
    def get_active_mfun(self) -> Object:
        '''Get machine_functions settings at current process location'''
        pass
    def get_active_obj(self) -> Object:
        '''Get STEP object associated with current process location'''
        pass
    def get_active_aux(self, auxidx: int) -> Object:
        '''Get auxillary STEP object associated with current process location'''
        pass
    def get_active_param(self) -> float:
        '''
        Get numeric parameter associated with STEP object at current moment
        in process, such as a curve parameter or position within sequence.
        '''
        pass
    def get_active_lenunit(self) -> RoseUnit:
        '''Get length unit at current process location'''
        pass
    def get_active_angunit(self) -> RoseUnit:
        '''Get angle unit at current process location'''
        pass
    
    def get_active_type(self) -> CtlType:
        '''Get type of process element at current process location'''
        pass
    def get_active_status(self) -> CtlStatus:
        '''Get state of process element at current moment in process'''
        pass
    
    def get_active_xform(self) -> List[float]:
        '''Get coordinate system transform matrix at current process location'''
        pass
    
    def get_active_pos(self, typ: CtlPosType, csys: CtlCsys = CtlCsys.WCS) -> int:
        '''Get position id by type and coordinate system'''
        pass
    def get_last_pos(self) -> int:
        '''Get postion id for move end, in the WCS'''
        pass
    def get_last_raw_pos(self) -> int:
        '''Get postion id for move end, in raw coordinate system'''
        pass

    
    def get_move_start(self, csys: CtlCsys = CtlCsys.WCS) -> int:
        '''Get position id for move start in WCS or optional CtlCsys'''
        pass
    def get_move_end(self, csys: CtlCsys = CtlCsys.WCS) -> int:
        '''Get position id for move end in WCS or optional CtlCsys'''
        pass
    def get_move_arc(self, csys: CtlCsys = CtlCsys.WCS) -> int:
        '''Get position id for entire arc in WCS or optional CtlCsys'''
        pass
    def get_move_probe(self, csys: CtlCsys = CtlCsys.WCS) -> int:
        '''Get position id for entire probe in WCS or optional CtlCsys'''
        pass


    def get_move_feed(self, u: RoseUnit = RoseUnit.AS_IS) -> float:
        '''Get feedrate in effect with optional unit for conversion'''
        pass
    def get_move_feed_unit(self) -> RoseUnit:
        '''Get feedrate unit used by the process.'''
        pass

    def get_move_spindle(self, u: RoseUnit = RoseUnit.AS_IS) -> float:
        '''Get spindle speed in effect with optional unit for conversion'''
        pass
    def get_move_spindle_unit(self) -> RoseUnit:
        '''Get spindle speed unit used by the process.'''
        pass


    def get_move_is_rapid(self) -> bool:
        '''Return true if move is rapid.'''
        pass
    def get_move_is_coolant(self) -> bool:
        '''Return true if move has coolant on.'''
        pass
    def get_move_is_mist_coolant(self) -> bool:
        '''Return true if move has mist coolant on.'''
        pass
    def get_move_is_thru_coolant(self) -> bool:
        '''Return true if move has through-spindle coolant on.'''
        pass


    def get_dwell_time(self, u: RoseUnit = RoseUnit.AS_IS) -> float:
        '''Get dwell time from a feedstop toolpath with optional unit for conversion'''
        pass
    def get_dwell_time_unit(self) -> RoseUnit:
        '''Get dwell time from a feedstop toolpath.'''
        pass


    def get_pos_lenunit(self, posid: int) -> RoseUnit:
        '''Get length unit for position id.'''
        pass
    def get_pos_angunit(self, posid: int) -> RoseUnit:
        '''Get angle unit for position id.'''
        pass
    def get_pos_csys(self, posid: int) -> CtlCsys:
        '''Get coordinate system code for position id.'''
        pass
    def get_pos_type(self, posid: int) -> CtlPosType:
        '''Get type code for position id.'''
        pass

    def get_pos_xyz(self, posid: int, u: RoseUnit = RoseUnit.AS_IS) -> tuple[float, float, float]:
        '''Return (X,Y,Z) values for position id and optional unit for conversion.'''
        pass

    def get_pos_dirz(self, posid: int) -> tuple[float, float, float]:
        '''Return (i,j,k) of Z direction for position id.'''
        pass
    def get_pos_default_dirz(self, posid: int) -> tuple[float, float, float]:
        '''Return (i,j,k) of Z direction for position id or default tool axis.'''
        pass

    def get_pos_dirx(self, posid: int) -> tuple[float, float, float]:
        '''Return (i,j,k) of X direction for position id.'''
        pass
    def get_pos_default_dirx(self, posid: int) -> tuple[float, float, float]:
        '''Return (i,j,k) of X direction for position id or default X axis.'''
        pass

    def get_pos_move_dir(self, posid: int) -> tuple[float, float, float]:
        '''Return (i,j,k) of move direction for position id.'''
        pass
    def get_pos_snorm_dir(self, posid: int) -> tuple[float, float, float]:
        '''Return (i,j,k) of surface normal direction for position id.'''
        pass

    def get_pos_speed_ratio(self, posid: int) -> float:
        '''Return speed ratio multiplier for position id.'''
        pass
    def get_pos_xsect(self, posid: int, u: RoseUnit = RoseUnit.AS_IS) -> dict[str, float]
        '''Return dictionary of cross section parameters for position id and optional unit for conversion.'''
        pass
    
    def get_pos_param(self, posid: int) -> float:
        '''Return the numeric parameter associated with the position id.'''
        pass

    
    def get_pos_xyz_obj(self, posid: int) -> Object:
        '''Return STEP object for XYZ value of position id.'''
        pass
    def get_pos_dirz_obj(self, posid: int) -> Object:
        '''Return STEP object for Z direction of position id.'''
        pass
    def get_pos_dirx_obj(self, posid: int) -> Object:
        '''Return STEP object for X direction of position id.'''
        pass
    def get_pos_snorm_dir_obj(self, posid: int) -> Object:
        '''Return STEP object for surface normal direction of position id.'''
        pass
    def get_pos_speed_ratio_obj(self, posid: int) -> Object:
        '''Return STEP object for speed ratio multiplier of position id.'''
        pass
    def get_pos_xsect_obj(self, posid: int) -> Object:
        '''Return STEP object for cross section of position id.'''
        pass


    def get_pos_is_equal(self, pos1: int, pos2: int) -> bool:
        '''Test whether two positions ids have same position, Z and X directions'''
        pass

    def get_arc_center(self, posid: int, u: RoseUnit = RoseUnit.AS_IS) -> tuple[float, float, float]:
        '''Return (X,Y,Z) values for center of arc position id with optional unit for conversion.'''
        pass
    def get_arc_axis(self, posid: int) -> tuple[float, float, float]:
        '''Return (i,j,k) values for axis of arc position id.'''
        pass

    def get_arc_radius(self, posid: int, u: RoseUnit = RoseUnit.AS_IS) -> float:
        '''Return radius value for arc position id with optional unit for conversion.'''
        pass
    def get_arc_angle(self, posid: int, u: RoseUnit = RoseUnit.AS_IS) -> float:
        '''Return angle value for arc position id with optional unit for conversion.'''
        pass
    def get_arc_height(self, posid: int, u: RoseUnit = RoseUnit.AS_IS) -> float:
        '''Return helix height value for arc position id with optional unit for conversion.'''
        pass

    def get_arc_is_cw(self, posid: int) -> bool:
        '''Return true if arc position id is clockwise'''
        pass
    def get_arc_is_over180(self, posid: int) -> bool:
        '''Return true if arc position id is over 180 degrees'''
        pass
    def get_arc_is_full_circle(self, posid: int) -> bool:
        '''Return true if arc position id is a complete circle'''
        pass


    def get_probe_direction(self, posid: int) -> tuple[float, float, float]:
        '''Return (i,j,k) values for direction of probe position id'''
        pass
    def get_probe_end(self, posid: int, u: RoseUnit = RoseUnit.AS_IS) -> tuple[float, float, float]:
        '''Return (X,Y,Z) values for end of probe position id with optional unit for conversion.'''
        pass
    def get_probe_start(self, posid: int, u: RoseUnit = RoseUnit.AS_IS) -> tuple[float, float, float]:
        '''Return (X,Y,Z) values for start of probe position id with optional unit for conversion.'''
        pass

    def get_probe_expected(self, posid: int, u: RoseUnit = RoseUnit.AS_IS) -> float:
        '''Return expected distance of probe position id with optional unit for conversion.'''
        pass
    
    def get_probe_expected_obj(self, posid: int) -> Object:
        '''Return STEP object for expected distance of probe position id.'''
        pass

    def get_probe_var(self, posid: int) -> str:
        '''Return variable name for probe position id.'''
        pass


    def get_probe_direction_obj(self, posid: int) -> Object:
        '''Return STEP object for direction of probe position id.'''
        pass
    def get_probe_start_obj(self, posid: int) -> Object:
        '''Return STEP object for start of probe position id.'''
        pass
    def get_probe_var_obj(self, posid: int) -> Object:
        '''Return STEP object for variable name of probe position id.'''
        pass
    def get_probe_workpiece(self, posid: int) -> Object:
        '''Return STEP workpiece object for probe position id.'''
        pass


    def get_stack_pos_of_type(self, t: CtlType) -> int:
        '''Return stack position containing event type'''
        pass
    def get_stack_size(self) -> int:
        '''Return stack size at current process location'''
        pass

    def get_frame_obj(self, idx: int) -> Object:
        '''Return STEP object for stack frame.'''
        pass
    def get_frame_aux(self, idx: int, auxidx: int) -> Object:
        '''Return auxillary STEP object for stack frame'''
        pass
    
    def get_frame_param(self, idx: int) -> float:
        '''Return numeric parameter associated with STEP object for stack frame.'''
        pass
    def get_frame_lenunit(self, idx: int) -> RoseUnit:
        '''Return length unit for stack frame'''
        pass
    def get_frame_angunit(self, idx: int) -> RoseUnit:
        '''Return angle unit for stack frame'''
        pass
    
    def get_frame_type(self, idx: int) -> CtlType:
        '''Return event type for stack frame'''
        pass
    def get_frame_status(self, idx: int) -> CtlStatus:
        '''Return event status for stack frame'''
        pass

    def get_frame_tech(self, idx: int) -> Object:
        '''Return STEP technology object for stack frame'''
        pass
    def get_frame_mfun(self, idx: int) -> Object:
        '''Return STEP machine functions object for stack frame'''
        pass
    def get_frame_xform(self, idx: int) -> List[float]:
        '''Return coordinate system transform for stack frame'''
        pass
    
    def get_frame_pos(self, pos: int, typ: CtlPosType, csys: CtlCsys = CtlCsys.WCS) -> int:
        '''Get position id in stack frame by type and coordinate system'''
        pass

    
# ==================================================
# GENERATE CODE GENERATOR CLASS
#
#

class TraceComments(IntEnum,auto):
    '''
    Identifies where descriptive comments are placed in codes created
    by the Generate class.

    '''
    NONE = auto()
    WORKPLAN = auto()
    WORKINGSTEP = auto()
    TOOLPATH = auto()
    POINT = auto()
    ALL_STEP = auto()

# Common signature for code generation functions
GenerateFn = Callable[[gen: Generate, gs: GenerateState, cur: Adaptive], Optional[str]]

class Generate:
    '''Generate code for process events.'''
    def reset(self) -> None:
        '''Reset the generate object to default style settings'''
        pass

    def set_style(self, name:str) -> bool:
        '''
        Find a built-in style with a given name and configure the 
        format object for that.  Returns true if the style was found.
        '''
        pass

    def export_cncfile(self, d: Design, filename: StrOrBytesPath) -> bool:
        '''
        Export a stepnc design to a CNC code file.  Set style and adjust
        any parameters, like digits of precision, before calling.
        '''
        pass

    def format_event(self, gs: GenerateState, cursor: Adaptive) -> Optional[str]:
        '''Return string for current process event.  May be None'''
        pass
    
    def format_type(self, gs: GenerateState, cursor: Adaptive) -> Optional[str]:
        '''Return string for active type in process event.  May be None'''
        pass

    def format_other(self, gs: GenerateState, cursor: Adaptive, name: str) -> Optional[str]:
        '''Return string for named support function.  May be None'''
        pass

    def format_block(self, gs: GenerateState, block: str) -> str:
        '''Return NC block, adding newline and block number if appropriate.'''
        pass
    def format_block_nonum(self, gs: GenerateState, block: str) -> str:
        '''Return NC block, adding newline, never block number.'''
        pass

    def format_comment(self, gs: GenerateState, s1: str, s2: str = '') -> str:
        '''Return comment using syntax for style, from one or two strings.'''
        pass
    

    def get_use_blocknums(self) -> bool:
        '''Use block numbers N1234 for each code.'''
        pass
    def set_use_blocknums(self, yn: bool) -> None:
        '''Use block numbers N1234 for each code.'''
        pass


    def get_blocknum_limit(self) -> int:
        '''
        Maximum permissible block number, or zero for no limit.  After
        the limit is reached, the block number wraps around to 1.
        '''
        pass
    def set_blocknum_limit(self, num: int) -> None:
        '''
        Maximum permissible block number, or zero for no limit.  After
        the limit is reached, the block number wraps around to 1.
        '''
        pass


    def get_use_whitespace(self) -> bool:
        '''Separate parameters by whitespace for readability.'''
        pass
    def set_use_whitespace(self, yn: bool) -> None:
        '''Separate parameters by whitespace for readability.'''
        pass


    def get_use_tool_constchip(self) -> bool:
        '''PROTOTYPE constant chip operation.'''
        pass
    def set_use_tool_constchip(self, yn: bool) -> None:
        '''PROTOTYPE constant chip operation.'''
        pass

    def get_use_tcp(self) -> bool:
        '''Generate TCP motion codes for five-axis.'''
        pass
    def set_use_tcp(self, yn: bool) -> None:
        '''Generate TCP motion codes for five-axis.'''
        pass

    def get_linearize_all_curves(self) -> bool:
        '''Break arcs and helixes into linear segments.'''
        pass
    def set_linearize_all_curves(self, yn: bool) -> None:
        '''Break arcs and helixes into linear segments.'''
        pass

    def get_chord_tolerance(self) -> float:
        '''Chordal tolerance used to linearize curves.'''
        pass
    def set_chord_tolerance(self, tol: float) -> None:
        '''Chordal tolerance used to linearize curves.'''
        pass

    def get_file_ext(self) -> str:
        '''Preferred file extension for code style.'''
        pass
    def set_file_ext(self, ext: str) -> None:
        '''Preferred file extension for code style.'''
        pass

    def get_digits(self) -> int:
        '''Maximum digits of precision when formatting coordinate values.'''
        pass
    def set_digits(self, cnt: int) -> None:
        '''Maximum digits of precision when formatting coordinate values.'''
        pass

    def get_min_digits(self) -> int:
        '''Minimum digits of precision when formatting coordinate values.'''
        pass
    def set_min_digits(self, cnt: int) -> None:
        '''Minimum digits of precision when formatting coordinate values.'''
        pass
    
    def get_ijk_digits(self) -> int:
        '''Maximum digits of precision when formatting IJK directions.'''
        pass
    def set_ijk_digits(self, cnt: int) -> None:
        '''Maximum digits of precision when formatting IJK directions.'''
        pass

    def get_ijk_min_digits(self) -> int:
        '''Minimum digits of precision when formatting IJK directions.'''
        pass
    def set_ijk_min_digits(self, cnt: int) -> None:
        '''Minimum digits of precision when formatting IJK directions.'''
        pass
    

    def get_angle_digits(self) -> int:
        '''Maximum digits of precision when formatting angle values.'''
        pass
    def set_angle_digits(self, cnt: int) -> None:
        '''Maximum digits of precision when formatting angle values.'''
        pass

    def get_angle_min_digits(self) -> int:
        '''Minimum digits of precision when formatting angle values.'''
        pass
    def set_angle_min_digits(self, cnt: int) -> None:
        '''Minimum digits of precision when formatting angle values.'''
        pass


    def get_feed_digits(self) -> int:
        '''Maximum digits of precision when formatting feedrate values.'''
        pass
    def set_feed_digits(self, cnt: int) -> None:
        '''Maximum digits of precision when formatting feedrate values.'''
        pass

    def get_feed_min_digits(self) -> int:
        '''Minimum digits of precision when formatting feedrate values.'''
        pass
    def set_feed_min_digits(self, cnt: int) -> None:
        '''Minimum digits of precision when formatting feedrate values.'''
        pass


    def get_spindle_digits(self) -> int:
        '''Maximum digits of precision when formatting spindle speeds.'''
        pass
    def set_spindle_digits(self, cnt: int) -> None:
        '''Maximum digits of precision when formatting spindle speeds.'''
        pass

    def get_spindle_min_digits(self) -> int:
        '''Minimum digits of precision when formatting spindle speeds.'''
        pass
    def set_spindle_min_digits(self, cnt: int) -> None:
        '''Minimum digits of precision when formatting spindle speeds.'''
        pass


    def get_program_number(self) -> int:
        '''Program number for fanuc and some other code styles.'''
        pass
    def set_program_number(self, pn: int) -> None:
        '''Program number for fanuc and some other code styles.'''
        pass

    def get_program_unit(self) -> RoseUnit:
        '''Preferred length unit to use when generating code.'''
        pass
    def set_program_unit(self, u: RoseUnit) -> None:
        '''Preferred length unit to use when generating code.'''
        pass
    
    
    def set_unit_system(self, cursor: Adaptive) -> None:
        '''
        Set length, feed, and spindle to match the program units.
        If AS_IS, use length unit of toolpaths from cursor.
        '''
        pass

    
    def get_len_unit(self) -> RoseUnit:
        '''Length unit to use when generating coordinates in code.'''
        pass
    def set_len_unit(self, u: RoseUnit) -> None:
        '''Length unit to use when generating coordinates in code.'''
        pass

    def get_feed_unit(self) -> RoseUnit:
        '''Feedrate unit to use when generating feed commands in code.'''
        pass
    def set_feed_unit(self, u: RoseUnit) -> None:
        '''Feedrate unit to use when generating feed commands in code.'''
        pass

    def get_spindle_unit(self) -> RoseUnit:
        '''Spindle speed unit to use when generating spindle commands in code.'''
        pass
    def set_spindle_unit(self, u: RoseUnit) -> None:
        '''Spindle speed unit to use when generating spindle commands in code.'''
        pass

    def get_move_is_modal(self) -> bool:
        '''
        Modal move emits G0/G1 once at start of a series of moves.
        Non-modal move emits the G0/G1 command for every move.
        '''
        pass
    def set_move_is_modal(self, yn: bool) -> None:
        '''
        Modal move emits G0/G1 once at start of a series of moves.
        Non-modal move emits the G0/G1 command for every move.
        '''
        pass

    def get_workoffset_frame(self) -> int:
        '''
        Work offset frame for generated code. -1 is no change, 0 is no offset.
        1 is the first on the machine, and so on.
        '''
        pass
    def set_workoffset_frame(self, ofs: int) -> None:
        '''
        Work offset frame for generated code. -1 is no change, 0 is no offset.
        1 is the first on the machine, and so on.
        '''
        pass

    def get_trace_comments(self) -> TraceComments:
        '''Control where helpful trace comments appear in generated code.'''
        pass
    def set_trace_comments(self, cmt: TraceComments) -> None:
        '''Control where helpful trace comments appear in generated code.'''
        pass

    
    def format_move_xyz(
            self, gs: GenerateState, cursor: Adaptive,
            x: float, y: float, z: float
    ) -> str:
        '''Move to an arbitrary XYZ position in the program units.'''
        pass

    def format_move_xyz_ijk(
            self, gs: GenerateState, cursor: Adaptive,
            x: float, y: float, z: float,
            i: float, j: float, k: float
    ) -> str:
        '''Move to an arbitrary XYZ/IJK position in the program units.'''
        pass

    
    def format_rapid_xyz(
            self, gs: GenerateState, cursor: Adaptive,
            x: float, y: float, z: float
    ) -> str:
        '''Rapid move to an arbitrary XYZ position in the program units.'''
        pass

    def format_rapid_xyz_ijk(
            self, gs: GenerateState, cursor: Adaptive,
            x: float, y: float, z: float,
            i: float, j: float, k: float
    ) -> str:
        '''Rapid move to an arbitrary XYZ/IJK position in the program units.'''
        pass

    
    // --------------------
    // STRING BUILDING AND NUMBER HANDLING -- 
    //
    def cat_space(self, txt: str) -> str:
        '''Add a space to the output string if whitespace is desired.'''
        pass
    def cat_required_space(self, txt: str) -> str:
        '''Add a space to the output string.'''
        pass

    def cat_number(self, txt: str, num: float, max_digits: int = None, min_digits: int = None) -> str:
        '''Add a number to the output string with optional precision values.'''
        pass
    def cat_number_as_ijk(self, txt: str, num: float) -> str:
        '''Add a number to the output string using IJK formatting.'''
        pass
    def cat_number_as_angle(self, txt: str, num: float) -> str:
        '''Add a number to the output string using angle formatting.'''
        pass
    def cat_number_as_feed(self, txt: str, num: float) -> str:
        '''Add a number to the output string using feedrate formatting.'''
        pass
    def cat_number_as_spindle(self, txt: str, num: float) -> str:
        '''Add a number to the output string using spindle speed formatting.'''
        pass

    
    def cat_param(self, txt: str, name: str, num: float = None, max_digits: int = None, min_digits: int = None) -> str:
        '''Add parameter name with optional number and precision values.'''
        pass
    def cat_param_as_ijk(self, txt: str, name: str, num: float) -> str:
        '''Add parameter name and IJK formatted number.'''
        pass
    def cat_param_as_angle(self, txt: str, name: str, num: float) -> str:
        '''Add parameter name and angle formatted number.'''
        pass
    def cat_param_as_feed(self, txt: str, name: str, num: float) -> str:
        '''Add parameter name and feed formatted number.'''
        pass
    def cat_param_as_spindle(self, txt: str, name: str, num: float) -> str:
        '''Add parameter name and spindle formatted number.'''
        pass


    def is_formatted_number(self, num1: float, num2: float, max_digits: int = None) -> bool:
        '''Do two numbers result in the same formatted value with optional digits of precision.'''
        pass
    def is_formatted_xyz(self,
                         x1: float, y1: float, z1: float,
                         x2: float, y2: float, z2: float) -> bool:
        '''Do two sets of XYZ numbers result in the same formatted values.'''
        pass
    
    def is_formatted_ijk(self,
                         i1: float, j1: float, k1: float,
                         i2: float, j2: float, k2: float) -> bool:
        '''Do two sets of IJK numbers result in the same formatted values.'''
        pass
    
    def get_out_xyz(self, cursor: Adaptive, pos: int, u: RoseUnit = RoseUnit.AS_IS) -> tuple[float, float, float]:
        '''Return (X,Y,Z) values for position id with output transform applied and optional unit conversion'''
        pass

    def get_out_dirz(self, cursor: Adaptive, pos: int) -> tuple[float, float, float]:
        '''Return (i,j,k) of Z direction for position id with output transform applied.'''
        pass
    def get_out_dirx(self, cursor: Adaptive, pos: int) -> tuple[float, float, float]:
        '''Return (i,j,k) of X direction for position id with output transform applied.'''
        pass
    def get_out_snorm_dir(self, cursor: Adaptive, pos: int) -> tuple[float, float, float]:
        '''Return (i,j,k) of surface normal direction for position id with output transform applied.'''
        pass
    def get_out_move_dir(self, cursor: Adaptive, pos: int) -> tuple[float, float, float]:
        '''Return (i,j,k) of move direction for position id with output transform applied.'''
        pass

    
    def get_out_arc_center(self, cursor: Adaptive, pos: int, u: RoseUnit = RoseUnit.AS_IS) -> tuple[float, float, float]:
        '''Return (X,Y,Z) values for center of arc position id with output transform applied and optional unit conversion'''
        pass
    def get_out_arc_axis(self, cursor: Adaptive, pos: int) -> tuple[float, float, float]:
        '''Return (i,j,k) of axis of arc position id with output transform applied.'''
        pass
    

    def get_out_xformed_point(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        '''Return (x,y,z) of point with output transform applied.'''
        pass
    def get_out_xformed_dir(self, i: float, j: float, k: float) -> tuple[float, float, float]:
        '''Return (i,j,k) of direction with output transform applied.'''
        pass

    
    def get_use_speed_override(self) -> bool:
        '''Generate feeds using override curve.'''
        pass
    def set_use_speed_override(self, yn: bool) -> None:
        '''Generate feeds using override curve.'''
        pass

    
    def get_stop_after_workingstep(self) -> bool:
        '''Generate an optional stop code after every workingstep.'''
        pass
    def set_stop_after_workingstep(self, yn: bool) -> None:
        '''Generate an optional stop code after every workingstep.'''
        pass


    
    def get_supress_xpos(self) -> bool:
        '''Do not generate any codes for the X axis.'''
        pass
    def set_supress_xpos(self, yn: bool) -> None:
        '''Do not generate any codes for the X axis.'''
        pass

    
    def get_supress_ypos(self) -> bool:
        '''Do not generate any codes for the Y axis.'''
        pass
    def set_supress_ypos(self, yn: bool) -> None:
        '''Do not generate any codes for the Y axis.'''
        pass
    
    def get_supress_zpos(self) -> bool:
        '''Do not generate any codes for the Z axis.'''
        pass
    def set_supress_zpos(self, yn: bool) -> None:
        '''Do not generate any codes for the Z axis.'''
        pass


    def get_feed_is_standalone(self) -> bool:
        '''True if feedrate changes are issued on a separate line.'''
        pass
    def set_feed_standalone(self) -> None:
        '''Generate feedrate changes on a separate line.'''
        pass
    def set_feed_inline(self) -> None:
        '''Generate feedrate changes as part of a move.'''
        pass

    def get_use_xform(self) -> bool:
        '''Apply destination transform to all coordinates and directions.'''
        pass
    def set_use_xform(self, yn: bool) -> None:
        '''Apply destination transform to all coordinates and directions.'''
        pass
    
    def get_dst_xform(self) -> List[float]:
        '''Get destination transform for coordinates and directions.'''
        pass
    def set_dst_xform(self, xf: Sequence[float]) -> None:
        '''Set destination transform for coordinates and directions.'''
        pass

    def get_dst_xform_is_left(self) -> bool:
        '''True if destination transform is left-handed.'''
        pass
    
    def set_event_fn(self, e: CtlEvent, fn: GenerateFn) -> None:
        '''Set callback function for formatting.'''
        pass
    
    def set_type_fn(self, t: CtlType, fn: GenerateFn) -> None:
        '''Set callback function for formatting.'''
        pass
    
    def set_other_fn(self, nm: str, fn: GenerateFn) -> None:
        '''Set callback function for formatting.'''
        pass
    
    def get_tool_number(self, tool: Object) -> int:
        '''Get number from description in tool object or special probe tool number.'''
        pass
    
    def get_probe_tool_number(self) -> int:
        '''Get special tool number to use for probing.'''
        pass
    def set_probe_tool_number(self, num: int) -> None:
        '''True if destination transform is left-handed.'''
        pass

    @staticmethod
    def builtin_none(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function none'''
        pass
    @staticmethod
    def builtin_coolant_apt(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function coolant_apt'''
        pass
    @staticmethod
    def builtin_coolant_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function coolant_default'''
        pass
    @staticmethod
    def builtin_coolant_haas(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function coolant_haas'''
        pass
    @staticmethod
    def builtin_coolant_off_apt(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function coolant_off_apt'''
        pass
    @staticmethod
    def builtin_coolant_off_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function coolant_off_default'''
        pass
    @staticmethod
    def builtin_coolant_off_haas(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function coolant_off_haas'''
        pass
    @staticmethod
    def builtin_coolant_off_siemens_macro(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function coolant_off_siemens_macro'''
        pass
    @staticmethod
    def builtin_coolant_okuma(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function coolant_okuma'''
        pass
    @staticmethod
    def builtin_coolant_siemens_macro(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function coolant_siemens_macro'''
        pass
    @staticmethod
    def builtin_dwell_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function dwell_default'''
        pass
    @staticmethod
    def builtin_dwell_fanuc(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function dwell_fanuc'''
        pass
    @staticmethod
    def builtin_dwell_siemens(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function dwell_siemens'''
        pass
    @staticmethod
    def builtin_error(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function error'''
        pass
    @staticmethod
    def builtin_filename(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function filename'''
        pass
    @staticmethod
    def builtin_move_apt(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_apt'''
        pass
    @staticmethod
    def builtin_move_arc_apt(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_arc_apt'''
        pass
    @staticmethod
    def builtin_move_arc_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_arc_default'''
        pass
    @staticmethod
    def builtin_move_arc_esab(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_arc_esab'''
        pass
    @staticmethod
    def builtin_move_arc_fanuc(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_arc_fanuc'''
        pass
    @staticmethod
    def builtin_move_arc_heidenhain(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_arc_heidenhain'''
        pass
    @staticmethod
    def builtin_move_arc_siemens(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_arc_siemens'''
        pass
    @staticmethod
    def builtin_move_arc_linear(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_arc_linear'''
        pass
    @staticmethod
    def builtin_move_contact(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_contact'''
        pass
    @staticmethod
    def builtin_move_crcl(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_crcl'''
        pass
    @staticmethod
    def builtin_move_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_default'''
        pass
    @staticmethod
    def builtin_move_dmis(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_dmis'''
        pass
    @staticmethod
    def builtin_move_fanuc_renishaw(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_fanuc_renishaw'''
        pass
    @staticmethod
    def builtin_move_feed(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_feed'''
        pass
    @staticmethod
    def builtin_move_feed_apt(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_feed_apt'''
        pass
    @staticmethod
    def builtin_move_feed_esab(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_feed_esab'''
        pass
    @staticmethod
    def builtin_move_helix_apt(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_helix_apt'''
        pass
    @staticmethod
    def builtin_move_helix_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_helix_default'''
        pass
    @staticmethod
    def builtin_move_helix_fanuc(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_helix_fanuc'''
        pass
    @staticmethod
    def builtin_move_helix_heidenhain(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_helix_heidenhain'''
        pass
    @staticmethod
    def builtin_move_helix_siemens(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_helix_siemens'''
        pass
    @staticmethod
    def builtin_move_helix_linear(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_helix_linear'''
        pass
    @staticmethod
    def builtin_move_ijk_fanuc(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_ijk_fanuc'''
        pass
    @staticmethod
    def builtin_move_ijk_siemens_traori(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_ijk_siemens_traori'''
        pass
    @staticmethod
    def builtin_move_ijk_tcp_ab(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_ijk_tcp_ab'''
        pass
    @staticmethod
    def builtin_move_ijk_tcp_ac(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_ijk_tcp_ac'''
        pass
    @staticmethod
    def builtin_move_ijk_tcp_bc(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_ijk_tcp_bc'''
        pass
    @staticmethod
    def builtin_move_none(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_none'''
        pass
    @staticmethod
    def builtin_move_siemens_renishaw(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_siemens_renishaw'''
        pass
    @staticmethod
    def builtin_move_trace(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_trace'''
        pass
    @staticmethod
    def builtin_move_xyz(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_xyz'''
        pass
    @staticmethod
    def builtin_move_xyz_esab(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function move_xyz_esab'''
        pass
    @staticmethod
    def builtin_ncfun_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_default'''
        pass
    @staticmethod
    def builtin_ncfun_exchange_pallet_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_exchange_pallet_default'''
        pass
    @staticmethod
    def builtin_ncfun_extended_apt_insert(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_extended_apt_insert'''
        pass
    @staticmethod
    def builtin_ncfun_extended_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_extended_default'''
        pass
    @staticmethod
    def builtin_ncfun_extended_esab(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_extended_esab'''
        pass
    @staticmethod
    def builtin_ncfun_index_pallet_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_index_pallet_default'''
        pass
    @staticmethod
    def builtin_ncfun_index_table_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_index_table_default'''
        pass
    @staticmethod
    def builtin_ncfun_index_table_heidenhain(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_index_table_heidenhain'''
        pass
    @staticmethod
    def builtin_ncfun_message_apt_pprint(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_message_apt_pprint'''
        pass
    @staticmethod
    def builtin_ncfun_message_comma_uppercase(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_message_comma_uppercase'''
        pass
    @staticmethod
    def builtin_ncfun_message_comment(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_message_comment'''
        pass
    @staticmethod
    def builtin_ncfun_message_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_message_default'''
        pass
    @staticmethod
    def builtin_ncfun_message_dmis(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_message_dmis'''
        pass
    @staticmethod
    def builtin_ncfun_message_okuma(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_message_okuma'''
        pass
    @staticmethod
    def builtin_ncfun_message_siemens(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_message_siemens'''
        pass
    @staticmethod
    def builtin_ncfun_optional_stop_apt(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_optional_stop_apt'''
        pass
    @staticmethod
    def builtin_ncfun_optional_stop_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_optional_stop_default'''
        pass
    @staticmethod
    def builtin_ncfun_stop_apt(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_stop_apt'''
        pass
    @staticmethod
    def builtin_ncfun_stop_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function ncfun_stop_default'''
        pass
    @staticmethod
    def builtin_op_approach_paths(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function op_approach_paths'''
        pass
    @staticmethod
    def builtin_op_lift_paths(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function op_lift_paths'''
        pass
    @staticmethod
    def builtin_probe_comments(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_comments'''
        pass
    @staticmethod
    def builtin_probe_comments_dmis(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_comments_dmis'''
        pass
    @staticmethod
    def builtin_probe_crcl(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_crcl'''
        pass
    @staticmethod
    def builtin_probe_datums_dmis(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_datums_dmis'''
        pass
    @staticmethod
    def builtin_probe_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_default'''
        pass
    @staticmethod
    def builtin_probe_dmis_feature(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_dmis_feature'''
        pass
    @staticmethod
    def builtin_probe_dmis_feature_end(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_dmis_feature_end'''
        pass
    @staticmethod
    def builtin_probe_dmis_feature_start(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_dmis_feature_start'''
        pass
    @staticmethod
    def builtin_probe_dmis_ptfeat(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_dmis_ptfeat'''
        pass
    @staticmethod
    def builtin_probe_dmis_ptmeas(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_dmis_ptmeas'''
        pass
    @staticmethod
    def builtin_probe_fanuc_renishaw(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_fanuc_renishaw'''
        pass
    @staticmethod
    def builtin_probe_haas_renishaw(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_haas_renishaw'''
        pass
    @staticmethod
    def builtin_probe_heidenhain(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_heidenhain'''
        pass
    @staticmethod
    def builtin_probe_heidenhain_hhcycle(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_heidenhain_hhcycle'''
        pass
    @staticmethod
    def builtin_probe_okuma(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_okuma'''
        pass
    @staticmethod
    def builtin_probe_prog_begin_fanuc(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_prog_begin_fanuc'''
        pass
    @staticmethod
    def builtin_probe_prog_begin_siemens(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_prog_begin_siemens'''
        pass
    @staticmethod
    def builtin_probe_siemens_renishaw(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_siemens_renishaw'''
        pass
    @staticmethod
    def builtin_probe_siemens_xy(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function probe_siemens_xy'''
        pass
    @staticmethod
    def builtin_program_end_apt(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_end_apt'''
        pass
    @staticmethod
    def builtin_program_end_crcl(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_end_crcl'''
        pass
    @staticmethod
    def builtin_program_end_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_end_default'''
        pass
    @staticmethod
    def builtin_program_end_dmis(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_end_dmis'''
        pass
    @staticmethod
    def builtin_program_end_esab(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_end_esab'''
        pass
    @staticmethod
    def builtin_program_end_fanuc(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_end_fanuc'''
        pass
    @staticmethod
    def builtin_program_end_heidenhain(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_end_heidenhain'''
        pass
    @staticmethod
    def builtin_program_end_okuma(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_end_okuma'''
        pass
    @staticmethod
    def builtin_program_end_okuma_omac(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_end_okuma_omac'''
        pass
    @staticmethod
    def builtin_program_end_okuma_lockheed(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_end_okuma_lockheed'''
        pass
    @staticmethod
    def builtin_program_end_siemens(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_end_siemens'''
        pass
    @staticmethod
    def builtin_program_end_siemens_traori(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_end_siemens_traori'''
        pass
    @staticmethod
    def builtin_program_start_apt(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_start_apt'''
        pass
    @staticmethod
    def builtin_program_start_crcl(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_start_crcl'''
        pass
    @staticmethod
    def builtin_program_start_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_start_default'''
        pass
    @staticmethod
    def builtin_program_start_dmis(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_start_dmis'''
        pass
    @staticmethod
    def builtin_program_start_esab(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_start_esab'''
        pass
    @staticmethod
    def builtin_program_start_fanuc(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_start_fanuc'''
        pass
    @staticmethod
    def builtin_program_start_haas_rpi(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_start_haas_rpi'''
        pass
    @staticmethod
    def builtin_program_start_heidenhain(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_start_heidenhain'''
        pass
    @staticmethod
    def builtin_program_start_mdsi(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_start_mdsi'''
        pass
    @staticmethod
    def builtin_program_start_okuma(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_start_okuma'''
        pass
    @staticmethod
    def builtin_program_start_okuma_omac(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_start_okuma_omac'''
        pass
    @staticmethod
    def builtin_program_start_okuma_lockheed(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_start_okuma_lockheed'''
        pass
    @staticmethod
    def builtin_program_start_siemens(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function program_start_siemens'''
        pass
    @staticmethod
    def builtin_refpoint_center(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function refpoint_center'''
        pass
    @staticmethod
    def builtin_refpoint_contact(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function refpoint_contact'''
        pass
    @staticmethod
    def builtin_refpoint_left(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function refpoint_left'''
        pass
    @staticmethod
    def builtin_refpoint_right(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function refpoint_right'''
        pass
    @staticmethod
    def builtin_setup_start_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function setup_start_default'''
        pass
    @staticmethod
    def builtin_spindle_apt(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function spindle_apt'''
        pass
    @staticmethod
    def builtin_spindle_apt_uvd(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function spindle_apt_uvd'''
        pass
    @staticmethod
    def builtin_spindle_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function spindle_default'''
        pass
    @staticmethod
    def builtin_spindle_off_apt(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function spindle_off_apt'''
        pass
    @staticmethod
    def builtin_spindle_off_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function spindle_off_default'''
        pass
    @staticmethod
    def builtin_spindle_off_siemens_macro(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function spindle_off_siemens_macro'''
        pass
    @staticmethod
    def builtin_spindle_siemens_macro(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function spindle_siemens_macro'''
        pass
    @staticmethod
    def builtin_spindle_speed_before_direction(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function spindle_speed_before_direction'''
        pass
    @staticmethod
    def builtin_tap_comment(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tap_comment'''
        pass
    @staticmethod
    def builtin_tap_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tap_default'''
        pass
    @staticmethod
    def builtin_tap_first(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tap_first'''
        pass
    @staticmethod
    def builtin_tap_first_siemens(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tap_first_siemens'''
        pass
    @staticmethod
    def builtin_tap_last(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tap_last'''
        pass
    @staticmethod
    def builtin_tap_last_g84(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tap_last_g84'''
        pass
    @staticmethod
    def builtin_tap_point_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tap_point_default'''
        pass
    @staticmethod
    def builtin_tap_point_g84(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tap_point_g84'''
        pass
    @staticmethod
    def builtin_tap_point_siemens(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tap_point_siemens'''
        pass
    @staticmethod
    def builtin_timestamp(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function timestamp'''
        pass
    @staticmethod
    def builtin_tool_change_apt(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tool_change_apt'''
        pass
    @staticmethod
    def builtin_tool_change_comment(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tool_change_comment'''
        pass
    @staticmethod
    def builtin_tool_change_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tool_change_default'''
        pass
    @staticmethod
    def builtin_tool_change_fanuc_tcp(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tool_change_fanuc_tcp'''
        pass
    @staticmethod
    def builtin_tool_change_fanuc_tcp_T100_no_M6(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tool_change_fanuc_tcp_T100_no_M6'''
        pass
    @staticmethod
    def builtin_tool_change_haas_rpi(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tool_change_haas_rpi'''
        pass
    @staticmethod
    def builtin_tool_change_heidenhain(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tool_change_heidenhain'''
        pass
    @staticmethod
    def builtin_tool_change_mdsi(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tool_change_mdsi'''
        pass
    @staticmethod
    def builtin_tool_change_okuma(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tool_change_okuma'''
        pass
    @staticmethod
    def builtin_tool_change_okuma_omac(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tool_change_okuma_omac'''
        pass
    @staticmethod
    def builtin_tool_change_okuma_lockheed(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tool_change_okuma_lockheed'''
        pass
    @staticmethod
    def builtin_tool_change_siemens(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tool_change_siemens'''
        pass
    @staticmethod
    def builtin_tool_change_siemens_810(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tool_change_siemens_810'''
        pass
    @staticmethod
    def builtin_tool_change_siemens_traori(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function tool_change_siemens_traori'''
        pass
    @staticmethod
    def builtin_toolpath_start_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function toolpath_start_default'''
        pass
    @staticmethod
    def builtin_units_apt(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function units_apt'''
        pass
    @staticmethod
    def builtin_units_crcl(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function units_crcl'''
        pass
    @staticmethod
    def builtin_units_dmis(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function units_dmis'''
        pass
    @staticmethod
    def builtin_units_g20(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function units_g20'''
        pass
    @staticmethod
    def builtin_units_g70(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function units_g70'''
        pass
    @staticmethod
    def builtin_units_g700(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function units_g700'''
        pass
    @staticmethod
    def builtin_workingstep_end_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workingstep_end_default'''
        pass
    @staticmethod
    def builtin_workingstep_start_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workingstep_start_default'''
        pass
    @staticmethod
    def builtin_workingstep_start_esab(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workingstep_start_esab'''
        pass
    @staticmethod
    def builtin_workingstep_start_fanuc(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workingstep_start_fanuc'''
        pass
    @staticmethod
    def builtin_workingstep_start_fanuc_unwind(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workingstep_start_fanuc_unwind'''
        pass
    @staticmethod
    def builtin_workingstep_start_siemens(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workingstep_start_siemens'''
        pass
    @staticmethod
    def builtin_workingstep_trace_clear_fanuc(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workingstep_trace_clear_fanuc'''
        pass
    @staticmethod
    def builtin_workingstep_trace_clear_siemens(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workingstep_trace_clear_siemens'''
        pass
    @staticmethod
    def builtin_workoffset_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workoffset_default'''
        pass
    @staticmethod
    def builtin_workoffset_okuma(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workoffset_okuma'''
        pass
    @staticmethod
    def builtin_workplan_end_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workplan_end_default'''
        pass
    @staticmethod
    def builtin_workplan_probe_end_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workplan_probe_end_default'''
        pass
    @staticmethod
    def builtin_workplan_probe_end_fanuc_renishaw(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workplan_probe_end_fanuc_renishaw'''
        pass
    @staticmethod
    def builtin_workplan_probe_end_haas_renishaw(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workplan_probe_end_haas_renishaw'''
        pass
    @staticmethod
    def builtin_workplan_probe_end_okuma(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workplan_probe_end_okuma'''
        pass
    @staticmethod
    def builtin_workplan_probe_end_siemens_renishaw(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workplan_probe_end_siemens_renishaw'''
        pass
    @staticmethod
    def builtin_workplan_probe_start_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workplan_probe_start_default'''
        pass
    @staticmethod
    def builtin_workplan_probe_start_fanuc_renishaw(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workplan_probe_start_fanuc_renishaw'''
        pass
    @staticmethod
    def builtin_workplan_probe_start_haas_renishaw(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workplan_probe_start_haas_renishaw'''
        pass
    @staticmethod
    def builtin_workplan_probe_start_okuma(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workplan_probe_start_okuma'''
        pass
    @staticmethod
    def builtin_workplan_probe_start_siemens_renishaw(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workplan_probe_start_siemens_renishaw'''
        pass
    @staticmethod
    def builtin_workplan_start_default(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workplan_start_default'''
        pass
    @staticmethod
    def builtin_workplan_start_dmis(gen: Generate, gs: GenerateState, cur: Adaptive) -> Optional[str]
        '''Built in generator function workplan_start_dmis'''
        pass
  
    
# ==================================================
# GENERATESTATE CODE GENERATOR SUPPORT CLASS
#
#

class GenerateState:
    '''Control variables for code generation'''
    def reset(self) -> None:
        '''Reset the generate state to default values'''
        pass

    def get_next_blocknum(self) -> int:
        '''Increment block number and return next one for generated code.'''
        pass

    def get_last_blocknum(self) -> int:
        '''Get last block number issued in generated code.'''
        pass

    def set_blocknum(self, num: int) -> None:
        '''Set block number for use in exported code.'''
        pass

    def clear_position(self) -> None:
        '''Clear stored position information.'''
        pass
    def get_xpos(self) -> float:
        '''Get last commanded X axis value.'''
        pass
    def get_ypos(self) -> float:
        '''Get last commanded Y axis value.'''
        pass
    def get_zpos(self) -> float:
        '''Get last commanded Z axis value.'''
        pass
    def get_xyzpos(self) -> tuple[float, float, float]:
        '''Get tuple containing last commanded X, Y, Z axis values.'''
        pass
    def set_xpos(self, x:float) -> None:
        '''Set last commanded X axis value.'''
        pass
    def set_ypos(self, y:float) -> None:
        '''Set last commanded Y axis value.'''
        pass
    def set_zpos(self, z:float) -> None:
        '''Set last commanded Z axis value.'''
        pass
    def set_xyzpos(self, x:float, y:float, z:float) -> None:
        '''Set last commanded X, Y, Z axis values.'''
        pass

    def is_changed_xyzpos(self, x:float, y:float, z:float) -> bool:
        '''Compare X, Y, Z values with last commanded axis values.'''
        pass
    
    def is_unknown_xyzpos(self) -> bool:
        '''Return true if last commanded X, Y, X axis values are unset.'''
        pass



    def get_ipos(self) -> float:
        '''Get last commanded I tool axis value.'''
        pass
    def get_jpos(self) -> float:
        '''Get last commanded J tool axis value.'''
        pass
    def get_kpos(self) -> float:
        '''Get last commanded K tool axis value.'''
        pass
    def get_ijkpos(self) -> tuple[float, float, float]:
        '''Get tuple containing last commanded IJK tool axis values.'''
        pass
    def set_ipos(self, x:float) -> None:
        '''Set last commanded I tool axis value.'''
        pass
    def set_jpos(self, y:float) -> None:
        '''Set last commanded J tool axis value.'''
        pass
    def set_kpos(self, z:float) -> None:
        '''Set last commanded K tool axis value.'''
        pass
    def set_ijkpos(self, i:float, j:float, k:float) -> None:
        '''Set last commanded IJK tool axis values.'''
        pass

    def is_changed_ijkpos(self, i:float, j:float, k:float) -> bool:
        '''Compare IJK values with last commanded tool axis values.'''
        pass
    def is_changed_ijkpos_3axis(self, i:float, j:float, k:float) -> bool:
        '''Compare IJK values with last commanded tool axis values, treating None as 001'''
        pass
    
    def is_unknown_ijkpos(self) -> bool:
        '''Return true if last commanded IJK tool axis values are unset.'''
        pass
    

    def get_apos(self) -> float:
        '''Get last commanded A axis value.'''
        pass
    def get_bpos(self) -> float:
        '''Get last commanded B axis value.'''
        pass
    def get_cpos(self) -> float:
        '''Get last commanded C axis value.'''
        pass

    def set_apos(self, x:float) -> None:
        '''Set last commanded A axis value.'''
        pass
    def set_bpos(self, y:float) -> None:
        '''Set last commanded B axis value.'''
        pass
    def set_cpos(self, z:float) -> None:
        '''Set last commanded C axis value.'''
        pass

    
    def clear_feed(self) -> None:
        '''Clear stored feedrate information.'''
        pass
    def get_feed(self) -> float:
        '''Get last commanded feedrate value.'''
        pass
    def set_feed(self, val:float) -> None:
        '''Set last commanded feedrate value.'''
        pass

    
    def clear_spindle(self) -> None:
        '''Clear stored spindle speed information.'''
        pass
    def get_spindle(self) -> float:
        '''Get last commanded spindle speed value.'''
        pass
    def set_spindle(self, val:float) -> None:
        '''Set last commanded spindle speed value.'''
        pass

    
    def clear_coolant(self) -> None:
        '''Clear stored coolant information.'''
        pass
    def get_coolant(self) -> bool:
        '''Get last commanded state of flood coolant.'''
        pass
    def set_coolant(self, val:bool) -> None:
        '''Set last commanded state of flood coolant.'''
        pass
    def get_coolant_mist(self) -> bool:
        '''Get last commanded state of mist coolant.'''
        pass
    def set_coolant_mist(self, val:bool) -> None:
        '''Set last commanded state of mist coolant.'''
        pass
    def get_coolant_thru(self) -> bool:
        '''Get last commanded state of thru spindle coolant.'''
        pass
    def set_coolant_thru(self, val:bool) -> None:
        '''Set last commanded state of thru spindle coolant.'''
        pass


    
    def clear_move_mode(self) -> None:
        '''Clear stored move mode information.'''
        pass
    def get_move_mode(self) -> int:
        '''Get numeric value for the last commanded modal move state.'''
        pass
    def set_move_mode(self, val:int) -> None:
        '''Set numeric value for the last commanded modal move state.'''
        pass

    
    def clear_move_prefix(self) -> None:
        '''Clear stored move prefix information.'''
        pass
    def get_move_prefix(self) -> str:
        '''Get stored move prefix string.'''
        pass
    def add_move_prefix(self, code:str) -> None:
        '''Append string to stored move prefix string, many can be added.'''
        pass

    
    def clear_move_comment(self) -> None:
        '''Clear stored move comment information.'''
        pass
    def get_move_comment(self) -> str:
        '''Get stored move comment string.'''
        pass
    def add_move_comment(self, code:str) -> None:
        '''Append string to stored move comment string, many can be added.'''
        pass


    
    def clear_program_stats(self) -> None:
        '''Clear stored program stats.'''
        pass
    def set_program_stats(self, cursor: Adaptive) -> None:
        '''Take and Adaptive object and Scan the program for probes, five axis motion.'''
        pass
    def get_program_has_5axis(self) -> bool:
        '''Get stat whether any toolpaths include a tool axis curve.'''
        pass
    def set_program_has_5axis(self, val:bool) -> None:
        '''Set stat whether any toolpaths include a tool axis curve.'''
        pass
    def get_program_has_probes(self) -> bool:
        '''Get stat whether program has any probing operations.'''
        pass

    def get_probe_count(self) -> int:
        '''Get stat computed number of probe operations in program.'''
        pass
    def set_probe_count(self, val:int) -> None:
        '''Set stat computed number of probe operations in program.'''
        pass
    
    def get_probe_index(self) -> int:
        '''Get the number of probing operations visited so far.'''
        pass
    def get_next_probe_index(self) -> int:
        '''Increment number of probing operations visited and return new value.'''
        pass
    def set_probe_index(self, val:int) -> None:
        '''Set the number of probing operations visited so far.'''
        pass
    

    def clear_refpoint(self) -> None:
      '''Clear stored reference point (center/contact) state.'''
      pass

    def is_refpoint_center(self) -> bool:
        '''Return true if tool reference point is set to center point.'''
        pass
    def is_refpoint_contact(self) -> bool:
        '''Return true if tool reference point is set to contact point.'''
        pass
    def is_refpoint_left(self) -> bool:
        '''Return true if tool reference is set to contact point and left.'''
        pass
    def is_refpoint_right(self) -> bool:
        '''Return true if tool reference is set to contact point and right.'''
        pass
    
    def set_refpoint_center(self) -> None:
        '''Set tool reference point to center point.'''
        pass
    def set_refpoint_contact(self) -> None:
        '''Set tool reference point to contact point.'''
        pass
    def set_refpoint_left(self) -> None:
        '''Set tool reference to left.'''
        pass
    def set_refpoint_right(self) -> None:
        '''Set tool reference to right.'''
        pass

  
    
    
# ==================================================
# APT API CLASS
#
class AptAPI:
    '''High level API for process creation operations'''
    @classmethod
    def auto_workingstep_spindle(cls) -> None:
        '''Create new workingsteps at spindle speed or tool changes.'''
        pass

    @classmethod
    def auto_workingstep_tool(cls) -> None:
        '''Create new workingsteps explicitly, or at tool change.'''
        pass
    
    @classmethod
    def design(cls) -> Design:
        '''Get the current design object.'''
        pass

    @classmethod
    def end_workplan(cls) -> None:
        '''End nested workplan and make its parent the current workplan.'''
        pass

    @classmethod
    def executable_workpiece_asis(cls, executable: Object, filename: StrOrBytesPath) -> Object:
        '''Import STEP model as AS-IS workpiece of executable, return new workpiece.'''
        pass

    @classmethod
    def executable_workpiece_removal(cls, executable: Object, filename: StrOrBytesPath) -> Object:
        '''Import STEP model as REMOVAL workpiece of executable, return new workpiece.'''
        pass

    @classmethod
    def executable_workpiece_reuse_asis(cls, executable: Object, other: Object) -> None:
        '''Use AS-IS workpiece of other as AS-IS workpiece of executable.'''

    @classmethod
    def executable_workpiece_reuse_removal(cls, executable: Object, other: Object) -> None:
        '''Use REMOVAL workpiece of other as REMOVAL workpiece of executable.'''

    @classmethod
    def executable_workpiece_reuse_tobe(cls, executable: Object, other: Object) -> None:
        '''Use TO-BE workpiece of other as TO-BE workpiece of executable.'''

    @classmethod
    def executable_workpiece_tobe(cls, executable: Object, filename: StrOrBytesPath) -> Object:
        '''Import STEP model as TO-BE workpiece of executable, return new workpiece.'''
        pass
    
    @classmethod
    def fixture(cls, filename: StrOrBytesPath, workplan: Object = None) -> Object:
        '''Import STEP CAD file for fixture of workplan setup.'''
        pass
    
    @classmethod
    def generate_all_tool_geometry(cls) -> None:
        '''Create product geometry from parametric description for any tool without it.'''
        pass
    
    @classmethod
    def geometry_for_tool_number(cls, filename: StrOrBytesPath, toolnum: int) -> Object:
        '''Import STEP CAD file for shape associated with tool number.'''
        pass
    
    @classmethod
    def get_current_fixture(cls) -> Object:
        '''Get current fixture workpiece object.'''
        pass

    @classmethod
    def get_current_project(cls) -> Object:
        '''Get current project object.'''
        pass

    @classmethod
    def get_current_rawpiece(cls) -> Object:
        '''Get current rawpiece object.'''
        pass

    @classmethod
    def get_current_workingstep(cls) -> Object:
        '''Get current workingstep object.'''
        pass

    @classmethod
    def get_current_workpiece(cls) -> Object:
        '''Get current workpiece object.'''
        pass
    
    @classmethod
    def get_current_workplan(cls) -> Object:
        '''Get current workplan object.'''
        pass

    @classmethod
    def get_executable_workpiece_asis(cls, executable: Object) -> Object:
        '''Return AS-IS workpiece of executable.'''
        pass

    @classmethod
    def get_executable_workpiece_removal(cls, executable: Object) -> Object:
        '''Return REMOVAL workpiece of executable.'''
        pass

    @classmethod
    def get_executable_workpiece_tobe(cls, executable: Object) -> Object:
        '''Return TO-BE workpiece of executable.'''
        pass

    @classmethod
    def get_id_from_uuid(cls, uuid: str) -> Object:
        '''Return data object with given UUID.'''
        pass
    
    @classmethod
    def get_uuid(cls, obj: Object) -> Optional[str]:
        '''Return UUID for data object if present, may be None.'''
        pass
    
    @classmethod
    def get_tool_product(cls, toolnum: str) -> Object:
        '''Return workpiece associated with tool number.'''
        pass
    
    @classmethod
    def inches(cls) -> None:
        '''Use inch units for process.'''
        pass

    @classmethod
    def millimeters(cls) -> None:
        '''Use millimeter units for process.'''
        pass
    
    @classmethod
    def nest_non_sequential(cls, name: str) -> Object:
        '''Create and return a new non-sequential as the current workplan.'''
        pass

    @classmethod
    def nest_non_sequential_after(cls, name: str, index: int, plan: Object) -> Object:
        '''Create and return a new non-sequential as the current workplan.'''
        pass
    
    @classmethod
    def nest_parallel(cls, name: str) -> Object:
        '''Create and return a new parallel as the current workplan.'''
        pass
    
    @classmethod
    def nest_parallel_after(cls, name: str, index: int, plan: Object) -> Object:
        '''Create and return a new parallel as the current workplan.'''
        pass

    @classmethod
    def nest_selective(cls, name: str) -> Object:
        '''Create and return a new selective as the current workplan.'''
        pass
    
    @classmethod
    def nest_selective_after(cls, name: str, index: int, plan: Object) -> Object:
        '''Create and return a new selective as the current workplan.'''
        pass
    
    @classmethod
    def nest_workplan(cls, name: str) -> Object:
        '''Create and return new workplan as the current workplan.'''
        pass
    
    @classmethod
    def nest_workplan_after(cls, name: str, index: int, plan: Object) -> Object:
        '''Create and return new workplan as the current workplan.'''
        pass
    
    @classmethod
    def new_project(cls, name: str) -> Design:
        '''Create a new project, return containing design.'''
        pass

    @classmethod
    def open_project(cls, filename: StrOrBytesPath) -> Design:
        '''Read STEP or STEP-NC file.'''
        pass

    @classmethod
    def partno(cls, partname: str) -> None:
        '''Set part name in process.'''
        pass

    @classmethod
    def put_workpiece_placement(
            cls, workpiece: Object,
	    x: float, y: float, z: float,
	    i: float = 0, j: float = 0, k: float = 1,
	    a: float = 1, b: float = 0, c: float = 0) -> None:
        '''Change placement of workpiece.'''
        pass

    @classmethod
    def rapid(cls) -> None:
        '''Use rapid feedrate.'''
        pass
    
    @classmethod
    def rawpiece(cls, filename: StrOrBytesPath) -> Object:
        '''Import STEP CAD file as rawpiece object.'''
        pass

    @classmethod
    def read_catia_aptcl(cls, filename: StrOrBytesPath) -> None:
        '''Create AP238 process from binary APT CL produced by Catia.'''
        pass

    @classmethod
    def read_makino_aptcl(cls, filename: StrOrBytesPath) -> None:
        '''Create AP238 process from APT CL produced by Makino FFCAM.'''
        pass

    @classmethod
    def read_proe_aptcl(cls, filename: StrOrBytesPath) -> None:
        '''Create AP238 process from APT CL produced by Pro/Engineer.'''
        pass

    @classmethod
    def read_ugs_aptcl(cls, filename: StrOrBytesPath) -> None:
        '''Create AP238 process from APT CL produced by Siemens NX.'''
        pass

    @classmethod
    def retract_plane(cls, z_value: float) -> None:
        '''Set the Z value for the retract plane for the process.'''
        pass

    @classmethod
    def save(cls, filename: StrOrBytesPath,
             modules: bool = True,
             xml: bool = False) -> None:
        '''Save file as filename.  Modules flag groups instances by ARM object.'''
        pass

    @classmethod
    def set_make_display_messages(cls, yn: bool) -> None:
        '''Control whether certain APT commands are included as message NC functions.'''
        pass

    @classmethod
    def set_name(cls, obj: Object, name: str) -> None:
        '''Set name of STEP-NC data object.'''
        pass

    @classmethod
    def set_name_in_plan(cls, workplan: Object, index: int, name: str) -> None:
        '''Set name of workingstep by position in a workplan.'''
        pass

    @classmethod
    def set_spindle_speed_for_feed_ccw(cls, feed: float, speed: float) -> None:
        '''Set counter-clockwise spindle speed for a given feed.'''
        pass

    @classmethod
    def set_spindle_speed_for_feed_cw(cls, feed: float, speed: float) -> None:
        '''Set clockwise spindle speed for a given feed.'''
        pass

    @classmethod
    def set_tool_diameter(cls, toolnum: int, diameter: float) -> None:
        '''Set the diameter in the parametric description of the given tool number.'''
        pass

    @classmethod
    def set_tool_length(cls, toolnum: int, length: float) -> None:
        '''Set the length in the parametric description of the given tool number.'''
        pass

    @classmethod
    def set_tool_radius(cls, toolnum: int, radius: float) -> None:
        '''Set the radius in the parametric description of the given tool number.'''
        pass

    @classmethod
    def spindle_speed_ccw(cls, speed: float) -> None:
        '''Set counter-clockwise spindle speed.'''
        pass

    @classmethod
    def spindle_speed_cw(cls, speed: float) -> None:
        '''Set clockwise spindle speed.'''
        pass

    @classmethod
    def spindle_speed_unit(cls, unit: str) -> None:
        '''Set spindle speed unit.'''
        pass

    @classmethod
    def workpiece(cls, filename: StrOrBytesPath) -> Object:
        '''Import STEP CAD file as workpiece object.'''
        pass

    @classmethod
    def workplan_setup(
            cls, workplan: Object,
	    x: float, y: float, z: float,
	    i: float = 0, j: float = 0, k: float = 1,
	    a: float = 1, b: float = 0, c: float = 0) -> None:
        '''Add setup placement to workplan.'''
        pass


    
# ==================================================
# TOLERANCE API CLASS
#
class ToleranceAPI:
    '''High level API for tolerance related operations'''

    @classmethod
    def add_workpiece_hardness(cls, workpiece: Object, value: float, measuring_method: str) -> Object:
        '''Add hardness description to workpiece, return hardness object.'''
        pass

    @classmethod
    def add_workpiece_material(cls, workpiece: Object, material: str, material_standard: str) -> Object:
        '''Add material description to workpiece, return material object.'''
        pass

        @classmethod
    def add_workpiece_treatment(cls, workpiece: Object, treatment_type: str, value: str) -> Object:
        '''Add a treatment description to workpiece, return treatment object.'''
        pass

    @classmethod
    def add_workpiece_treatment_heat(cls, workpiece: Object, value: str) -> Object:
        '''Add a heat treatment description to workpiece, return treatment object'''
        pass
    
    @classmethod
    def get_tolerance_face_all(cls, tolerance: Object) -> List[Object]:
        '''Get all faces associated with a tolerance'''
        pass

    @classmethod
    def get_tolerance_origin_face_all(cls, tolerance: Object) -> List[Object]:
        '''Get all faces associated with the origin of a tolerance dimension'''
        pass

    @classmethod
    def get_tolerance_target_face_all(cls, tolerance: Object) -> List[Object]:
        '''Get all faces associated with the target of a tolerance dimension'''
        pass

    @classmethod
    def plan_additive_layer(
            cls, workplan: Object,
	    shape: Object,
	    index: int = -1,
            name: str = '',
            pre_contour: bool = False,
            post_contour: bool = True,
            theta_interlayer_rotation: float = 69,
            overlap: float = 0.25,
            layer_thickness: float = 0.004,
            hatch_space: float = 0.0085,
            theta_island_rotation: float = 90,
            rectangle_length: float = 1.25,
            rectangle_width: float = 0.75,
            first_layer: int = -1,
            last_layer: int = -1) -> Object:
        '''Create a workplan with additive toolpaths'''
        pass

    @classmethod
    def plan_any_probing(
            cls, workplan: Object,
	    index: int,
            name: str,
            face: Object,
	    point_count: int,
	    edge_tol: float) -> Object:
        '''Create probing workplan to test position and profile of any surface.'''
        pass

    @classmethod
    def plan_bspline_probing(
            cls, workplan: Object,
	    index: int,
            name: str,
            face: Object,
	    num_u_points: int,
	    num_v_points: int) -> Object:
        '''Create probing workplan to test position and profile of bspline surface.'''
        pass

    @classmethod
    def plan_set_delta_uv(cls, delta_u: float, delta_v: float) -> None:
        '''Adjust starting U and V values by delta.'''
        pass

    @classmethod
    def plan_set_start_clear(cls, start: float, clear: float) -> None:
        '''Define distance from start to touch point, and clearance height.'''
        pass

    @classmethod
    def plan_using_clear_always(cls) -> None:
        '''Use clear plane for every probe.'''
        pass

    @classmethod
    def plan_using_clear_at_start_end_only(cls) -> None:
        '''Use clear plane only at first and last probe.'''
        pass

    @classmethod
    def plan_using_normal(cls) -> None:
        '''Probe surface along normal (three axis move).'''
        pass

    @classmethod
    def plan_using_x_and_y(cls) -> None:
        '''Probe allows simultaneous two axis (X+Y) moves.'''
        pass

    @classmethod
    def plan_using_x_or_y(cls) -> None:
        '''Probe allows one axis (X or Y) moves.'''
        pass
    
    @classmethod
    def plan_using_z_axis(cls) -> None:
        '''Probe surface by moving in Z, then in XY plane.'''
        pass

    @classmethod
    def set_tolerance_name_in_workpiece(cls, workpiece: Object, index: int, name: str) -> None:
        '''Assign name to tolerance by position in list'''
        pass


class Vec:
    '''Point/Direction Vector'''

    @classmethod
    def cross(self, v1: Sequence[float], v2: Sequence[float]) -> List[float]:
        '''Return cross product of two 3D vectors, v1 x v2'''
        pass

    @classmethod
    def diff(self, v1: Sequence[float], v2: Sequence[float]) -> List[float]:
        '''Return difference of two 3D vectors, v1-v2'''
        pass

    @classmethod
    def dot(self, v1: Sequence[float], v2: Sequence[float]) -> float:
        '''Return dot product of two 3D vectors, v1 . v2'''
        pass
    
    @classmethod
    def is_equal(self, v1: Sequence[float], v2: Sequence[float], epsilon: float = None) -> bool:
        '''Compare 3D vectors with an epsilon tolerance'''
        pass
    
    @classmethod
    def is_zero(self, v1: Sequence[float], epsilon: float = None) -> bool:
        '''Test if 3D vector zero with an epsilon tolerance'''
        pass
    
    @classmethod
    def length(self, v1: Sequence[float]) -> float:
        '''Return length of a 3D vector'''
        pass
    
    @classmethod
    def negate(self, v1: Sequence[float]) -> List[float]:
        '''Return negation of a 3D vector, -v1'''
        pass
    
    @classmethod
    def normalize(cls, v1: Sequence[float]) -> List[float]:
        '''Return normalized 3D vector'''
        pass
    
    @classmethod
    def scale(self, v1: Sequence[float], scale: float) -> List[float]:
        '''Return scaled 3D vector'''
        pass
    
    @classmethod
    def sum(self, v1: Sequence[float], v2: Sequence[float]) -> List[float]:
        '''Return sum of two 3D vectors, v1+v2'''
        pass



class Xform:
    '''Transform Matrix (4x4)'''

    @classmethod
    def apply(self, xf: Sequence[float], pnt: Sequence[float]) -> List[float]:
        '''Return point in new location resulting from matrix multiply to apply transform to a point'''
        pass

    @classmethod
    def apply_dir(self, xf: Sequence[float], dir: Sequence[float]) -> List[float]:
        '''Return direction in new orientation resulting from matrix multiply that applies transform, ignoring any origin change'''
        pass

    @classmethod
    def compose(self, outer_xf: Sequence[float], inner_xf: Sequence[float]) -> List[float]:
        '''Return matrix resulting from matrix multiply that applies outer transform matrix to an inner matrix'''
        pass

    @classmethod
    def compose_rotation(
            self, xf: Sequence[float],
            axis: Sequence[float],
            origin: Sequence[float],
            angle: float,
            angle_unit: RoseUnit = RoseUnit.RAD
    ) -> List[float]:
        '''Return matrix resulting from rotation applied to a source matrix, given an axis, angle and origin'''
        pass

    @classmethod
    def compose_scale(self, xf: Sequence[float], scale: float) -> List[float]:
        '''Return matrix resulting from scaling applied to a source matrix'''
        pass

    
    @classmethod
    def det(self, xf: Sequence[float]) -> float:
        '''Return determinant of the 4x4 transform matrix'''
        pass

    @classmethod
    def get_euler_angles(self, xf: Sequence[float], angle_unit: RoseUnit = RoseUnit.RAD) -> Tuple[float,float,float]
        '''Return Euler angles for the rotation portion of transform, computed by ZXZ convention'''
        pass
    
    @classmethod
    def identity(self) -> List[float]:
        '''Return identity matrix'''
        pass

    @classmethod
    def inverse(self, xf: Sequence[float]) -> List[float]:
        '''Return inverse of transform, or None if no inverse can be found'''
        pass


    @classmethod
    def is_dir_identity(self, xf: Sequence[float], epsilon: float = None) -> bool:
        '''Test if direction part of transform is identity matrix within an epsilon'''
        pass

    @classmethod
    def is_identity(self, xf: Sequence[float], epsilon: float = None) -> bool:
        '''Test if transform is the identity matrix within an epsilon'''
        pass

    @classmethod
    def is_equal(self, xf1: Sequence[float], xf2: Sequence[float], epsilon: float = None) -> bool:
        '''Test if two transform are equal within an epsilon'''
        pass
    
    @classmethod
    def normalize(self, xf: Sequence[float]) -> List[float]:
        '''Return transform matrix with normalized direction vectors'''
        pass
    
    @classmethod
    def normalize(self, xf: Sequence[float]) -> List[float]:
        '''Return transform matrix with normalized direction vectors'''
        pass

    @overload    
    @classmethod
    def scale_dirs(self, xf: Sequence[float], scale: float) -> List[float]: ...
    @overload    
    @classmethod
    def scale_dirs(self, xf: Sequence[float], scale_x: float, scale_y: float, scale_z: float) -> List[float]:
        '''Return transform matrix with scaled direction vectors'''
        pass
    
    @classmethod
    def transform_to(self, src: Sequence[float], dst: Sequence[float]) -> List[float]:
        '''Return transform matrix that moves items in src to dst coordinate system'''
        pass

    @classmethod
    def translate(self, xf: Sequence[float], x: float, y: float, z: float) -> List[float]:
        '''Return transform matrix resulting from translation of matrix in XYZ'''
        pass

    @classmethod
    def transpose(self, xf: Sequence[float]) -> List[float]:
        '''Return transform matrix resulting from transpose of matrix'''
        pass



    # rose_xform_put_alldirs()
# rose_xform_put_cto()
# rose_xform_put_dirs()
# rose_xform_put_euler_angles()
# rose_xform_put_frustrum()
# rose_xform_put_identity()
# rose_xform_put_origin()
# rose_xform_put_ortho()
# rose_xform_put_rotation()
# rose_xform_put_xdir()
# rose_xform_put_ydir()
# rose_xform_put_zdir()

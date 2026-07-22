from enum import IntEnum

COUNTER = 0

class CarConst(IntEnum):
    """Indices mapping properties within the cars data matrix."""
    REACTION_TIME = 2
    DISTANCE_REACTION = 50
    SEGMENT_REACTION = 10
    
class AnimationConst(IntEnum):
    """Constants for animations"""
    FACTOR = 600
    
class PartIndex(IntEnum):
    """Indices mapping properties within the parts data matrix."""
    ZONES = 0
    LENGTH = 1
    MAX_SPEEDS = 2
    
class SegmentIndex(IntEnum):
    """Segment data constants."""
    SPEED = 0
    LENGTH = 1
    ICON = 2
    COLOR = 3
    
class SegmentTypes:
    """Types of road parts"""
    SEGMENTS = {
        "highway": (36, 800, "🟩 ", (0, 1, 0)),
        "road": (25, 500, "🟨 ", (1, 1, 0)),
        "city": (14, 250, "🟧 ", (1, 165/255, 0)),
        "school": (8, 50, "🟥 ",	(1, 0, 0)),
        "construction": (2, 10, "🟪 ",  (218/255,112/255,214/255))
    }
    



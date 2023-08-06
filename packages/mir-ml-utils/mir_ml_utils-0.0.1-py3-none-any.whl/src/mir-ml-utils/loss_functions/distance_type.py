"""module distance_type. Provides an enumeration
of the various distance metrics the mir_project-engine implements

"""

import enum


class DistanceType(enum.Enum):
    """Enumeration of the various distance types
    implemented by the mir_project-engine

    """

    INVALID = 0
    L2_DISTANCE = 1

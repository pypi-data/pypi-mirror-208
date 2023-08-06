from enum import Enum
from typing import Any, Dict, List, Optional

import pydantic

from classiq.interface.helpers.versioned_model import VersionedModel


class CytoScapePosition(pydantic.BaseModel):
    x: int = pydantic.Field(
        default=..., description="X coordinate in the Cytoscape View"
    )
    y: int = pydantic.Field(
        default=..., description="Y coordinate in the Cytoscape View"
    )


class CytoScapeEdgeData(pydantic.BaseModel):
    source: str = pydantic.Field(
        default=..., description="the Id of the Node that is the Source of the edge"
    )
    target: str = pydantic.Field(
        default=..., description="the Id of the Node that is the Target the edge"
    )


class CytoScapeEdge(pydantic.BaseModel):
    data: CytoScapeEdgeData = pydantic.Field(
        default=..., description="Edge's Data, mainly the source and target of the Edge"
    )


class CytoScapeNode(pydantic.BaseModel):
    data: Dict[str, Any] = pydantic.Field(
        default=...,
        description="Data of the Node, such as label, and color, can be of free form",
    )
    position: Optional[CytoScapePosition] = pydantic.Field(
        default=..., description="Position of the Node to be rendered in Cytocape"
    )


class CytoScapeGraph(pydantic.BaseModel):
    nodes: List[CytoScapeNode] = pydantic.Field(
        default_factory=list,
        description="Nodes of the Graph",
    )
    edges: List[CytoScapeEdge] = pydantic.Field(
        default_factory=list,
        description="Edges of the Graph",
    )


class ConnectivityErrors(str, Enum):
    EMPTY = ""
    DEVICE_NOT_AVAILABLE_ERROR_MSG = (
        "HW connectivity map temporarily unavailable for this Device"
    )


class HardwareConnectivityGraphResult(VersionedModel):
    graph: Optional[CytoScapeGraph] = pydantic.Field(
        default=...,
        description="The Cytoscape graph in the desired Structure for the FE",
    )
    error: ConnectivityErrors = pydantic.Field(
        default=ConnectivityErrors.EMPTY,
        description="Any errors encountered while generating the graph",
    )

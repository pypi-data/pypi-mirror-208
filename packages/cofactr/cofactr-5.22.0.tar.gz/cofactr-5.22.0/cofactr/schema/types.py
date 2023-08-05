"""Types for use in schema definitions."""
# Standard Modules
from typing import Any, List, Literal, Optional, TypedDict
from typing_extensions import NotRequired


class OfferCorrection(TypedDict):
    """Offer correction."""

    correct_value: Any
    original_value: Any
    detail: Optional[str]
    created_at: str


class Document(TypedDict):
    """Document."""

    label: str
    url: str
    filename: str


class Completion(TypedDict):
    """Autocomplete prediction."""

    id: str
    label: str


TerminationType = Literal[
    "other",
    "SMT",
    "THT",
    "pressed fit",
    "hybrid of SMT and THT",
    "hybrid of pressed fit and SMT",
    "hybrid of pressed fit and THT",
]


class ManufacturerInV0(TypedDict):
    """Manufacturer input."""

    custom_label: NotRequired[Optional[str]]
    custom_id: NotRequired[Optional[str]]
    id: NotRequired[Optional[str]]


class ClassificationInV0(TypedDict):
    """Classification input."""

    custom_label: NotRequired[Optional[str]]
    custom_id: NotRequired[Optional[str]]
    id: NotRequired[Optional[str]]


class PartInV0(TypedDict):
    """Part input."""

    owner_id: str

    mpn: str
    alt_mpns: NotRequired[Optional[List[str]]]
    custom_id: NotRequired[Optional[str]]
    mfr: NotRequired[Optional[ManufacturerInV0]]

    classification: NotRequired[Optional[ClassificationInV0]]
    description: NotRequired[Optional[str]]
    msl: NotRequired[Optional[str]]
    package: NotRequired[Optional[str]]
    terminations: NotRequired[Optional[int]]
    termination_type: NotRequired[Optional[TerminationType]]

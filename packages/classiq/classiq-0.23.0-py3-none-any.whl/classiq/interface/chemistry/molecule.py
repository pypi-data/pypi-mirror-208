from typing import List

import pydantic

from classiq.interface.chemistry.elements import ELEMENTS
from classiq.interface.helpers.custom_pydantic_types import AtomType
from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)


class Molecule(HashablePydanticBaseModel):
    atoms: List[AtomType] = pydantic.Field(
        description="A list of atoms each containing the string of the atom's symbol and a list of its (x,y,z) location; for example [('H', (0.0, 0.0, 0.0)), ('H', (0.0, 0.0, 0.735))]."
    )
    spin: pydantic.NonNegativeInt = pydantic.Field(
        default=1, description="spin of the molecule"
    )
    charge: pydantic.NonNegativeInt = pydantic.Field(
        default=0, description="charge of the molecule"
    )

    @pydantic.validator("atoms", each_item=True)
    def _validate_atoms(cls, atom: AtomType) -> AtomType:
        if len(atom) != 2:
            raise ValueError(
                "each atom should be a list of two entries: 1) name pf the elemnt (str) 2) list of its (x,y,z) location"
            )
        if type(atom[0]) != str:
            raise ValueError(
                f"atom name should be a string. unknown element: {atom[0]}."
            )
        if atom[0] not in ELEMENTS:
            raise ValueError(f"unknown element: {atom[0]}.")
        if len(atom[1]) != 3:
            raise ValueError(
                f"location of the atom is of length three, representing the (x,y,z) coordinates of the atom, error value: {atom[1]}"
            )
        for idx in atom[1]:
            if type(idx) != float and type(idx) != int:
                raise ValueError(
                    f"coordinates of the atom should be of type float. error value: {idx}"
                )
        return atom

    class Config:
        frozen = True

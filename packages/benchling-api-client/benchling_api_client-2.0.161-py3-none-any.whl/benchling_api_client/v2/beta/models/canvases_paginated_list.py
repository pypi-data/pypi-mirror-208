from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.canvas import Canvas
from ..types import UNSET, Unset

T = TypeVar("T", bound="CanvasesPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class CanvasesPaginatedList:
    """  """

    _canvases: Union[Unset, List[Canvas]] = UNSET
    _next_token: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("canvases={}".format(repr(self._canvases)))
        fields.append("next_token={}".format(repr(self._next_token)))
        return "CanvasesPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        canvases: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._canvases, Unset):
            canvases = []
            for canvases_item_data in self._canvases:
                canvases_item = canvases_item_data.to_dict()

                canvases.append(canvases_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if canvases is not UNSET:
            field_dict["canvases"] = canvases
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_canvases() -> Union[Unset, List[Canvas]]:
            canvases = []
            _canvases = d.pop("canvases")
            for canvases_item_data in _canvases or []:
                canvases_item = Canvas.from_dict(canvases_item_data, strict=False)

                canvases.append(canvases_item)

            return canvases

        try:
            canvases = get_canvases()
        except KeyError:
            if strict:
                raise
            canvases = cast(Union[Unset, List[Canvas]], UNSET)

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        try:
            next_token = get_next_token()
        except KeyError:
            if strict:
                raise
            next_token = cast(Union[Unset, str], UNSET)

        canvases_paginated_list = cls(
            canvases=canvases,
            next_token=next_token,
        )

        return canvases_paginated_list

    @property
    def canvases(self) -> List[Canvas]:
        if isinstance(self._canvases, Unset):
            raise NotPresentError(self, "canvases")
        return self._canvases

    @canvases.setter
    def canvases(self, value: List[Canvas]) -> None:
        self._canvases = value

    @canvases.deleter
    def canvases(self) -> None:
        self._canvases = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET

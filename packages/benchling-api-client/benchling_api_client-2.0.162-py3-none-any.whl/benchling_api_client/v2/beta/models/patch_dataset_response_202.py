from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="PatchDatasetResponse_202")


@attr.s(auto_attribs=True, repr=False)
class PatchDatasetResponse_202:
    """  """

    def __repr__(self):
        fields = []
        return "PatchDatasetResponse_202({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        src_dict.copy()

        patch_dataset_response_202 = cls()

        return patch_dataset_response_202

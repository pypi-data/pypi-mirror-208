from typing import NamedTuple, Union, Dict, Any, List
from enum import Enum
import json, base64


class ModelConversionInputType(Enum):
    Float16 = "float16"
    Float32 = "float32"
    Float64 = "float64"
    Int16 = "int16"
    Int32 = "int32"
    Int64 = "int64"
    UInt8 = "uint8"
    UInt16 = "uint16"
    UInt32 = "uint32"
    UInt64 = "uint64"
    Boolean = "bool"
    Double = "double"


class ConvertKerasArguments(NamedTuple):
    name: str
    comment: Union[str, None]
    input_type: ModelConversionInputType
    dimensions: List[Union[None, int, float]]

    def to_dict(self) -> Dict[str, Any]:
        base = self._asdict()
        base["input_type"] = self.input_type.value
        return base


class ConvertSKLearnArguments(NamedTuple):
    name: str
    number_of_columns: int
    input_type: ModelConversionInputType
    comment: Union[str, None]

    def to_dict(self) -> Dict[str, Any]:
        base = self._asdict()
        base["input_type"] = self.input_type.value
        return base


class ConvertXGBoostArgs(NamedTuple):
    name: str
    number_of_columns: int
    input_type: ModelConversionInputType
    comment: Union[str, None]

    def to_dict(self) -> Dict[str, Any]:
        base = self._asdict()
        base["input_type"] = self.input_type.value
        return base


ModelConversionArguments = Union[
    ConvertKerasArguments, ConvertSKLearnArguments, ConvertXGBoostArgs
]


class ModelConversionSource(Enum):
    KERAS = "keras"
    XGBOOST = "xgboost"
    SKLEARN = "sklearn"


class ModelConversionGenericException(Exception):
    pass


class ModelConversionFailure(Exception):
    pass


class ModelConversionUnsupportedType(Exception):
    pass


class ModelConversionSourceFileNotPresent(Exception):
    pass

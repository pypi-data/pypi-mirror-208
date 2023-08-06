from typing import Generic, List, TypeVar, Union

from pydantic import BaseModel, Extra
from pydantic.fields import Field, ModelField
from pydantic.generics import GenericModel

Attribute = TypeVar("Attribute")

AssetAttributes_ = TypeVar("AssetAttributes_")

AssetPresets_ = TypeVar("AssetPresets_")


class SchemaBaseModel(BaseModel):
    class Config:
        extra = Extra.forbid


class AttributesList(list, Generic[Attribute]):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Union[Attribute, List[Attribute]], field: ModelField) -> List[Attribute]:
        if not v:
            return None
        if not isinstance(v, list):
            v = [v]
        return [field.type_(v_) for v_ in v]


class AssetAttributes(BaseModel):
    class Config:
        frozen = True


class Asset(SchemaBaseModel, GenericModel, Generic[AssetAttributes_]):
    id: str
    attributes: AssetAttributes_ = Field(default=None)

    def dict(self, *args, **kwargs):
        kwargs["exclude"] = {"attributes"}
        return super().dict(*args, **kwargs)


class PresetAsset(SchemaBaseModel, GenericModel, Generic[AssetAttributes_, AssetPresets_]):
    id: str
    attributes: AssetAttributes_ = Field(default=None)
    presets: AssetPresets_ = Field(default=None)

    def dict(self, *args, **kwargs):
        kwargs["exclude"] = {"attributes", "presets"}
        return super().dict(*args, **kwargs)

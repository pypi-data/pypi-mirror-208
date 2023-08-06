from typing import List, Optional

from datagen_protocol.schema import humans as humans_core_schema
from datagen_protocol.schema.environment import Background, Camera, Light, Wavelength
from datagen_protocol.schema.humans import Human
from datagen_protocol.validation.humans.accessories import Accessories as ValidationAccessories
from pydantic import validator


class HumanDatapoint(humans_core_schema.HumanDatapoint):
    accessories: Optional[ValidationAccessories]

    @validator("lights", always=True)
    def lights_and_not_nir_mutually_exclusive(cls, lights: List[Light], values) -> List[Light]:
        has_lights = lights is not None and len(lights) > 0
        if has_lights and not cls._is_set_to_nir(values["camera"]):
            raise ValueError("Lights are only relevant if the camera is using 'nir' wavelength")
        return lights

    @validator("background", always=True)
    def background_and_nir_mutually_exclusive(cls, background, values) -> Background:
        if background is not None and cls._is_set_to_nir(values["camera"]):
            raise ValueError("Background is only relevant if the camera is not using 'nir' wavelength")
        return background

    @staticmethod
    def _is_set_to_nir(camera: Camera) -> bool:
        return camera.intrinsic_params.wavelength == Wavelength.NIR

    @validator("accessories", always=True)
    def mask_and_facial_hair_mutually_exclusive(
        cls, accessories: ValidationAccessories, values: list
    ) -> ValidationAccessories:
        if accessories and accessories.mask and cls._has_facial_hair(values["human"]):
            raise ValueError("Facial hair and masks are mutually exclusive")
        return accessories

    @staticmethod
    def _has_facial_hair(human: Human) -> bool:
        return bool(human.head.facial_hair)

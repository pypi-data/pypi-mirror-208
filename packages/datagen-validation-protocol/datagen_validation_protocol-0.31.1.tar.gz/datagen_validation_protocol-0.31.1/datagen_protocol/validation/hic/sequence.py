from datagen_protocol.schema import DataSequence as CoreDataSequence
from pydantic import root_validator


class DataSequence(CoreDataSequence):
    @root_validator()
    def validate_background_or_lights(cls, values):
        if values.get("background") is None and values.get("lights") is None:
            raise ValueError("No light source defined - either a background or lights must be provided")
        return values

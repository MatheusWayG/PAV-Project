from pydantic import BaseModel, ConfigDict, field_validator

class BaseSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("*", mode="before")
    @classmethod
    def reject_null_characters(cls, value):
        if isinstance(value, str) and "\x00" in value:
            raise ValueError("Text cannot contain null characters.")
        
        return value
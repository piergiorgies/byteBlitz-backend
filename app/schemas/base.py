from pydantic import BaseModel, ConfigDict

# Request objects definition
class BaseRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        str_strip_whitespace=True
        )
    
# Response objects definition
class BaseResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        )

class BaseListResponse(BaseResponse):
    count: int

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        )
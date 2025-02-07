from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, model_validator

ZoteroLibraryType = Literal["user", "group"]


class ZoteroLiberary(BaseModel):
    type: ZoteroLibraryType = Field(
        description="The type of library ('user', 'group')."
    )
    name: str = Field(description="The library ID.")


class ZoteroTag(BaseModel):
    tag: str = Field(description="Tag name.")
    type: Optional[int] = Field(description="Tag type.")


class ZoteroCreator(BaseModel):
    creatorType: str
    firstName: str
    lastName: str


class ZoteroData(BaseModel):
    key: str = Field(description="The item key.")
    version: int = Field(1, description="The item version.")
    parentItem: Optional[str] = Field(default="Key of the parent item, if any.")
    title: str = Field("The title of the item.")
    itemType: str = Field(
        "Type of item (e.g. 'attachment', 'book')"
    )  # todo enhance the typing
    note: str = Field(default="", description="A note associated with the item.")
    contentType: Optional[str] = Field(default="")
    filename: Optional[str] = Field(
        default="", description="The filename of the item, if applicable."
    )
    mtime: Optional[int] = Field(
        description="The modification time of the item, if applicable.", default=None
    )
    tags: List[ZoteroTag] = Field(
        description="Tag associated with the item.", default_factory=list
    )
    language: str = Field(default="en")
    creators: List[ZoteroCreator] = Field(default_factory=list)


class ZoteroItem(BaseModel):
    key: str = Field(description="The unique item key.")
    version: int = Field(description="The item version", default=1)
    library: ZoteroLiberary = Field(description="The library that the item belongs to.")
    data: ZoteroData = Field(description="The actual dataof the item.")

    @model_validator(mode="before")
    def check_data_consistency(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values.get("data", {}).get("linkMode") == "linked_url" and not values.get(
            "data", {}
        ).get("url"):
            raise ValueError("If linkMode is 'linked_url', a URL must be provided.")
        return values

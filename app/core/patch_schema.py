from typing import ClassVar

from pydantic import BaseModel, model_validator


class PatchSchema(BaseModel):
  """Base for PATCH bodies that rejects empty updates and invalid nulls."""

  nullable_fields: ClassVar[frozenset[str]] = frozenset()

  @model_validator(mode='after')
  def validate_patch(self):
    if not self.model_fields_set:
      raise ValueError('At least one field must be provided')
    for field in self.model_fields_set - self.nullable_fields:
      if getattr(self, field) is None:
        raise ValueError(f'{field} cannot be null')
    return self

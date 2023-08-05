""""Model field validators for the community app."""


from typing import Any, ClassVar, Optional

from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class HTMLMaxLengthValidator:
    """A validator that checks the length of the HTML text."""

    max_length: int
    message_template: ClassVar[
        str
    ] = "Only {max_length} characters are allowed."
    message: str

    def __init__(self, max_length: int, message: Optional[str] = None) -> None:
        self.max_length = max_length
        message = message or self.message_template
        self.message = message.format(max_length=max_length)

    def __call__(self, value: str) -> Any:
        soup = BeautifulSoup(value, "html.parser")
        length = len(soup.text)
        if length > 4000:
            raise ValidationError(
                "Only 4000 characters are allowed in the abstract!"
            )
        return value

    def __eq__(self, other):
        return (
            isinstance(other, HTMLMaxLengthValidator)
            and self.max_length == other.max_length
            and self.message == other.message
        )

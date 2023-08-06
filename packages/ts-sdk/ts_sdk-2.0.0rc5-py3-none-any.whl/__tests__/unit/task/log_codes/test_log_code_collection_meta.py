import pytest

from ts_sdk.task.log_codes.log_code import LogCode
from ts_sdk.task.log_codes.log_code_collection_meta import (
    LogCodeCollectionMeta,
    LogCodeConfigurationError,
)


def test_overriding_code_messages() -> None:
    """
    Assert that an error is raised when the child class contains a member whose code_message
    is the same as that in its parent class.
    """

    # Arrange
    class FooCodes(metaclass=LogCodeCollectionMeta):
        foo = LogCode(code_message="Foo", code=1000)

    # Act and Assert
    with pytest.raises(LogCodeConfigurationError, match="Foo"):

        class BarCodes(FooCodes):
            bar = LogCode(code_message="Bar", code=1001)
            baz = LogCode(code_message="Foo", code=1002)


def test_overriding_ids() -> None:
    """
    Assert that an error is raised when the child class contains a member whose log code
    ID is the same as that in its parent class.
    """

    # Arrange
    class FooCodes(metaclass=LogCodeCollectionMeta):
        foo = LogCode(code_message="Foo", code=1000)

    # Act and Assert
    with pytest.raises(LogCodeConfigurationError, match="1000"):

        class BarCodes(FooCodes):
            bar = LogCode(code_message="Bar", code=1000)
            baz = LogCode(code_message="Baz", code=1001)


def test_slug_name_too_long() -> None:
    """Assert that an code_message whose name is longer than the allowed length raises an error."""
    # no Arrange
    # Act and Assert
    with pytest.raises(LogCodeConfigurationError):

        class ClassUnderTest(metaclass=LogCodeCollectionMeta):
            slug_is_longer_than_thirty_two_characters = LogCode(
                "SlugIsLongerThanThirtyTwoCharacters", code=1000
            )


@pytest.mark.parametrize(
    "code_message",
    ["slugIsNotPascalCase", "slug_is_not_pascal_case", "SlugIsNotPascalCaseAB"],
    ids=["camelCase", "snake_case", "contains-sequential-capital-letters"],
)
def test_slug_not_pascal_case(code_message: str) -> None:
    """Assert that a code_message that's not PascalCase is flagged as invalid."""

    # no Arrange
    # Act and Assert
    class ClassUnderTest(metaclass=LogCodeConfigurationError):
        log_code = LogCode(code_message, code=1000)

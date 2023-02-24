from pydantic import constr
from pydantic_core import core_schema
from typing import ClassVar, Any

from .country import CountryAlpha2


class IBAN(str):
    """
    based on https://en.wikipedia.org/wiki/International_Bank_Account_Number
    """
    __strip_whitespace: ClassVar[bool] = True
    __max_length: ClassVar[int] = 34

    country_code: CountryAlpha2
    check_digits: constr(min_length=2, max_length=2)
    bban: constr(max_length=30)

    def __init__(self, iban: str):
        print('iban', iban)
        self.country_code = CountryAlpha2._validate(iban[:2])
        # todo: validation algorithm https://en.wikipedia.org/wiki/International_Bank_Account_Number#Algorithms

    @classmethod
    def __get_pydantic_core_schema__(cls, **_kwargs: Any) -> core_schema.FunctionSchema:
        return core_schema.function_after_schema(
            core_schema.str_schema(
                max_length=cls.__max_length,
                strip_whitespace=cls.__strip_whitespace,
            ),
            cls._validate,
        )

    @classmethod
    def _validate(cls, __input_value: str, **_kwargs: Any) -> 'IBAN':
        return cls(__input_value)

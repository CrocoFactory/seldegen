from typing import Union

__all__ = ['Context']


class Context:
    """The class, containing context variables"""
    __default_timeout = 15

    @classmethod
    def default_timeout(cls) -> float:
        """The default timeout to interact with elements"""
        return cls.__default_timeout

    @classmethod
    def set_default_timeout(cls, value: float):
        """Setter for the default timeout"""
        if isinstance(value, Union[float, int]):
            cls.__default_timeout = value
        else:
            raise TypeError('Default timeout must be float or int')
        
import typing, abc
from System import Array_1
from System.IO import TextWriter

class WebUtility(abc.ABC):
    @staticmethod
    def UrlDecode(encodedValue: str) -> str: ...
    @staticmethod
    def UrlDecodeToBytes(encodedValue: Array_1[int], offset: int, count: int) -> Array_1[int]: ...
    @staticmethod
    def UrlEncode(value: str) -> str: ...
    @staticmethod
    def UrlEncodeToBytes(value: Array_1[int], offset: int, count: int) -> Array_1[int]: ...
    # Skipped HtmlDecode due to it being static, abstract and generic.

    HtmlDecode : HtmlDecode_MethodGroup
    class HtmlDecode_MethodGroup:
        @typing.overload
        def __call__(self, value: str) -> str:...
        @typing.overload
        def __call__(self, value: str, output: TextWriter) -> None:...

    # Skipped HtmlEncode due to it being static, abstract and generic.

    HtmlEncode : HtmlEncode_MethodGroup
    class HtmlEncode_MethodGroup:
        @typing.overload
        def __call__(self, value: str) -> str:...
        @typing.overload
        def __call__(self, value: str, output: TextWriter) -> None:...



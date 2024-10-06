"""grassplain.backends: code generation backends for grassplain"""

from dataclasses import dataclass
from typing import Protocol

from tomlantic import ModelBoundTOML

from .config import GrassplainConfigurationFile


class GrassplainEmitterProtocol(Protocol):
    config: ModelBoundTOML[GrassplainConfigurationFile]

    def __init__(self, config: ModelBoundTOML[GrassplainConfigurationFile]) -> None: ...

    def emit(self) -> str: ...


@dataclass
class GrassplainToPythonEmitter(GrassplainEmitterProtocol):
    config: ModelBoundTOML[GrassplainConfigurationFile]

    def build(self) -> str:
        return (
            "from typing import Callable, NamedTuple\n"
            "\n"
            "\n"
            "class GrassplainParsedArguments(NamedTuple):\n"
            "    demo: str = 'test'\n"
            "\n"
            "\n"
            "def parse_args(argv: list[str], version_function: Callable[[], str]) -> GrassplainParsedArguments:\n"
            "    return GrassplainParsedArguments()"
        )

    def emit(self) -> str:
        raise NotImplementedError()  # TODO
        return self.build()

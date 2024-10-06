from enum import Enum
from pathlib import Path
from sys import exit, stderr
from typing import Literal

from pydantic import BaseModel, Field
from tomlantic import ModelBoundTOML, TOMLValidationError
from tomlkit import TOMLDocument, loads


class GrassplainTargetLanguageEnum(str, Enum):
    PYTHON = "python"


GrassplainTargetLanguageType = Literal[GrassplainTargetLanguageEnum.PYTHON]


class GCFMetaSection(BaseModel):
    description: str = ""
    max_line_length: int = 80
    min_description_padding: int = 12
    max_description_length: int = 25
    target_language: GrassplainTargetLanguageType = GrassplainTargetLanguageEnum.PYTHON
    extra: dict[str, str] = {}


class GrassplainArgument(BaseModel):
    description: str
    number_of_arguments: int = 1


class GrassplainOption(BaseModel):
    description: str
    delimiter: str = ""
    default: str = ""


class GrassplainFlag(BaseModel):
    description: str
    short: str = ""
    default: int = 0


class GCFGlobalSection(BaseModel):
    arguments: dict[str, GrassplainArgument] = {}
    options: dict[str, GrassplainOption] = {}
    flags: dict[str, GrassplainFlag] = {}


class GCFSubcommandSection(BaseModel):
    description: str
    arguments: dict[str, GrassplainArgument] = {}
    options: dict[str, GrassplainOption] = {}
    flags: dict[str, GrassplainFlag] = {}

    # god bless pydantic supporting cyclic references
    subcommands: dict[str, "GCFSubcommandSection"] = {}


class GrassplainConfigurationFile(BaseModel):
    meta: GCFMetaSection = GCFMetaSection()
    global_: GCFGlobalSection = Field(alias="global", default=GCFGlobalSection())
    subcommand: dict[str, GCFSubcommandSection] = {}


def get_config_from_args(
    argv: list[str],
) -> tuple[Path, ModelBoundTOML[GrassplainConfigurationFile]]:
    if len(argv) < 2:
        print(
            f"error: no configuration file specified\n\nusage: {argv[0]} CONFIG",
            file=stderr,
        )
        exit(-1)

    config_path: Path = Path(argv[1])
    if not (config_path.exists() and config_path.is_file()):
        print(f"error: {config_path} does not exist", file=stderr)
        exit(-1)

    try:
        config_toml: TOMLDocument = loads(config_path.read_text(encoding="utf-8"))

    except Exception as e:
        print(
            f"error while parsing '{config_path}': {e} ({e.__class__.__name__})",
            file=stderr,
        )
        exit(-1)

    try:
        config_data: ModelBoundTOML[GrassplainConfigurationFile] = ModelBoundTOML(
            model=GrassplainConfigurationFile,
            document=config_toml,
            # handle_errors=False,
        )

    except TOMLValidationError as e:
        print(
            f"error while validating '{config_path}': {e}",
            sep="\n",
            file=stderr,
        )
        exit(-1)

    except Exception as e:
        print(
            f"error while validating '{config_path}': {e} ({e.__class__.__name__})",
            file=stderr,
        )
        exit(-1)

    return config_path, config_data

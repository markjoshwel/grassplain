from pathlib import Path
from pprint import pprint
from sys import argv, exit, stderr

from pydantic import BaseModel, Field
from tomlantic import ModelBoundTOML, TOMLValidationError
from tomlkit import TOMLDocument, loads


class GCFMetaSection(BaseModel):
    description: str = ""
    max_line_length: int = 80
    min_description_padding: int = 12
    max_description_length: int = 25
    extra: dict[str, str] = {}


class GCFArgument(BaseModel):
    description: str
    number_of: int = 1


class GCFOption(BaseModel):
    description: str
    number_of: int = 1
    default: str = ""


class GCFFlag(BaseModel):
    description: str
    short: str = ""
    default: int = 1


class GCFGlobalSection(BaseModel):
    arguments: dict[str, GCFArgument] = {}
    options: dict[str, GCFOption] = {}
    flags: dict[str, GCFFlag] = {}


class GCFSubcommandsSection(BaseModel):
    description: str
    arguments: dict[str, GCFArgument] = {}
    options: dict[str, GCFOption] = {}
    flags: dict[str, GCFFlag] = {}

    # god bless pydantic supporting cyclic references
    subcommands: dict[str, "GCFSubcommandsSection"] = {}


class GrassplainConfigurationFile(BaseModel):
    # [meta]
    # description = "<description here>"
    # max_line_length = 80
    # min_description_padding = 12
    # max_description_padding = 25
    #
    # [metas.extra]
    # "<header>" = "<body text>"
    #
    # [global.arguments."<argument name>"]
    # description = "<description here>"
    # number_of = 1  # set to -1 for unlimited
    #
    # [global.options."<option name>"]
    # description = "<description here>"
    # number_of = 1  # set to -1 for unlimited
    # default = ""  # when reading, if the value is empty, then the option was not set
    #
    # [global.flags."<long flag name>"]
    # short = "<short flag character>"
    # description = "<description here>"
    # default = 1
    #
    # [subcommands."<subcommand name>"]
    # description = "<description here>"
    #
    # # defined just like their global counterparts
    # [subcommands."<subcommand name>".arguments."<option name>"]
    # [subcommands."<subcommand name>".options."<option name>"]
    # [subcommands."<subcommand name>".flags."<option name>"]
    #
    # # subcommands can have subcommands
    # [subcommands."<subcommand name>".subcommands."<subcommand name>"]
    # description = "<description here>"

    meta: GCFMetaSection = GCFMetaSection()
    global_: GCFGlobalSection = Field(alias="global", default=GCFGlobalSection())
    subcommand: dict[str, GCFSubcommandsSection] = {}


def main() -> None:
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
        config: ModelBoundTOML[GrassplainConfigurationFile] = ModelBoundTOML(
            model=GrassplainConfigurationFile, document=config_toml
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

    # pprint(config.model.model_dump())


if __name__ == "__main__":
    main()

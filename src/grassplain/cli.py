"""grassplain: an (unserious) command line argument parser generator"""

from sys import argv, exit, stderr

from . import backends, config


def main() -> None:
    config_path, config_data = config.get_config_from_args(argv=argv)

    backend: backends.GrassplainEmitterProtocol
    config_target = config_data.model.meta.target_language

    if config_target == "python":
        backend = backends.GrassplainToPythonEmitter(config=config_data)

    else:
        print(f"error: unsupported target language '{config_target}'", file=stderr)
        exit(1)

    print(backend.emit())
    exit(0)


if __name__ == "__main__":
    main()

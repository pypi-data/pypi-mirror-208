# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2021-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations

import os
import typing as t
from configparser import ConfigParser as BaseConfigParser
from dataclasses import dataclass
from os import makedirs, path
from os.path import isfile, dirname

from .log import get_logger
from .path import RESOURCE_DIR, USER_ES7S_DATA_DIR
from .. import APP_NAME

_config: ConfigParser | None = None
_default_config: ConfigParser | None = None


@dataclass
class ConfigLoaderParams:
    default: bool = False


class ConfigParser(BaseConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._already_logged_options: t.Set[t.Tuple[str, str]] = set()

    def get(self, section: str, option: str, *args, **kwargs) -> t.Any:
        log_msg = f'Getting config value: {section}.{option}'
        result = None
        try:
            result = super().get(section, option, *args, **kwargs)
        except Exception:
            raise
        finally:
            log_msg += f' = ' + ('"'+result.replace('\n', ' ')+'"' if result else str(result))
            get_logger().debug(log_msg)
        return result

    def getintlist(self, section: str, option: str, *args, **kwargs) -> list[int]:
        try:
            return [*map(int, filter(None, self.get(section, option).splitlines()))]
        except ValueError as e:
            raise RuntimeError(f"Conversion to [int] failed for: {section}.{option}") from e

    def get_monitor_debug_mode(self) -> bool:
        if (env_var := os.getenv('ES7S_MONITOR_DEBUG', None)) is not None:
            return True if env_var != '' else False
        return self.getboolean("monitor", "debug", fallback=False)

    def get_indicator_debug_mode(self) -> bool:
        if (env_var := os.getenv('ES7S_INDICATOR_DEBUG', None)) is not None:
            return True if env_var != '' else False
        return self.getboolean("indicator", "debug", fallback=False)

    def set(self, section: str, option: str, value: str | None = ...) -> None:
        log_msg = f'Setting config value: {section}.{option} = "{value}"'
        get_logger().info(log_msg)

        super().set(section, option, value)

    def log(self, section: str, option: str, msg: str):
        logger = get_logger()


def get_app_config_yaml(name: str) -> dict|list:
    import yaml
    filename = f'{name}.yml'
    user_path = os.path.join(USER_ES7S_DATA_DIR, filename)

    if os.path.isfile(user_path):
        with open(user_path, 'rt') as f:
            return yaml.safe_load(f.read())
    else:
        import pkg_resources
        app_path = os.path.join(RESOURCE_DIR, filename)
        s = pkg_resources.resource_stream(APP_NAME, app_path).read()
        return yaml.safe_load(s)


def get_default_config_filepath() -> str:
    filename = 'es7s.conf.d'
    user_path = os.path.join(USER_ES7S_DATA_DIR, filename)

    if os.path.isfile(user_path):
        return user_path
    else:
        import pkg_resources
        app_path = os.path.join(RESOURCE_DIR, 'es7s.conf.d')
        get_logger(False).warning(
            f"Default config not found in user data dir, "
            f"loading from app data dir instead: '{app_path}'"
        )
        return pkg_resources.resource_filename(APP_NAME, app_path)


def get_user_config_filepath() -> str:
    import click
    user_config_path = click.get_app_dir(APP_NAME)
    return path.join(user_config_path, f"{APP_NAME}.conf")


def get_config(require=True) -> ConfigParser | None:
    if not _config:
        if require:
            raise RuntimeError("Config is uninitialized")
        return None
    return _config


def get_default_config() -> ConfigParser|None:
    return _default_config


def init_config(cfg_params=ConfigLoaderParams()):
    global _config, _default_config
    _config = ConfigParser(interpolation=None)  # @todo decorate and log gets/sets
    _default_config = ConfigParser(interpolation=None)

    default_config_filepath = get_default_config_filepath()
    user_config_filepath = get_user_config_filepath()

    if not isfile(user_config_filepath):
        reset_config(False)

    config_filepaths = [default_config_filepath]
    if not cfg_params.default:
        config_filepaths += [user_config_filepath]

    logger = get_logger(False)
    logger.info("Reading configs from: " + ", ".join(f'"{fp}"' for fp in config_filepaths))

    read_ok = _default_config.read(default_config_filepath)
    if len(read_ok) == 0:
        raise RuntimeError(f"Failed to read default config: {default_config_filepath}")

    read_ok = _config.read(config_filepaths)
    if not len(read_ok) == len(config_filepaths):
        read_failed = set(config_filepaths) - set(read_ok)
        logger.warning("Failed to read config(s): " + ", ".join(read_failed))


def reset_config(backup: bool = True) -> str|None:
    """ Return path to backup file, if any. """
    default_config_filepath = get_default_config_filepath()
    user_config_filepath = get_user_config_filepath()
    makedirs(dirname(user_config_filepath), exist_ok=True)

    get_logger().debug(f'Making default config in: "{user_config_filepath}"')

    user_backup_filepath = None
    if backup and os.path.exists(user_config_filepath):
        user_backup_filepath = user_config_filepath+'.bak'
        os.rename(user_config_filepath, user_backup_filepath)
        get_logger().info(f'Original file renamed to: "{user_backup_filepath}"')

    header = True
    with open(user_config_filepath, "wt") as user_cfg:
        with open(default_config_filepath, "rt") as default_cfg:
            for idx, line in enumerate(default_cfg.readlines()):
                if header and line.startswith(('#', ';', '\n')):
                    continue
                header = False

                prefix = ""
                if not line.startswith((";", "#", "[", "syntax-version", "\n")):
                    prefix = "# "
                elif line.startswith((";", "#", "\n")):
                    line = "\n"

                user_cfg.write(prefix + line)
                get_logger().trace(line.strip(), f"{idx+1}| ")

    return user_backup_filepath


def save_config():
    user_config_filepath = get_user_config_filepath()

    get_logger().debug(f'Writing config to: "{user_config_filepath}"')
    with open(user_config_filepath, "wt") as user_cfg:
        _config.write(user_cfg)

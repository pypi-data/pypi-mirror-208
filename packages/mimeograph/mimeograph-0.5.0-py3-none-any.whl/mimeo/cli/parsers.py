"""The Mimeo Parser module.

It exports two parser classes:
    * MimeoArgumentParser
        A custom ArgumentParser for the Mimeo CLI.
    * MimeoConfigParser
        A class parsing source Mimeo Configuration with Mimeo
        arguments.
"""
from __future__ import annotations

import json
import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

from mimeo import MimeoConfig
from mimeo.cli.exc import (EnvironmentNotFoundError,
                           EnvironmentsFileNotFoundError)

logger = logging.getLogger(__name__)

DEFAULT_ENVS_PATH = "mimeo.envs.json"


class MimeoArgumentParser(ArgumentParser):
    """A custom ArgumentParser for the Mimeo CLI."""

    def __init__(
            self,
    ):
        """Initialize MimeoArgumentParser class.

        Extends ArgumentParser constructor with a Mimeo CLI details.

        It provides the following command line interface:

        usage: mimeo [OPTIONS] paths

        Generate data based on a template

        positional arguments:
          paths                 take paths to Mimeo Configuration files

        optional arguments:
          -h, --help            show this help message and exit
          -v, --version         show program's version number and exit

        Mimeo Configuration arguments:
          -o {file,stdout,http}, --output {file,stdout,http}
                                overwrite the output/direction property
          -x {true,false}, --xml-declaration {true,false}
                                overwrite the output/xml_declaration property
          -i INDENT, --indent INDENT
                                overwrite the output/indent property
          -d DIRECTORY_PATH, --directory DIRECTORY_PATH
                                overwrite the output/directory_path property
          -f FILE_NAME, --file FILE_NAME
                                overwrite the output/file_name property
          -H HOST, --http-host HOST
                                overwrite the output/host property
          -p PORT, --http-port PORT
                                overwrite the output/port property
          -E ENDPOINT, --http-endpoint ENDPOINT
                                overwrite the output/endpoint property
          -U USERNAME, --http-user USERNAME
                                overwrite the output/username property
          -P PASSWORD, --http-password PASSWORD
                                overwrite the output/password property
          --http-method METHOD
                                overwrite the output/method property
          --http-protocol PROTOCOL
                                overwrite the output/protocol property
          -e ENVIRONMENT, --http-env ENVIRONMENT
                                overwrite the output http properties using a mimeo
                                env configuration
          --http-envs-file PATH
                                use a custom environments file
                                (by default: mimeo.envs.json)

        Logging arguments:
          --silent              disable INFO logs
          --debug               enable DEBUG mode
          --fine                enable FINE mode
        """
        super().__init__(
            prog="mimeo",
            description="Generate data based on a template",
            usage="%(prog)s [OPTIONS] paths")
        self._add_positional_arguments()
        self._add_mimeo_configuration_arguments()
        self._add_logging_arguments()

    def _add_positional_arguments(
            self,
    ):
        """Add positional arguments."""
        self.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s v0.5.0")
        self.add_argument(
            "paths",
            nargs="+",
            type=str,
            help="take paths to Mimeo Configuration files")

    def _add_mimeo_configuration_arguments(
            self,
    ):
        """Add arguments overwriting Mimeo Configuration."""
        mimeo_config_args = self.add_argument_group("Mimeo Configuration arguments")
        mimeo_config_args.add_argument(
            "-o",
            "--output",
            type=str,
            choices=["file", "stdout", "http"],
            help="overwrite the output/direction property")
        mimeo_config_args.add_argument(
            "-x",
            "--xml-declaration",
            type=str,
            choices=["true", "false"],
            help="overwrite the output/xml_declaration property")
        mimeo_config_args.add_argument(
            "-i",
            "--indent",
            type=int,
            help="overwrite the output/indent property")
        mimeo_config_args.add_argument(
            "-d",
            "--directory",
            type=str,
            metavar="DIRECTORY_PATH",
            help="overwrite the output/directory_path property")
        mimeo_config_args.add_argument(
            "-f",
            "--file",
            type=str,
            metavar="FILE_NAME",
            help="overwrite the output/file_name property")
        mimeo_config_args.add_argument(
            "-H",
            "--http-host",
            type=str,
            metavar="HOST",
            help="overwrite the output/host property")
        mimeo_config_args.add_argument(
            "-p",
            "--http-port",
            type=str,
            metavar="PORT",
            help="overwrite the output/port property")
        mimeo_config_args.add_argument(
            "-E",
            "--http-endpoint",
            type=str,
            metavar="ENDPOINT",
            help="overwrite the output/endpoint property")
        mimeo_config_args.add_argument(
            "-U",
            "--http-user",
            type=str,
            metavar="USERNAME",
            help="overwrite the output/username property")
        mimeo_config_args.add_argument(
            "-P",
            "--http-password",
            type=str,
            metavar="PASSWORD",
            help="overwrite the output/password property")
        mimeo_config_args.add_argument(
            "--http-method",
            type=str,
            metavar="METHOD",
            help="overwrite the output/method property")
        mimeo_config_args.add_argument(
            "--http-protocol",
            type=str,
            metavar="PROTOCOL",
            help="overwrite the output/protocol property")
        mimeo_config_args.add_argument(
            "-e",
            "--http-env",
            type=str,
            metavar="ENVIRONMENT",
            help="overwrite the output http properties using a mimeo env configuration")
        mimeo_config_args.add_argument(
            "--http-envs-file",
            type=str,
            metavar="PATH",
            help=f"use a custom environments file (by default: {DEFAULT_ENVS_PATH})")

    def _add_logging_arguments(
            self,
    ):
        """Add arguments customizing logs producing."""
        logging_args = self.add_argument_group("Logging arguments")
        logging_args_excl = logging_args.add_mutually_exclusive_group()
        logging_args_excl.add_argument(
            "--silent",
            action="store_true",
            help="disable INFO logs")
        logging_args_excl.add_argument(
            "--debug",
            action="store_true",
            help="enable DEBUG mode")
        logging_args_excl.add_argument(
            "--fine",
            action="store_true",
            help="enable FINE mode")


class MimeoConfigParser:
    """A class parsing source Mimeo Configuration with Mimeo arguments.

    Methods
    -------
    parse_config() -> MimeoConfig
        Parse a Mimeo Configuration using Mimeo arguments.
    """

    _ENVIRONMENT_PROPS = [MimeoConfig.OUTPUT_PROTOCOL_KEY,
                          MimeoConfig.OUTPUT_HOST_KEY,
                          MimeoConfig.OUTPUT_PORT_KEY,
                          MimeoConfig.OUTPUT_USERNAME_KEY,
                          MimeoConfig.OUTPUT_PASSWORD_KEY]

    _ENTRY_PATH_KEY = "entry_path"
    _GET_VALUE_KEY = "get_value"
    _ARGS_MAPPING = {
        "output": {
            "entry_path": [MimeoConfig.OUTPUT_KEY,
                           MimeoConfig.OUTPUT_DIRECTION_KEY],
        },
        "xml_declaration": {
            "entry_path": [MimeoConfig.OUTPUT_KEY,
                           MimeoConfig.OUTPUT_XML_DECLARATION_KEY],
            "get_value": lambda arg: arg.lower() == "true",
        },
        "indent": {
            "entry_path": [MimeoConfig.OUTPUT_KEY,
                           MimeoConfig.OUTPUT_INDENT_KEY],
        },
        "directory": {
            "entry_path": [MimeoConfig.OUTPUT_KEY,
                           MimeoConfig.OUTPUT_DIRECTORY_PATH_KEY],
        },
        "file": {
            "entry_path": [MimeoConfig.OUTPUT_KEY,
                           MimeoConfig.OUTPUT_FILE_NAME_KEY],
        },
        "http_method": {
            "entry_path": [MimeoConfig.OUTPUT_KEY,
                           MimeoConfig.OUTPUT_METHOD_KEY],
        },
        "http_protocol": {
            "entry_path": [MimeoConfig.OUTPUT_KEY,
                           MimeoConfig.OUTPUT_PROTOCOL_KEY],
        },
        "http_host": {
            "entry_path": [MimeoConfig.OUTPUT_KEY,
                           MimeoConfig.OUTPUT_HOST_KEY],
        },
        "http_port": {
            "entry_path": [MimeoConfig.OUTPUT_KEY,
                           MimeoConfig.OUTPUT_PORT_KEY],
        },
        "http_endpoint": {
            "entry_path": [MimeoConfig.OUTPUT_KEY,
                           MimeoConfig.OUTPUT_ENDPOINT_KEY],
        },
        "http_user": {
            "entry_path": [MimeoConfig.OUTPUT_KEY,
                           MimeoConfig.OUTPUT_USERNAME_KEY],
        },
        "http_password": {
            "entry_path": [MimeoConfig.OUTPUT_KEY,
                           MimeoConfig.OUTPUT_PASSWORD_KEY],
        },
    }

    def __init__(
            self,
            config: dict,
            args: Namespace,
    ):
        """Initialize MimeoConfigParser class.

        Parameters
        ----------
        config:
            A source config dictionary
        args
            Arguments parsed by MimeoArgumentParser
        """
        self._raw_config = config
        self._args = args

    def parse_config(
            self,
    ) -> MimeoConfig:
        """Parse a Mimeo Configuration using Mimeo arguments.

        The parsing is made according to the following rule:
        configuration is overwritten from the most general to the most
        specific setting. It means that, whenever CLI arguments
        are overlapping (e.g. -e and -u), first the higher-level
        customization is applied (e.g. environment) and then the lower
        one (e.g. username).

        Returns
        -------
        mimeo_config : MimeoConfig
            A parsed Mimeo Configuration

        Raises
        ------
        EnvironmentsFileNotFoundError
            If environments file does not exist.
        EnvironmentNotFoundError
            If the http environment is not defined in the environments file
        """
        logger.info("Parsing Mimeo Configuration")
        config = dict(self._raw_config)
        config = self._parse_with_http_environment(config)
        config = self._parse_with_specific_args(config)
        mimeo_config = MimeoConfig(config)
        logger.fine("Parsed Mimeo Configuration: [%s]", mimeo_config)
        return mimeo_config

    def _parse_with_http_environment(
            self,
            config: dict,
    ) -> dict:
        """Parse Mimeo Configuration with an HTTP environment.

        When --http-envs-file argument has not been provided, then
        the default environments path is used: mimeo.envs.json.

        Parameters
        ----------
        config : dict
            A source Mimeo Configuration dictionary

        Returns
        -------
        config : dict
            An overwritten Mimeo Configuration dictionary when
            --http-env argument has been provided. Otherwise,
            the source one, without any modification.

        Raises
        ------
        EnvironmentsFileNotFoundError
            If environments file does not exist.
        EnvironmentNotFoundError
            If the http environment is not defined in the environments file
        """
        if self._args.http_env is None:
            return config

        if self._args.http_envs_file is None:
            env = self._get_environment(DEFAULT_ENVS_PATH, self._args.http_env)
        else:
            env = self._get_environment(self._args.http_envs_file, self._args.http_env)
        return self._overwrite_output_with_env(config, env)

    def _parse_with_specific_args(
            self,
            config: dict,
    ) -> dict:
        """Parse Mimeo Configuration with Mimeo Configuration args.

        This method uses an internal `dict` fetching each command line
        argument with a corresponding Mimeo Configuration entry.

        Parameters
        ----------
        config : dict
            A source Mimeo Configuration dictionary

        Returns
        -------
        config : dict
            An overwritten Mimeo Configuration dictionary when
            some configuration arguments have been provided. Otherwise,
            the source one, without any modification.
        """
        for arg_name, mapping in self._ARGS_MAPPING.items():
            arg = getattr(self._args, arg_name, None)
            if arg is not None:
                entry_path = mapping.get(self._ENTRY_PATH_KEY, arg_name)
                get_value = mapping.get(self._GET_VALUE_KEY, lambda a: a)
                value = get_value(arg)
                config = self._overwrite_config_entry(config, entry_path, value)
        return config

    @classmethod
    def _overwrite_output_with_env(
            cls,
            config: dict,
            env: dict,
    ) -> dict:
        """Overwrite Mimeo Output Details with an environment config.

        Parameters
        ----------
        config : dict
            A source Mimeo Configuration dictionary
        env : dict
            An HTTP environment

        Returns
        -------
        config : dict
            An overwritten Mimeo Configuration.
        """
        for prop in cls._ENVIRONMENT_PROPS:
            value = env.get(prop)
            if value is not None:
                config_entry_path = [MimeoConfig.OUTPUT_KEY, prop]
                config = cls._overwrite_config_entry(config, config_entry_path, value)
        return config

    @classmethod
    def _overwrite_config_entry(
            cls,
            config_entry: dict,
            entry_path: list,
            value: str | int | bool,
    ) -> dict:
        """Overwrite a Mimeo Configuration entry.

        Recursively finds an entry using `entry_path` list. If any of
        middle entries does not exist, it is initialized as an empty
        dictionary. Once the target entry is found, the `value` is put
        there.

        Parameters
        ----------
        config_entry : dict
            A Mimeo Configuration entry to get its direct child
        entry_path : list
            A list of Mimeo Configuration nested properties, e.g.
            ['output', 'direction'] points to the direction
            property under output details entry.
        value
            An overwriting value when `entry_path` contains only one
            element.

        Returns
        -------
        config_entry : dict
            An overwritten Mimeo Configuration entry.
        """
        direct_entry = entry_path[0]
        if len(entry_path) > 1:
            if direct_entry not in config_entry:
                config_entry[direct_entry] = {}
            value = cls._overwrite_config_entry(
                config_entry[direct_entry],
                entry_path[1:],
                value)
        else:
            logger.fine("Overwriting %s to [%s]", direct_entry, value)
        config_entry[direct_entry] = value
        return config_entry

    @staticmethod
    def _get_environment(
            envs_path: str,
            env_name: str,
    ) -> dict:
        """Load an HTTP environment from HTTP envs vile.

        Parameters
        ----------
        envs_path : str
            An HTTP envs file path
        env_name : str
            An HTTP environment name

        Returns
        -------
        env : dict
            An HTTP environment configuration

        Raises
        ------
        EnvironmentsFileNotFoundError
            If environments file does not exist.
        EnvironmentNotFoundError
            If the http environment is not defined in the environments file
        """
        if not Path(envs_path).exists():
            raise EnvironmentsFileNotFoundError(envs_path)

        with Path(envs_path).open() as envs_file:
            envs = json.load(envs_file)
            if env_name not in envs:
                raise EnvironmentNotFoundError(env_name, envs_path)

        env = envs[env_name]
        logger.debug("Using environment [%s] from file [%s]: [%s]",
                     env_name, envs_path, env)
        return env

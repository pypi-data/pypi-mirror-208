"""The Mimeo Job module.

It exports a single class:
    * MimeoJob
        A class representing a single Mimeo processing job.
"""
from __future__ import annotations

import asyncio
import json
import logging
from argparse import Namespace
from os import walk
from pathlib import Path

from mimeo import MimeoConfig, Mimeograph
from mimeo.cli import MimeoArgumentParser, MimeoConfigParser

logger = logging.getLogger(__name__)


class MimeoJob:
    """A class representing a single Mimeo processing job.

    It is meant to be used in context of a command line. First it
    parses command line arguments using MimeoArgumentParser and then
    prepares logging. In the next step each Mimeo Configuration is
    parsed by MimeoConfigParser and provided arguments. Having prepared
    Mimeo Configuration, data processing starts.

    Methods
    -------
    run()
        Executes a Mimeo Job based on the CLI arguments.
    """

    def __init__(
            self,
    ):
        """Initialize MimeoJob class."""
        self._args = MimeoArgumentParser().parse_args()

    def run(
            self,
    ):
        """Execute a Mimeo Job based on the CLI arguments.

        First it customizes a log level. After that all Mimeo Configs
        paths are collected. Each of them is used in the next steps,
        which are: (1) parsing the configuration and (2) processing
        it.
        """
        self._customize_log_level(self._args)
        logger.info("Starting a Mimeo job")
        for config_path in self._get_config_paths(self._args.paths):
            mimeo_config = self._get_mimeo_config(config_path, self._args)
            asyncio.run(
                Mimeograph(mimeo_config).process(),
            )

    @staticmethod
    def _customize_log_level(
            args,
    ):
        """Customize the log level based on command line arguments."""
        if args.silent:
            logging.getLogger("mimeo").setLevel(logging.WARNING)
        elif args.debug:
            logging.getLogger("mimeo").setLevel(logging.DEBUG)
        elif args.fine and hasattr(logging, "FINE"):
            logging.getLogger("mimeo").setLevel(logging.FINE)

    @staticmethod
    def _get_config_paths(
            paths: list,
    ) -> list:
        """Collect Mimeo Configuration paths.

        This method traverses directory paths and collects all files
        within.

        Parameters
        ----------
        paths : list
            A list of paths provided in command line

        Returns
        -------
        file_paths : list
            A list of file paths
        """
        file_paths = []
        for file_path in paths:
            if Path(file_path).is_dir():
                for dir_path, _, file_names in walk(file_path):
                    for file_name in file_names:
                        file_paths.append(f"{dir_path}/{file_name}")
            elif Path(file_path).is_file():
                file_paths.append(file_path)
        return file_paths

    @classmethod
    def _get_mimeo_config(
            cls,
            config_path: str,
            args: Namespace,
    ) -> MimeoConfig:
        """Return parsed Mimeo Configuration.

        This method parses a raw configuration with command line
        arguments using a MimeoConfigParser instance.

        Parameters
        ----------
        config_path : str
            A raw configuration path
        args
            Command line arguments parsed by MimeoArgumentParser

        Returns
        -------
        MimeoConfig
            A parsed Mimeo Configuration

        Raises
        ------
        EnvironmentsFileNotFoundError
            If environments file does not exist.
        EnvironmentNotFoundError
            If the http environment is not defined in the environments file
        """
        config = cls._get_raw_config(config_path)
        mimeo_config_parser = MimeoConfigParser(config, args)
        return mimeo_config_parser.parse_config()

    @staticmethod
    def _get_raw_config(
            config_path: str,
    ) -> dict:
        """Load configuration file to a dictionary."""
        logger.info("Reading Mimeo Configuration: %s", config_path)
        with Path(config_path).open() as config_file:
            return json.load(config_file)

"""The Mimeo Consumer Factory module.

It exports only one class:
    * ConsumerFactory
        A Factory class instantiating a Consumer based on Mimeo Config.
"""
from __future__ import annotations

from mimeo.config.exc import UnsupportedPropertyValueError
from mimeo.config.mimeo_config import MimeoConfig
from mimeo.consumers import Consumer, FileConsumer, HttpConsumer, RawConsumer


class ConsumerFactory:
    """A Factory class instantiating a Consumer based on Mimeo Config.

    Implementation of the Consumer class depends on the output direction configured.

    Attributes
    ----------
    FILE_DIRECTION
        The 'file' output direction
    STD_OUT_DIRECTION
        The 'stdout' output direction
    HTTP_DIRECTION
        The 'http' output direction

    Methods
    -------
    get_consumer(mimeo_config: MimeoConfig) -> Consumer
        Initialize a Consumer based on the Mimeo Output Direction.
    """

    FILE_DIRECTION = MimeoConfig.OUTPUT_DIRECTION_FILE
    STD_OUT_DIRECTION = MimeoConfig.OUTPUT_DIRECTION_STD_OUT
    HTTP_DIRECTION = MimeoConfig.OUTPUT_DIRECTION_HTTP

    @staticmethod
    def get_consumer(
            mimeo_config: MimeoConfig,
    ) -> Consumer:
        """Initialize a Consumer based on the Mimeo Output Direction.

        Parameters
        ----------
        mimeo_config : MimeoConfig
            A Mimeo Configuration

        Returns
        -------
        Consumer
            A Consumer's implementation instance

        Raises
        ------
        UnsupportedPropertyValueError
            If the output direction is not supported
        """
        direction = mimeo_config.output.direction
        if direction == ConsumerFactory.STD_OUT_DIRECTION:
            return RawConsumer()
        if direction == ConsumerFactory.FILE_DIRECTION:
            return FileConsumer(mimeo_config.output)
        if direction == ConsumerFactory.HTTP_DIRECTION:
            return HttpConsumer(mimeo_config.output)
        raise UnsupportedPropertyValueError(
            MimeoConfig.OUTPUT_DIRECTION_KEY,
            direction,
            MimeoConfig.SUPPORTED_OUTPUT_DIRECTIONS)

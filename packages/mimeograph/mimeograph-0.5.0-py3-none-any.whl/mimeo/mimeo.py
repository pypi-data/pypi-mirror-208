"""The Mimeo module.

This module is a main module providing the most high level class
in Mimeo:
    * Mimeograph
        A class responsible for the Mimeo processing.
"""
from __future__ import annotations

import logging

from mimeo.config.mimeo_config import MimeoConfig
from mimeo.consumers import ConsumerFactory
from mimeo.context import MimeoContextManager
from mimeo.generators import GeneratorFactory

logger = logging.getLogger(__name__)


class Mimeograph:
    """A class responsible for the Mimeo processing.

    Based on the Mimeo Configuration it instantiates generator and
    consumer to produce desired data.

    Methods
    -------
    process()
        Process the Mimeo Configuration (generate data and consume).
    """

    def __init__(
            self,
            mimeo_config: MimeoConfig,
    ):
        self._mimeo_config = mimeo_config
        self._generator = GeneratorFactory.get_generator(self._mimeo_config)
        self._consumer = ConsumerFactory.get_consumer(self._mimeo_config)

    async def process(
            self,
    ):
        """Process the Mimeo Configuration (generate data and consume)."""
        logger.info("Starting data generation")
        with MimeoContextManager(self._mimeo_config):
            data = self._generator.generate(self._mimeo_config.templates)
            data_str = (self._generator.stringify(data_unit)
                        for data_unit in data)
            await self._consumer.consume(data_str)
        logger.info("Data has been processed")

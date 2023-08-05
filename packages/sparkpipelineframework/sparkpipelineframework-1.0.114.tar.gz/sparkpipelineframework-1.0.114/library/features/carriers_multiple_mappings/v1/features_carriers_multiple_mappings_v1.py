from typing import Optional, Dict, Any
from spark_pipeline_framework.proxy_generator.proxy_base import ProxyBase
from spark_pipeline_framework.progress_logger.progress_logger import ProgressLogger
from os import path


# This file was auto-generated by generate_proxies(). It enables auto-complete in PyCharm. Do not edit manually!
class FeaturesCarriersMultipleMappingsV1(ProxyBase):
    def __init__(
        self,
        parameters: Dict[str, Any],
        progress_logger: Optional[ProgressLogger] = None,
        verify_count_remains_same: bool = False,
    ) -> None:
        location: str = path.dirname(path.abspath(__file__))
        super().__init__(
            parameters=parameters,
            location=location,
            progress_logger=progress_logger,
            verify_count_remains_same=verify_count_remains_same,
        )

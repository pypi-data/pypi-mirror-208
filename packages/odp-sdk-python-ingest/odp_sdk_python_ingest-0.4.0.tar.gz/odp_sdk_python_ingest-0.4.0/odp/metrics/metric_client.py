from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union

from odp.metrics.abstract_metrics import CounterABC, GaugeABC, HistogramABC


class MetricClient(ABC):
    """Base class for metric clients"""

    @abstractmethod
    def create_counter(
        self,
        name: str,
        documentation: str,
        labelnames: Union[List[str], Tuple[str]] = (),
        namespace: str = "",
        subsystem: str = "",
        unit: str = "",
    ) -> CounterABC:
        """Base method to create a counter from the metric client"""

    @abstractmethod
    def create_gauge(self, name: str, documentation: str, labels: Optional[List] = None) -> GaugeABC:
        """Base method to create a gauge from the metric client"""

    @abstractmethod
    def create_histogram(self, name: str, description: str, labels: Optional[List] = None) -> HistogramABC:
        """Base method to create a gauge from the metric client"""

    @abstractmethod
    def push_metrics(self):
        """Base method to push metrics"""

from __future__ import annotations

import logging
import time as time_module
from contextlib import contextmanager
from typing import Dict, List, Optional

import attrs

from hkkang_utils.string import generate_random_str


@attrs.define
class Period:
    start_time: float
    end_time: float
    
    @property
    def elapsed_time(self) -> float:
        return self.end_time - self.start_time

class TimerMetaclass(type):
    def __call__(cls, name: Optional[str] = None):
        if name is None:
            while name is None or name in Timer._cache:
                name = generate_random_str(size=4)
        if name not in Timer._cache.keys():
            obj = cls.__new__(cls)
            obj.__init__()
            Timer._cache[name] = obj
        return Timer._cache[name]

# @attrs.define
class Timer(metaclass=TimerMetaclass):
    _cache: Dict[str, Timer] = dict()
    def __init__(self):
        self.start_time: Optional[float] = None
        self.measured_times: List[Period] = []
        self.paused_times: List[Period] = []
    
    @property
    def name(self) -> str:
        for k, v in Timer._cache.items():
            if v is self:
                return k
        return None
        
    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(f"Timer.{self.name}")

    @contextmanager
    def pause(self) -> Timer:
        # Pre processing
        current_time = time_module.time()
        self.measured_times.append(Period(self.start_time, current_time))
        self.start_time = current_time
        yield self
        # Post processing
        current_time = time_module.time()
        self.paused_times.append(Period(self.start_time, current_time))
        self.start_time = current_time
    
    @contextmanager
    def measure(self, print_measured_time: bool = False) -> Timer:
        # Pre processing
        self.start_time = time_module.time()
        yield self
        # Post processing
        self.measured_times.append(Period(self.start_time, time_module.time()))
        if print_measured_time:
            self.show_elapsed_time()
        
    @staticmethod
    def get_timer(name: str) -> Timer:
        # __new__ will create a new timer if it does not exist
        return Timer(name)

    @property
    def elapsed_time(self):
        return sum([period.elapsed_time for period in self.measured_times])
    
    def start(self) -> None:
        if self.start_time is not None:
            self.logger.warning("Timer has already been started. Please call stop() first.")
        self.start_time = time_module.time()
        
    def stop(self) -> None:
        if self.start_time is None:
            self.logger.warning("Timer has not been started. Please call start() first.")
        self.measured_times.append(Period(self.start_time, time_module.time()))
        self.start_time = None

    def show_elapsed_time(self):
        self.logger.info(f"Elapsed time: {self.elapsed_time:.2f} seconds")


    def delete(self):
        del self.cache[self.name]


def measure_time(func):
    def wrapper(*args, **kwargs):
        timer = Timer()
        with timer.measure(print_measured_time=True):
            result = func(*args, **kwargs)
        del timer
        return result
    return wrapper

if __name__ == "__main__":
    timer = Timer()
    print("Done")
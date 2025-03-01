from typing import Type, List

class ScraperConfig:
    def __init__(
        self,
        must_raise: List[Type[Exception]] = [Exception],
        create_error_logs: bool = False,
    ):
        self.must_raise = must_raise
        self.create_error_logs = create_error_logs
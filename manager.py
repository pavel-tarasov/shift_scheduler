from copy import deepcopy
from typing import Type

from intern import InternsList
from schedule import MonthlySchedule
from scheduler import BaseScheduler


class SchedulerManager:
    def __init__(
        self,
        interns: InternsList,
        schedule: MonthlySchedule,
        scheduler_classes: list[Type[BaseScheduler]],
        num_runs: int = 10,
    ):
        self.interns = interns
        self.schedule = schedule
        self.scheduler_classes = scheduler_classes
        self.num_runs = num_runs
        self.results = []

    def run_schedulers(self):
        for scheduler_class in self.scheduler_classes:
            for _ in range(self.num_runs):
                scheduler = scheduler_class(
                    deepcopy(self.interns), deepcopy(self.schedule)
                )
                scheduler.generate_schedule()
                scheduler.calculate_statistics()
                score = scheduler.calculate_score()
                self.results.append(
                    {
                        "scheduler_type": type(scheduler),
                        "score": score,
                        "schedule": scheduler.schedule,
                        "statistics": scheduler.intern_statistics,
                    }
                )

    def get_best_result(self):
        return min(self.results, key=lambda x: x["score"])

import datetime
import random
import statistics
from abc import ABC, abstractmethod
from typing import Literal

from intern import InternsList, Intern
from schedule import MonthlySchedule, DailySchedule


class NoAvailableInternsError(Exception):
    """Raise when there is no interns available for the shift"""

    def __init__(self, date: datetime.date):
        self.date = date

    def __str__(self):
        return f"There is no available interns for date {self.date}"


class BaseScheduler(ABC):
    def __init__(self, interns: InternsList, schedule: MonthlySchedule):
        self.interns = interns
        self.schedule = schedule
        self.intern_statistics: list[dict] = []
        self.shift_counts = {intern: 0 for intern in self.interns}
        self.friday_counts = {intern: 0 for intern in self.interns}
        self.saturday_counts = {intern: 0 for intern in self.interns}
        self.sunday_counts = {intern: 0 for intern in self.interns}
        self.er_counts = {intern: 0 for intern in self.interns}

    @abstractmethod
    def generate_schedule(self):
        pass

    @abstractmethod
    def calculate_statistics(self):
        pass

    def print_statistics(self):
        for row in self.intern_statistics:
            print(row)

    @abstractmethod
    def calculate_score(self):
        pass


class GreedyScheduler(BaseScheduler):
    def __init__(self, interns: InternsList, schedule: MonthlySchedule):
        super().__init__(interns, schedule)

    def get_best_available_intern(self, date: datetime.date, er_shift=False):
        def calc_score(intern: Intern, current_date: datetime.date):
            if not intern.shifts:
                return 100
            else:
                val = (current_date - max(intern.shifts)).days
                return val

        available_interns = [
            intern for intern in self.interns if intern.is_available(date, er_shift)
        ]

        if not available_interns:
            raise NoAvailableInternsError(date)

        scores = [calc_score(intern, date) for intern in available_interns]
        max_score = max(scores)
        best_interns = [
            intern
            for intern, score in zip(available_interns, scores)
            if score == max_score
        ]

        best_intern = random.choice(best_interns)

        return best_intern

    def assign_intern(
        self,
        day: DailySchedule,
        intern: Intern,
        shift_type: Literal["department", "er_1", "er_2"],
    ) -> None:
        if shift_type == "department":
            day.department_shift = intern
        elif shift_type == "er_1":
            day.er_shifts[0] = intern
        elif shift_type == "er_2":
            day.er_shifts[1] = intern

        intern.shifts.append(day.date)
        self.er_counts[intern] += 1
        self.shift_counts[intern] += 1
        if day.date.isoweekday() == 5:
            self.friday_counts[intern] += 1
        elif day.date.isoweekday() == 6:
            self.saturday_counts[intern] += 1
        elif day.date.isoweekday() == 7:
            self.sunday_counts[intern] += 1

    def generate_schedule(self):
        for day in self.schedule.days:
            # print(f"day: {day.date}, ER shifts: {day.has_er_shifts}")
            if day.has_er_shifts:
                best_available_intern = self.get_best_available_intern(
                    date=day.date, er_shift=True
                )
                # print(f"first best available intern for ER: {best_available_intern}")
                self.assign_intern(day, best_available_intern, "er_1")

                best_available_intern = self.get_best_available_intern(
                    date=day.date, er_shift=True
                )
                # print(f"second best available intern for ER: {best_available_intern}")
                self.assign_intern(day, best_available_intern, "er_2")

            best_available_intern = self.get_best_available_intern(
                date=day.date, er_shift=False
            )
            # print(f"best available intern for department: {best_available_intern}")
            self.assign_intern(day, best_available_intern, "department")

    def calculate_statistics(self):
        for intern in self.interns:
            sandwiches_number = 0
            for i, shift in enumerate(intern.shifts):
                if i > 0:
                    if (shift - intern.shifts[i - 1]).days == 2:
                        sandwiches_number += 1

            self.intern_statistics.append(
                {
                    "name": intern.name,
                    "days": len(intern.shifts),
                    "fridays": self.friday_counts[intern],
                    "saturdays": self.saturday_counts[intern],
                    "sundays": self.sunday_counts[intern],
                    "sandwiches": sandwiches_number,
                }
            )

    def calculate_score(self):
        all_shifts_std = statistics.pstdev(list(self.shift_counts.values()))
        friday_shifts_std = statistics.pstdev(list(self.friday_counts.values()))
        saturday_shifts_std = statistics.pstdev(list(self.saturday_counts.values()))
        sunday_shifts_std = statistics.pstdev(list(self.sunday_counts.values()))
        er_shifts_std = statistics.pstdev(list(self.er_counts.values()))

        score = (
            all_shifts_std
            + friday_shifts_std
            + saturday_shifts_std
            + sunday_shifts_std
            + er_shifts_std
        )

        for intern in self.interns:
            shift_differences = [
                (intern.shifts[i + 1] - intern.shifts[i]).days
                for i in range(len(intern.shifts) - 1)
            ]
            score += statistics.pstdev(shift_differences)

        return score

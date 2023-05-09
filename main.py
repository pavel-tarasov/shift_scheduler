import csv
import datetime
from abc import ABC, abstractmethod
from calendar import monthrange


class Intern:
    def __init__(self, name: str, can_work_er: bool):
        self.name = name
        self.can_work_er = can_work_er
        self.shifts: list[datetime.date] = []

    def is_available(self, date: datetime.date, er_shift=False):
        available = True
        if er_shift:
            if not self.can_work_er:
                available = False
        for shift in self.shifts:
            if abs((date - shift).days) < 2:
                available = False
        return available

    def __str__(self) -> str:
        return self.str_short()

    def str_short(self) -> str:
        return self.name

    def str_long(self) -> str:
        if self.can_work_er:
            return f"{self.name} (ER)"
        else:
            return f"{self.name}"


class InternsList(list):
    def __init__(self, iterable):
        super().__init__(self._validate_intern(item) for item in iterable)

    def __setitem__(self, index, item):
        super().__setitem__(index, self._validate_intern(item))

    def insert(self, index, item):
        super().insert(index, self._validate_intern(item))

    def append(self, item):
        super().append(self._validate_intern(item))

    def extend(self, other):
        if isinstance(other, type(self)):
            super().extend(other)
        else:
            super().extend(self._validate_intern(item) for item in other)

    @staticmethod
    def _validate_intern(item: Intern) -> Intern:
        if isinstance(item, Intern):
            return item
        raise TypeError(f"Intern type expected, got {type(item).__name__}")

    @classmethod
    def from_csv(cls, file_path):
        interns = []
        with open(file_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row["name"]
                can_work_er = row["er"] == "1"
                interns.append(Intern(name, can_work_er))
        return cls(interns)

    def __str__(self) -> str:
        return self.str_short()

    def str_short(self) -> str:
        return ", ".join([str(intern) for intern in self])

    def str_long(self) -> str:
        return ", ".join([intern.str_long() for intern in self])

    def str_full(self) -> str:
        return "\n".join([intern.str_full() for intern in self])


class DailySchedule:
    def __init__(self, date: datetime.date, er_shifts: bool = False):
        self.date = date
        self.department_shift: Intern | None = None
        self.er_shifts: [Intern | None] = [None, None] if er_shifts else None
        self.has_er_shifts = er_shifts

    def __str__(self) -> str:
        if self.has_er_shifts:
            return (
                f"{self.date}: MD shift: {self.department_shift}; "
                f"ER shifts: {self.er_shifts[0]}, {self.er_shifts[1]}"
            )
        else:
            return f"{self.date}: MD shift: {self.department_shift}"


class MonthlySchedule:
    def __init__(self, year: int, month: int, first_er_shift_day: int):
        self.year = year
        self.month = month
        self.first_er_shift_day = first_er_shift_day
        self.days = self.generate_empty_schedule()

    def generate_empty_schedule(self) -> list[DailySchedule]:
        _, days_in_month = monthrange(self.year, self.month)
        empty_schedule = []

        for day in range(1, days_in_month + 1):
            date = datetime.date(year=self.year, month=self.month, day=day)
            if (day - self.first_er_shift_day) % 4 == 0:
                er_shifts = True
            else:
                er_shifts = False
            day_schedule = DailySchedule(date, er_shifts)

            empty_schedule.append(day_schedule)

        return empty_schedule

    def __str__(self) -> str:
        return "\n".join([str(day) for day in self.days])


class BaseScheduler(ABC):
    def __init__(self, interns: InternsList, schedule: MonthlySchedule):
        self.interns = interns
        self.schedule = schedule
        self.statistics: list[dict] = []

    @abstractmethod
    def generate_schedule(self):
        pass

    @abstractmethod
    def calculate_statistics(self):
        pass

    def print_statistics(self):
        for row in self.statistics:
            print(row)

    @abstractmethod
    def calculate_score(self):
        pass


# TODO: add score function
class GreedyScheduler(BaseScheduler):
    def __init__(self, interns: InternsList, schedule: MonthlySchedule):
        super().__init__(interns, schedule)

    def get_best_available_intern(self, date: datetime.date, er_shift=False):
        def sort_key(intern: Intern, date: datetime.date):
            if not intern.shifts:
                return 100
            else:
                val = (date - max(intern.shifts)).days
                return val

        available_interns = [
            intern for intern in self.interns if intern.is_available(date, er_shift)
        ]

        if not available_interns:
            return None

        best_intern = max(
            available_interns,
            key=lambda intern: sort_key(intern, date),
        )

        return best_intern

    def generate_schedule(self):
        for day in self.schedule.days:
            print(f"day: {day.date}, ER shifts: {day.has_er_shifts}")
            if day.has_er_shifts:
                best_available_intern = self.get_best_available_intern(
                    date=day.date, er_shift=True
                )
                print(f"first best available intern for ER: {best_available_intern}")
                day.er_shifts[0] = best_available_intern
                best_available_intern.shifts.append(day.date)

                best_available_intern = self.get_best_available_intern(
                    date=day.date, er_shift=True
                )
                print(f"second best available intern for ER: {best_available_intern}")
                day.er_shifts[1] = best_available_intern
                best_available_intern.shifts.append(day.date)

            best_available_intern = self.get_best_available_intern(
                date=day.date, er_shift=False
            )
            print(f"best available intern for department: {best_available_intern}")
            day.department_shift = best_available_intern
            best_available_intern.shifts.append(day.date)

    def calculate_statistics(self):
        for intern in self.interns:
            fridays_number = 0
            saturdays_number = 0
            sundays_number = 0
            sandwiches_number = 0
            for i, shift in enumerate(intern.shifts):
                if shift.isoweekday() == 5:
                    fridays_number += 1
                elif shift.isoweekday() == 6:
                    saturdays_number += 1
                elif shift.isoweekday() == 7:
                    sundays_number += 1

                if i > 0:
                    if (shift - intern.shifts[i - 1]).days == 2:
                        sandwiches_number += 1

            self.statistics.append(
                {
                    "name": intern.name,
                    "days": len(intern.shifts),
                    "fridays": fridays_number,
                    "saturdays": saturdays_number,
                    "sundays": sundays_number,
                    "sandwiches": sandwiches_number,
                }
            )

    def calculate_score(self):
        pass


if __name__ == "__main__":
    interns_list = InternsList.from_csv("interns.csv")
    monthly_schedule = MonthlySchedule(year=2023, month=5, first_er_shift_day=2)

    scheduler = GreedyScheduler(interns=interns_list, schedule=monthly_schedule)
    scheduler.generate_schedule()
    print("---")
    scheduler.calculate_statistics()
    scheduler.print_statistics()

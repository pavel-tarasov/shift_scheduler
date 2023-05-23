import datetime
from calendar import monthrange

from intern import Intern


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

    def add_er_shift(self, date: datetime):
        for day in self.days:
            if day.date == date:
                day.er_shifts = [None, None]
                day.has_er_shifts = True

    def remove_er_shift(self, date: datetime):
        for day in self.days:
            if day.date == date:
                day.er_shifts = None
                day.has_er_shifts = False

    def __str__(self) -> str:
        return "\n".join([str(day) for day in self.days])

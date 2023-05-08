import csv
import datetime
from calendar import monthrange


class Intern:
    def __init__(self, name: str, er_duty: bool):
        self.name: str = name
        self.can_work_er: bool = er_duty
        self.shifts: list[datetime.date] = []
        self.last_shift: datetime.date | None = None

    def assign_to_shift(self, date: datetime.date) -> None:
        self.shifts.append(date)
        self.last_shift = max(self.shifts)

    def is_available(self, date: datetime.date):
        if self.last_shift is None or date - self.last_shift > datetime.timedelta(
            days=2
        ):
            return True
        else:
            return False

    # TODO: add random sort in case of same score for interns
    def sort_key(self, date: datetime.date):
        if self.last_shift is None:
            return 100
        else:
            return abs((self.last_shift - date).days)

    def __str__(self):
        return self.str_short()

    def str_short(self):
        return self.name

    def str_long(self):
        return f"{self.name} (ER duty: {self.can_work_er})"

    def str_full(self):
        shifts_str = ", ".join(map(str, self.shifts))
        return f"{self.name} ER duty: {self.can_work_er}, shifts: {shifts_str}"


class InternsList:
    def __init__(self, interns: list[Intern] = None):
        self.interns = interns if interns else []

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

    def add_intern(self, intern):
        self.interns.append(intern)

    def remove_intern(self, intern):
        self.interns.remove(intern)

    def __str__(self):
        return self.str_short()

    def str_short(self):
        return "\n".join([str(intern) for intern in self.interns])

    def str_long(self):
        return "\n".join([intern.str_long() for intern in self.interns])

    def str_full(self):
        return "\n".join([intern.str_full() for intern in self.interns])

    def get_best_available_intern(self, date: datetime.date, er_shift=False):
        available_interns = [
            intern
            for intern in self.interns
            if intern.is_available(date)
            and (er_shift is False or (er_shift is True and intern.can_work_er))
        ]

        if not available_interns:
            return None

        best_intern = max(
            available_interns,
            key=lambda intern: intern.sort_key(date),
        )

        return best_intern


class DaySchedule:
    def __init__(self, date: datetime.date, er_shifts: bool = False):
        self.date = date
        self.department_shift = None
        self.er_shifts = [None, None] if er_shifts else None
        self.has_er_shifts = er_shifts

    def __str__(self):
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
        self.schedule = self.generate_empty_schedule()

    def generate_empty_schedule(self):
        _, days_in_month = monthrange(self.year, self.month)
        empty_schedule = []

        for day in range(1, days_in_month + 1):
            date = datetime.date(year=self.year, month=self.month, day=day)
            if (day - self.first_er_shift_day) % 4 == 0:
                er_duties = True
            else:
                er_duties = False
            day_schedule = DaySchedule(date, er_duties)

            empty_schedule.append(day_schedule)

        return empty_schedule

    def __str__(self):
        return "\n".join([str(day_schedule) for day_schedule in self.schedule])


# TODO: add score function
# TODO: change according to gpt suggestions
class Scheduler:
    def __init__(self, interns_list: InternsList, monthly_schedule: MonthlySchedule):
        self.interns_list = interns_list
        self.monthly_schedule = monthly_schedule

    def generate_greedy_schedule(self):
        for day in self.monthly_schedule.schedule:
            print(f"day: {day.date}, ER shifts: {day.has_er_shifts}")
            if day.has_er_shifts:
                best_available_intern = self.interns_list.get_best_available_intern(
                    date=day.date, er_shift=True
                )
                print(f"first best available intern for ER: {best_available_intern}")
                day.er_shifts[0] = best_available_intern
                best_available_intern.assign_to_shift(day.date)

                best_available_intern = self.interns_list.get_best_available_intern(
                    date=day.date, er_shift=True
                )
                print(f"second best available intern for ER: {best_available_intern}")
                day.er_shifts[1] = best_available_intern
                best_available_intern.assign_to_shift(day.date)

            best_available_intern = self.interns_list.get_best_available_intern(
                date=day.date, er_shift=False
            )
            print(f"best available intern for department: {best_available_intern}")
            day.department_shift = best_available_intern
            best_available_intern.assign_to_shift(day.date)

    def get_schedule_statistics(self):
        stats = []
        for intern in self.interns_list.interns:
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

            stats.append(
                {
                    "name": intern.name,
                    "days": len(intern.shifts),
                    "fridays": fridays_number,
                    "saturdays": saturdays_number,
                    "sundays": sundays_number,
                    "sandwiches": sandwiches_number,
                }
            )
        return stats


# class GreedyScheduleSolver:
#     def __init__(self, interns: InternsList, monthly_schedule: MonthlySchedule):
#         self.interns = interns
#         self.monthly_schedule = monthly_schedule
#
#     def solve(self):
#         for day in self.monthly_schedule.schedule:
#             print(f"day: {day.date}, ER shifts: {day.has_er_shifts}")
#             if day.has_er_shifts:
#                 best_available_intern = self.interns.get_best_available_intern(
#                     date=day.date, er_shift=True
#                 )
#                 print(f"first best available intern for ER: {best_available_intern}")
#                 day.er_shifts[0] = best_available_intern
#                 best_available_intern.assign_to_shift(day.date)
#
#                 best_available_intern = self.interns.get_best_available_intern(
#                     date=day.date, er_shift=True
#                 )
#                 print(f"second best available intern for ER: {best_available_intern}")
#                 day.er_shifts[1] = best_available_intern
#                 best_available_intern.assign_to_shift(day.date)
#
#             best_available_intern = self.interns.get_best_available_intern(
#                 date=day.date, er_shift=False
#             )
#             print(f"best available intern for department: {best_available_intern}")
#             day.department_shift = best_available_intern
#             best_available_intern.assign_to_shift(day.date)


if __name__ == "__main__":
    interns_list = InternsList.from_csv("interns.csv")
    monthly_schedule = MonthlySchedule(2023, 5, 1)
    print(monthly_schedule)
    print("---")

    scheduler = Scheduler(interns_list=interns_list, monthly_schedule=monthly_schedule)
    scheduler.generate_greedy_schedule()
    print("---")

    print(monthly_schedule)
    print("---")
    for intern_stats in scheduler.get_schedule_statistics():
        print(intern_stats)

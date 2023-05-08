import csv
import datetime
from calendar import monthrange


class Intern:
    def __init__(self, name: str, er_shift: bool):
        self.name = name
        self.er_shift = er_shift

    def __str__(self) -> str:
        return self.str_short()

    def str_short(self) -> str:
        return self.name

    def str_long(self) -> str:
        return f"{self.name} (ER duty: {self.er_shift})"


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

    # def get_best_available_intern(self, date: datetime.date, er_shift=False):
    #     available_interns = [
    #         intern
    #         for intern in self.interns
    #         if intern.is_available(date)
    #         and (er_shift is False or (er_shift is True and intern.can_work_er))
    #     ]
    #
    #     if not available_interns:
    #         return None
    #
    #     best_intern = max(
    #         available_interns,
    #         key=lambda intern: intern.sort_key(date),
    #     )
    #
    #     return best_intern


class DaySchedule:
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

    def generate_empty_schedule(self) -> list[DaySchedule]:
        _, days_in_month = monthrange(self.year, self.month)
        empty_schedule = []

        for day in range(1, days_in_month + 1):
            date = datetime.date(year=self.year, month=self.month, day=day)
            if (day - self.first_er_shift_day) % 4 == 0:
                er_shifts = True
            else:
                er_shifts = False
            day_schedule = DaySchedule(date, er_shifts)

            empty_schedule.append(day_schedule)

        return empty_schedule

    def __str__(self) -> str:
        return "\n".join([str(day) for day in self.days])


# # TODO: add score function
# # TODO: change according to gpt suggestions
# class Scheduler:
#     def __init__(self, interns_list: InternsList, monthly_schedule: MonthlySchedule):
#         self.interns_list = interns_list
#         self.monthly_schedule = monthly_schedule
#
#     def generate_greedy_schedule(self):
#         for day in self.monthly_schedule.schedule:
#             print(f"day: {day.date}, ER shifts: {day.has_er_shifts}")
#             if day.has_er_shifts:
#                 best_available_intern = self.interns_list.get_best_available_intern(
#                     date=day.date, er_shift=True
#                 )
#                 print(f"first best available intern for ER: {best_available_intern}")
#                 day.er_shifts[0] = best_available_intern
#                 best_available_intern.assign_to_shift(day.date)
#
#                 best_available_intern = self.interns_list.get_best_available_intern(
#                     date=day.date, er_shift=True
#                 )
#                 print(f"second best available intern for ER: {best_available_intern}")
#                 day.er_shifts[1] = best_available_intern
#                 best_available_intern.assign_to_shift(day.date)
#
#             best_available_intern = self.interns_list.get_best_available_intern(
#                 date=day.date, er_shift=False
#             )
#             print(f"best available intern for department: {best_available_intern}")
#             day.department_shift = best_available_intern
#             best_available_intern.assign_to_shift(day.date)
#
#     def get_schedule_statistics(self):
#         stats = []
#         for intern in self.interns_list.interns:
#             fridays_number = 0
#             saturdays_number = 0
#             sundays_number = 0
#             sandwiches_number = 0
#             for i, shift in enumerate(intern.shifts):
#                 if shift.isoweekday() == 5:
#                     fridays_number += 1
#                 elif shift.isoweekday() == 6:
#                     saturdays_number += 1
#                 elif shift.isoweekday() == 7:
#                     sundays_number += 1
#
#                 if i > 0:
#                     if (shift - intern.shifts[i - 1]).days == 2:
#                         sandwiches_number += 1
#
#             stats.append(
#                 {
#                     "name": intern.name,
#                     "days": len(intern.shifts),
#                     "fridays": fridays_number,
#                     "saturdays": saturdays_number,
#                     "sundays": sundays_number,
#                     "sandwiches": sandwiches_number,
#                 }
#             )
#         return stats


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
    print(interns_list)
    print("---")
    for intern in interns_list:
        print(intern)
    print("---")

    monthly_schedule = MonthlySchedule(2023, 5, 2)
    print(monthly_schedule)
    print("---")

    # scheduler = Scheduler(interns_list=interns_list, monthly_schedule=monthly_schedule)
    # scheduler.generate_greedy_schedule()
    # print("---")
    #
    # print(monthly_schedule)
    # print("---")
    # for intern_stats in scheduler.get_schedule_statistics():
    #     print(intern_stats)

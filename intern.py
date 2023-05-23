import csv
import datetime


class Intern:
    def __init__(
        self,
        name: str,
        department: bool,
        er: bool,
        forbidden_days: list[datetime.date],
        desirable_days: list[datetime.date],
    ):
        self.name = name
        self.department = department
        self.er = er
        self.shifts: list[datetime.date] = []
        self.forbidden_days = forbidden_days
        self.desirable_days = desirable_days
        self.taken_days = forbidden_days

    def is_available(self, current_date: datetime.date, er_shift=False):
        available = True
        if er_shift and not self.er:
            available = False
        if not er_shift and not self.department:
            available = False
        for shift in self.shifts:
            if abs((current_date - shift).days) < 2:
                available = False
        if current_date in self.taken_days:
            available = False
        return available

    def __str__(self) -> str:
        return self.str_short()

    def str_short(self) -> str:
        return self.name

    def str_long(self) -> str:
        return (
            f"{self.name} "
            f"(Department: {'Yes' if self.department else 'No'}, "
            f"ER: {'Yes' if self.er else 'No'})"
        )


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
    def from_csv(cls, file_path: str, year: int, month: int):
        interns = []
        with open(file_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row["name"]
                department = row["department"] == "1"
                er = row["er"] == "1"

                forbidden_days = []
                for day_index in row["forbidden_days"].split(","):
                    if day_index != "":
                        forbidden_days.append(
                            datetime.date(year, month, int(day_index))
                        )

                desirable_days = []
                for day_index in row["desirable_days"].split(","):
                    if day_index != "":
                        desirable_days.append(
                            datetime.date(year, month, int(day_index))
                        )

                interns.append(
                    Intern(name, department, er, forbidden_days, desirable_days)
                )
        return cls(interns)

    def __str__(self) -> str:
        return self.str_short()

    def str_short(self) -> str:
        return ", ".join([str(intern) for intern in self])

    def str_long(self) -> str:
        return ", ".join([intern.str_long() for intern in self])

    def str_full(self) -> str:
        return "\n".join([intern.str_full() for intern in self])

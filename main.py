from intern import InternsList
from schedule import MonthlySchedule
from scheduler import GreedyScheduler

if __name__ == "__main__":
    interns_list = InternsList.from_csv("interns.csv")
    monthly_schedule = MonthlySchedule(year=2023, month=5, first_er_shift_day=2)

    scheduler = GreedyScheduler(interns=interns_list, schedule=monthly_schedule)
    scheduler.generate_schedule()
    print("---")
    print(scheduler.schedule)
    print("---")
    print(scheduler.calculate_score())

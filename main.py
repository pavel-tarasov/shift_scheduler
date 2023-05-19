from intern import InternsList
from manager import SchedulerManager
from schedule import MonthlySchedule
from scheduler import GreedyScheduler

if __name__ == "__main__":
    interns_list = InternsList.from_csv("interns.csv")
    monthly_schedule = MonthlySchedule(year=2023, month=5, first_er_shift_day=2)
    manager = SchedulerManager(
        interns=interns_list,
        schedule=monthly_schedule,
        scheduler_classes=[GreedyScheduler],
        num_runs=10,
    )
    manager.run_schedulers()
    best_result = manager.get_best_result()
    print(best_result['score'])
    print(best_result['schedule'])

from todoist_api_python.api import TodoistAPI
import keyring
import configparser
import logging
import datetime
import sys
import requests
from time import sleep
from CommandLineParser import CommandLineParser
from CommandLineParser import ini_path

current_version = "v1.1.1"
api_token = None


def check_for_updates():
    """
    Check for updates in the repository releases

    @return Response
    """

    repo_url = "https://api.github.com/repos/ussaka/todoist-prioritizer/releases"
    response = requests.get(repo_url)
    if response.status_code == 200:
        releases = response.json()
        latest_release = releases[0]
        latest_version = latest_release["tag_name"]
        if latest_version > current_version:
            logging.info(f"New version available: {latest_version}")
            logging.info(f"Changelog: {latest_release['body']}")
            logging.info(f"Download link: {latest_release['html_url']}\n")
    else:
        logging.error(
            "Update checker failed, failed to fetch releases from the repository"
        )
    return response


def get_tasks(filters: str) -> list:
    """!
    Get filtered tasks from the Todoist API

    @param filters The filters to apply to the tasks

    @return The list of tasks from the Todoist API
    """

    tasks_lists = []
    tasks_list = []
    try:
        tasks_lists = api_token.filter_tasks(query=filters)
    except Exception as error:
        logging.error(error)
        sys.exit(1)
    logging.debug(f"({filters}) filtered tasks:\n")
    for task_list in tasks_lists:
        for task in task_list:
            tasks_list.append(task)
            logging.debug(f"{task.content}")
    return tasks_list


def sort_tasks_date(tasks: list) -> list:
    """!
    Sort the tasks by date, oldest to newest

    @param tasks The list of tasks to sort

    @return The sorted list of tasks, oldest to newest
    """
    tasks.sort(key=lambda x: x.created_at)
    logging.debug(f"Sorted tasks:\n")
    for task in tasks:
        logging.debug(f"{task.content}")
    return tasks


def convert_priority(priority):
    """!
    Convert API priority (4 is highest) to UI priority (1 is highest)

    @param priority The priority to convert

    @return The converted priority

    @raises ValueError: If the priority is not between 1 and 4
    """
    if priority not in {1, 2, 3, 4}:
        raise ValueError(f"Invalid priority: {priority}. Must be between 1 and 4.")

    priority_map = {1: 4, 2: 3, 3: 2, 4: 1}
    return priority_map[priority]


def prioritize_tasks(tasks: list, p: int, max_size: int) -> list:
    """!
    Prioritize the tasks

    @param tasks The list of tasks to prioritize
    @param p The priority to set, 1-4, 4 being the highest priority
    @param max_size The maximum number of tasks to prioritize

    @return The list of tasks with the new priority
    """
    for i in range(0, max_size):
        try:
            is_success = api_token.update_task(task_id=tasks[i].id, priority=p)
            logging.info(
                f"Priority changed:\n- {is_success['content']}: P{convert_priority(tasks[i].priority)} -> P{convert_priority(p)}\n"
            )
        except Exception as error:
            logging.error(error)
            sys.exit(1)
    logging.debug(f"Prioritized tasks:\n{tasks}\n")
    return tasks


def move_task_to_a_parent(task: object, parent_id: str) -> None:
    """!
    Move a task to today

    @param task The task to move
    """

    task_duration = task.duration
    if task_duration == None:
        task_duration = 60
    else:
        task_duration = task.duration.amount
    retval = api_token.update_task(
        task_id=task.id,
        due_string="today at 18:00",
        duration=task_duration,
        duration_unit="minute",
    )
    if retval is None:
        logging.error(f"Failed to move {task.content} to today")
        sys.exit(1)

    try:
        api_token.move_task(
            task_id=task.id,
            project_id=parent_id,
        )
        logging.info(f"Moved {task.content} to today\n")
    except Exception as error:
        logging.error(error)
        sys.exit(1)


def fill_today_tasks(
    tasks_pool: list, task_reschedule_time: datetime.datetime
) -> datetime.datetime:
    """!
    Fill the tasks for today based on the user's configuration

    @param tasks_pool The list of tasks to reschedule for today
    @param task_reschedule_time The starting time to reschedule the tasks to

    @return The new reschedule starting time to use for the next tasks
    """
    today_tasks = get_tasks("today")
    no_duration_tasks_pcs = 0
    tasks_duration_min = 0
    usr_no_duration_tasks_pcs = int(config.get("USER", "number_of_tasks"))
    usr_tasks_duration_min = int(config.get("USER", "task_duration"))

    # Get current number of tasks with no duration and total duration
    for task in today_tasks:
        logging.debug(f"Task: {task}")
        if task.duration == None:
            no_duration_tasks_pcs += 1
        elif task.duration.amount > 0:
            if task.duration.unit == "minute":
                tasks_duration_min += task.duration.amount
            elif task.duration.unit == "hour":
                tasks_duration_min += task.duration.amount * 60

    for task in tasks_pool:
        # Tasks with no duration
        if no_duration_tasks_pcs < usr_no_duration_tasks_pcs:
            logging.debug(f"Task: {task}")
            if task.duration == None:
                no_duration_tasks_pcs += 1
                due_str = f"today at {task_reschedule_time.hour:02}:{task_reschedule_time.minute:02}"
                api_token.update_task(
                    task_id=task.id,
                    due_string=due_str,
                )
                logging.info(f"Rescheduled {task.content} for today\n")
        # Tasks with duration
        if tasks_duration_min < usr_tasks_duration_min:
            if task.duration != None:
                if task.duration.amount > 0:
                    if task.duration.unit == "minute":
                        tasks_duration_min += task.duration.amount
                        task_reschedule_time = (
                            task_reschedule_time
                            + datetime.timedelta(minutes=task.duration.amount)
                        )
                        due_str = f"today at {task_reschedule_time.hour:02}:{task_reschedule_time.minute:02}"
                        api_token.update_task(
                            task_id=task.id,
                            due_string=due_str,
                            duration=task.duration.amount,
                            duration_unit=task.duration.unit,
                        )
                        logging.info(f"Rescheduled {task.content} for today\n")
                    elif task.duration.unit == "hour":
                        tasks_duration_min += task.duration.amount * 60
                        task_reschedule_time = (
                            task_reschedule_time
                            + datetime.timedelta(hours=task.duration.amount)
                        )
                        due_str = f"today at {task_reschedule_time.hour:02}:{task_reschedule_time.minute:02}"
                        api_token.update_task(
                            task_id=task.id,
                            due_string=due_str,
                            duration=task.duration.amount,
                            duration_unit=task.duration.unit,
                        )
        if (
            no_duration_tasks_pcs == usr_no_duration_tasks_pcs
            and tasks_duration_min == usr_tasks_duration_min
        ):
            break
    return task_reschedule_time


if __name__ == "__main__":
    # Create the command line parser
    cmd = CommandLineParser()
    cmd.user_input()

    # Create the config parser
    config = configparser.ConfigParser()
    config.read(ini_path)

    # API token must be set
    try:
        if keyring.get_password("system", "todoist-api-token") is None:
            raise Exception("No API token provided")
    except Exception as error:
        logging.error(error)

    # Create the TodoistAPI object
    api_token = TodoistAPI(keyring.get_password("system", "todoist-api-token"))

    run_hour = int(config.get("USER", "run_hour"))
    run_minute = int(config.get("USER", "run_minute"))

    logging.info(f"todoist-prioritizer {current_version}\n")
    logging.info("todoist-prioritizer is running...")

    while True:
        current_time = datetime.datetime.now().time()
        run_time = datetime.time(run_hour, run_minute)
        if (
            current_time.hour == run_time.hour
            and current_time.minute == run_time.minute
        ):
            # Prioritize the tasks
            p1_tasks = get_tasks("P1")
            p1_tasks_size = len(p1_tasks)
            p1_tasks_target_size = int(config.get("USER", "p1_tasks"))
            p2_tasks = sort_tasks_date(get_tasks("P2"))
            if p1_tasks_size < p1_tasks_target_size:
                logging.info(
                    f"You have {p1_tasks_size}/{p1_tasks_target_size} P1 tasks"
                )
                prioritize_tasks(p2_tasks, 4, p1_tasks_target_size - p1_tasks_size)

            p2_tasks = get_tasks("P2")
            p2_tasks_size = len(p2_tasks)
            p2_tasks_target_size = int(config.get("USER", "p2_tasks"))
            p3_tasks = sort_tasks_date(get_tasks("P3"))
            if p2_tasks_size < p2_tasks_target_size:
                logging.info(
                    f"You have {p2_tasks_size}/{p2_tasks_target_size} P2 tasks"
                )
                prioritize_tasks(p3_tasks, 3, p2_tasks_target_size - p2_tasks_size)

            p3_tasks = get_tasks("P3")
            p3_tasks_size = len(p3_tasks)
            p3_tasks_target_size = int(config.get("USER", "p3_tasks"))
            p4_tasks = sort_tasks_date(get_tasks("P4"))
            if p3_tasks_size < p3_tasks_target_size:
                logging.info(
                    f"You have {p3_tasks_size}/{p3_tasks_target_size} P3 tasks"
                )
                prioritize_tasks(p4_tasks, 2, p3_tasks_target_size - p3_tasks_size)

            # Fill tasks for today
            reschedule_starting_time = datetime.datetime.now()
            reschedule_starting_time = reschedule_starting_time.replace(
                hour=18, minute=0
            )

            reschedule_starting_time = fill_today_tasks(
                p1_tasks, reschedule_starting_time
            )
            reschedule_starting_time = fill_today_tasks(
                p2_tasks, reschedule_starting_time
            )
            reschedule_starting_time = fill_today_tasks(
                p3_tasks, reschedule_starting_time
            )
            reschedule_starting_time = fill_today_tasks(
                p4_tasks, reschedule_starting_time
            )

            # Move the first P1 task to a parent
            parent_id = config.get("USER", "parent_id")
            if parent_id != "None" and p1_tasks:
                move_task_to_a_parent(p1_tasks[0], parent_id)

            check_for_updates()
            sleep(60)  # Run only once
        else:
            sleep(60)

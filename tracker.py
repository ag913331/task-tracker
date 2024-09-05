import argparse
import json
import logging
import os

from enum import Enum
from typing import Tuple, List
from dataclasses import dataclass
from functools import lru_cache
from logging.handlers import RotatingFileHandler

MAX_TASK_NAME_LENGTH = 100
TASKS_FILE = "tasks.json"

@lru_cache(maxsize=None)
def get_logger(log_name):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    )

    os.makedirs(f"logs", exist_ok=True)
    fh = RotatingFileHandler(
        f"logs/{log_name}.log", 
        maxBytes=1024 * 1024 * 10, 
        backupCount=10
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    )

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger

LOG = get_logger("task-tracker")

class Action(Enum):
    """Represents the action type - add | update | list | delete."""
    ADD = "add"
    UPDATE = "update"


class TaskStatus(Enum):
    """Represents the status of a task."""
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"


@dataclass
class Task:
    """
    Represents a task in the task tracker.

    Attributes:
        id (int): The unique identifier for the task.
        name (str): The name or description of the task.
        status (TaskStatus): The current status of the task, defaulting to TaskStatus.PENDING.
    """
    id: int
    name: str
    status: TaskStatus = TaskStatus.TODO


def validate_task_name(task_name: str) -> Tuple[bool, str]:
    """
    Validates the name of a task.

    Args:
        task_name (str): The task name to validate.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating if the task name is valid,
                          and a string with an error message if invalid.
    """
    if not task_name.strip():
        return False, "Task name cannot be empty."
    if len(task_name) > MAX_TASK_NAME_LENGTH:
        return False, f"Task name cannot exceed {MAX_TASK_NAME_LENGTH} characters."
    if any(c in task_name for c in '/\\'):
        return False, "Task name cannot contain slashes."
    return True, ""

def load_tasks() -> List[Task]:
    """
    Loads tasks from a JSON file.

    Returns:
        List[Task]: A list of Task objects loaded from the JSON file. If the file is not found or is empty,
                    an empty list is returned.
    """
    try:
        with open(TASKS_FILE, "r") as file:
            tasks_data = json.load(file)
            return [
                Task(id=task['id'], name=task['name'], status=TaskStatus(task['status']))
                for task in tasks_data
            ]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tasks(tasks: List[Task]):
    """
    Saves a list of tasks to a JSON file.

    Args:
        tasks (List[Task]): The list of Task objects to be saved.
    """
    with open(TASKS_FILE, "w") as file:
        json.dump([{"id": task.id, "name": task.name, "status": task.status.value} for task in tasks], file, indent=4)

def add_task(task_name: str):
    """
    Adds a new task to the task tracker.

    Args:
        task_name (str): The name of the task to add.
    
    Returns:
        None
    """
    tasks = load_tasks()
    new_id = max([task.id for task in tasks], default=0) + 1
    new_task = Task(id=new_id, name=task_name)
    tasks.append(new_task)
    save_tasks(tasks)
    LOG.info(f"[+] New task '{task_name}' added.")

def handle_task(task_name: str, action: Action):
    valid, error_message = validate_task_name(task_name)
    if not valid:
        LOG.error(f"[ERR] Task input validation: {error_message}")
        return
    
    if action == Action.ADD:
        add_task(task_name)
    elif action == Action.UPDATE:
        # Here you would implement update functionality
        print(f"Task '{task_name}' updated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Task tracker CLI")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--add", type=str, help="Name of the task to add")
    group.add_argument("-u", "--update", type=str, help="Name of the task to update")
    args = parser.parse_args()

    if args.add:
        handle_task(args.add, Action.ADD)
    elif args.update:
        handle_task(args.update, Action.UPDATE)

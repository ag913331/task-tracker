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

def update_task(task_id: int, updated_name: str):
    """
    Updates the name of a task with the given task_id.

    Args:
        task_id (int): The ID of the task to update.
        updated_name (str): The new name for the task.
    
    Returns:
        None
    """
    # Load existing tasks from the file
    tasks = load_tasks()

    # Find the task by ID
    task_to_update = next((task for task in tasks if task.id == task_id), None)

    if task_to_update is None:
        LOG.error(f"Task with ID {task_id} not found.")
        return

    # Validate the updated task name
    is_valid, error_message = validate_task_name(updated_name)
    if not is_valid:
        LOG.error(f"Task input validation: {error_message}")
        return

    # Update the task name
    task_to_update.name = updated_name

    # Save the updated tasks back to the file
    save_tasks(tasks)
    
    LOG.info(f"[+u] Task ID {task_id} updated successfully to '{updated_name}'.")


def delete_task(task_id: int):
    """
    Deletes a task with the given task_id from the task tracker.

    Args:
        task_id (int): The ID of the task to delete.
    
    Returns:
        None
    """
    # Load existing tasks from the file
    tasks = load_tasks()

    # Find the task by ID
    task_to_delete = next((task for task in tasks if task.id == task_id), None)

    if task_to_delete is None:
        LOG.error(f"Task with ID {task_id} not found.")
        return

    # Remove the task from the list
    tasks = [task for task in tasks if task.id != task_id]

    # Save the updated task list back to the file
    save_tasks(tasks)
    
    LOG.info(f"[-] Task ID {task_id} deleted.")


def update_status(task_id: int, updated_status: str):
    """
    Updates the status of a task with the given task_id.

    Args:
        task_id (int): The ID of the task to update.
        updated_status (str): The new status for the task ('pending', 'in-progress', 'completed').
    
    Returns:
        None
    """
    # Define valid statuses
    valid_statuses = [status.value for status in TaskStatus]
    
    # Load existing tasks from the file
    tasks = load_tasks()

    # Find the task by ID
    task_to_update = next((task for task in tasks if task.id == task_id), None)

    if task_to_update is None:
        LOG.error(f"Task with ID {task_id} not found.")
        return

    # Validate the updated status
    if updated_status.lower() not in valid_statuses:
        LOG.error(f"'{updated_status}' is not a valid status. Valid statuses are: {valid_statuses}.")
        return

    # Update the task status
    task_to_update.status = TaskStatus(updated_status.lower())

    # Save the updated task list back to the file
    save_tasks(tasks)

    LOG.info(f"[+u] Task ID {task_id} status updated successfully to '{updated_status}'.")


def list_tasks(task_status: str):
    """
    Lists tasks filtered by the given task status.

    Args:
        task_status (str): The status of the tasks to list. 
                           Options: 'all', 'todo', 'in-progress', 'done'.

    Returns:
        None
    """
    tasks = load_tasks()

    if task_status not in ["all", "todo", "in-progress", "done"]:
        LOG.error(f"Error: Invalid status '{task_status}'. Valid options are: all, todo, in-progress, done.")
        return

    if task_status == "all":
        filtered_tasks = tasks
    else:
        filtered_tasks = [task for task in tasks if task.status.value == task_status]

    if not filtered_tasks:
        LOG.info(f"No tasks found with status '{task_status}'.")
    else:
        for task in filtered_tasks:
            print(f"ID: {task.id}, Name: {task.name}, Status: {task.status.value}")


def handle_task(args: argparse.Namespace):
    if args.action in ["add", "update"]:
        valid, error_message = validate_task_name(args.name)
        if not valid:
            LOG.error(f"Task input validation: {error_message}")
            return
    
    if args.action == "add":
        add_task(args.name)
    elif args.action == "update":
        update_task(int(args.id), args.name)
    elif args.action == "delete":
        delete_task(int(args.id))
    elif args.action == "mark":
        update_status(int(args.id), args.status)
    elif args.action == "list":
        list_tasks(args.status)
    else:
        LOG.error(f"Invalid action: {args.action}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Task tracker CLI")
    subparsers = parser.add_subparsers(help="list of actions", dest="action", required=True)

    add_task_parser = subparsers.add_parser("add", help="Add task related arguments")
    add_task_parser.add_argument("name", type=str, help="Name of the task to add")

    update_task_parser = subparsers.add_parser("update", help="Update task related arguments")
    update_task_parser.add_argument("id", type=int, help="Task ID")
    update_task_parser.add_argument("name", type=str, help="Task's new name")
    
    mark_task_parser = subparsers.add_parser("mark", help="Update task status related arguments")
    mark_task_parser.add_argument("id", type=int, help="Task ID")
    mark_task_parser.add_argument("status", choices=["todo", "in-progress", "done"], help="Task's new status")

    delete_task_parser = subparsers.add_parser("delete", help="Delete task related arguments")
    delete_task_parser.add_argument("id", type=int, help="Task ID")
    
    list_task_parser = subparsers.add_parser("list", help="List tasks related arguments")
    list_task_parser.add_argument("status", nargs="?", choices=["all", "todo", "in-progress", "done"], default="all", help="Task type")

    args = parser.parse_args()

    handle_task(args)

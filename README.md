# Task Tracker

## Description
This Task Tracker CLI is a command-line application for managing tasks, where tasks are saved in a JSON file. Users can add, update, delete, and list tasks with various statuses. The application ensures tasks are named properly, avoids invalid characters, and restricts task status to pre-defined states (`todo`, `in-progress`, `done`).

[Project URL](https://roadmap.sh/projects/task-tracker)

## Setup & Installation

### Requirements
To run the Task Tracker CLI, you'll need the following:
- Python 3.7+

### Installation

1. Clone the Repository

- via SSH:
```bash
git clone git@github.com:ag913331/task-tracker.git
cd task-tracker
```

- via HTTPS:
```bash
git clone https://github.com/ag913331/task-tracker.git
cd task-tracker
```

## Features

- **Add a Task**: Add a new task with a name and automatically assign it an ID and a default status (`todo`).
- **Update a Task**: Modify an existing task's name.
- **Delete a Task**: Remove a task by its unique ID.
- **Update Task Status**: Change the status of a task (`todo`, `in-progress`, `done`).
- **List Tasks**: View all tasks or filter by task status (`all`=default, `todo`, `in-progress`, `done`).

All tasks are stored persistently in a JSON file.

## How it works?

### Task structure
Each task is represented as an object with the following properties:
- `id` (int): A unique identifier for the task.
- `name` (str): The name or title of the task.
- `status` (enum): The current status of the task (`todo`, `in-progress`, `done`).
- `created_at` (str): The current timestamp when a task is created.
- `updated_at` (str): The current timestamp when a task is updated.

### Argument descriptions

The Task Tracker CLI uses the `argparse` module to manage command-line arguments. This allows for organized handling of various actions related to task management. The arguments are grouped into subparsers (`add`, `update`, `mark`, `delete`, `list`), which are specific to each action. This design ensures that users cannot input a wrong combination of arguments for any given action.

### Subparsers (actions)

1. `add`: Adds a new task to the task tracker.
Arguments:
    - `name`: The name of the task to add. This argument is required to provide a description of the task being created.

2. `update`: Updates an existing task.
Arguments:
    - `id`: The unique identifier of the task to update. This is required to specify which task is being modified.
    - `name`: The new name for the task. This argument is required to set a new description for the specified task.

3. `mark`: Updates the status of an existing task.
    - `id`: The unique identifier of the task to update. This is required to identify which task's status is being changed.
    - `status`: The new status for the task. Valid options are `todo`, `in-progress`, and `done`. This argument is required to set the task's current state.

4. `delete`: Deletes a task from the task tracker.
    - `id`: The unique identifier of the task to delete. This argument is required to specify which task is being removed from the tracker.

5. `list`: Lists tasks based on their status.
    - `status` (optional): The status of the tasks to list. Options are `all`, `todo`, `in-progress`, and `done`. This argument defaults to `all` if not specified, allowing the user to view all tasks or filter by status.

The identical names of the arguments do not conflict with each other, since their are being used with their respective parser. For more information about subparsers please see [argparser-subparsers](https://docs.python.org/3/library/argparse.html#sub-commands).


### Core functionalities
1. **Adding a Task**:

A task is added by providing a name. The task is automatically assigned a unique ID and a status of `todo`. Input validation ensures task names are not empty, too long, or contain invalid characters like slashes.

```bash
python tracker.py add "New Task"
```

2. **Updating a Task**:

A task's name can be updated by providing its id and the new name. Input validation ensures task names are not empty, too long, or contain invalid characters like slashes.

```bash
python tracker.py update 1 "Updated Task Name"
```

3. **Deleting a Task**:

A task can be deleted by its `id`.

```bash
python tracker.py delete 1
```

4. **Updating Task Status**:

The task's status can be updated to `todo`, `in-progress`, or `done` by providing its `id` and the new status.

```bash
python tracker.py mark 1 in-progress
```

5. **Listing Tasks**:

Tasks can be listed by status or all at once. For instance, you can list tasks with the status `todo`, `in-progress`, or `done`.

```bash
python tracker.py list done
```

You can list all tasks by using keyword `all` or not providing a status at all.

- With `all`:
```bash
python tracker.py list all
```

- Skipping the status keyword will result in the same output as using `all`.
```bash
python tracker.py list
```

## Code structure

- `tracker.py`: Main CLI entry point where arguments are parsed and passed to their respective functions.

- Functions:
    - `add_task()`: Adds a new task.
    - `update_task()`: Updates an existing task's name.
    - `delete_task()`: Deletes a task.
    - `update_status()`: Updates a task's status.
    - `list_tasks()`: Lists tasks based on the provided status.
    - `load_tasks()`: Loads tasks from the JSON file.
    - `save_tasks()`: Saves tasks to the JSON file.
    - `validate_task_name()`: Validates task names to ensure they meet criteria (non-empty, proper length, no invalid characters).

## Important details

- **Task Persistence**: Tasks are saved in a JSON file (`tasks.json`) that persists data between sessions.
- **Task IDs**: Task IDs are automatically generated and unique, making them easy to reference for updates, deletions, or status changes.
- **Input Validation**: Names and statuses are validated to ensure correct input. Invalid input will result in error messages, preventing incorrect data from being stored.

## Future Enhancements

- Add the ability to prioritize tasks.
- Introduce a due date feature for tasks.
- Add more sophisticated search and filtering options for tasks.
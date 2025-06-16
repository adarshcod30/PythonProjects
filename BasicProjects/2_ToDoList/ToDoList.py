import os
import datetime  # For handling dates and times


# --- Configuration ---
TASK_FILE = 'tasks.txt'
# The format for each line in the task file will be:
# ID,Description,IsCompleted,CreationDateTime,DeadlineDateTime
# Example: 1,Buy groceries,False,2024-06-16 16:00:00.000000,2024-06-17 23:59:00.000000

# --- Helper Functions for Time Handling ---


def _parse_datetime_input(prompt: str, optional: bool = False) -> datetime.datetime | None:
    """
    Prompts the user for a date and time, parses it, and returns a datetime object.
    Includes basic validation and allows for optional input.

    Args:
        prompt (str): The message to display to the user.
        optional (bool): If True, allows the user to press Enter for no input.

    Returns:
        datetime.datetime | None: The parsed datetime object, or None if input is empty
                                  and optional is True, or if parsing fails.
    """
    while True:
        user_input = input(f"{prompt} (YYYY-MM-DD HH:MM, e.g., 2024-12-31 14:30) or press Enter to skip: ").strip()
        if not user_input:
            if optional:
                return None
            else:
                print("Input cannot be empty. Please enter a date and time.")
                continue

        try:
            # Attempt to parse the input string into a datetime object
            return datetime.datetime.strptime(user_input, '%Y-%m-%d %H:%M')
        except ValueError:
            print("Invalid date/time format. Please use YYYY-MM-DD HH:MM.")
        except Exception as e:
            print(f"An unexpected error occurred during date/time parsing: {e}")


def _format_timedelta(delta: datetime.timedelta) -> str:
    """
    Formats a datetime.timedelta object into a human-readable string (e.g., "2 days, 3 hours").

    Args:
        delta (datetime.timedelta): The time difference to format.

    Returns:
        str: A human-readable string representation of the timedelta.
    """
    # Get absolute value of delta for consistent formatting
    total_seconds = int(abs(delta).total_seconds())

    # Calculate days, hours, minutes, seconds
    days, remainder = divmod(total_seconds, 86400) # 86400 seconds in a day
    hours, remainder = divmod(remainder, 3600)    # 3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60)      # 60 seconds in a minute

    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 and not days and not hours and not minutes: # Only show seconds if less than a minute
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    if not parts: # If delta is 0 seconds
        return "0 seconds"
    return ", ".join(parts)


# --- Task Class ---
class Task:
    """
    Represents a single To-Do task with ID, description, completion status,
    creation timestamp, and an optional deadline.
    """
    def __init__(self, task_id: int, description: str, is_completed: bool,
                 creation_datetime: datetime.datetime, deadline_datetime: datetime.datetime | None):
        """
        Initializes a new Task object.

        Args:
            task_id (int): A unique identifier for the task.
            description (str): The description of the task.
            is_completed (bool): The completion status of the task.
            creation_datetime (datetime.datetime): The timestamp when the task was created.
            deadline_datetime (datetime.datetime | None): The optional deadline for the task.
        """
        if not isinstance(task_id, int) or task_id <= 0:
            raise ValueError("Task ID must be a positive integer.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Task description cannot be empty.")
        if not isinstance(is_completed, bool):
            raise ValueError("is_completed must be a boolean.")
        if not isinstance(creation_datetime, datetime.datetime):
            raise ValueError("creation_datetime must be a datetime object.")
        if deadline_datetime is not None and not isinstance(deadline_datetime, datetime.datetime):
            raise ValueError("deadline_datetime must be a datetime object or None.")

        self.id = task_id
        self.description = description.strip()
        self.is_completed = is_completed
        self.creation_datetime = creation_datetime
        self.deadline_datetime = deadline_datetime

    def get_time_status(self) -> str:
        """
        Calculates and returns the time status relative to the deadline.
        Returns strings like "X time left", "X time passed", or "No deadline".

        Returns:
            str: A formatted string indicating the time status.
        """
        if self.is_completed:
            return "Task Completed"

        if self.deadline_datetime is None:
            return "No Deadline Set"

        now = datetime.datetime.now()
        time_difference = self.deadline_datetime - now

        if time_difference.total_seconds() > 0:
            # Deadline is in the future
            return f"Time Left: {_format_timedelta(time_difference)}"
        else:
            # Deadline has passed
            return f"Overdue by: {_format_timedelta(time_difference)}"

    def __str__(self):
        """
        Returns a human-readable string representation of the Task,
        including its ID, status, description, creation date, and deadline status.
        """
        status_text = ""
        if self.is_completed:
            status_text = "[COMPLETED]"
        elif self.deadline_datetime and datetime.datetime.now() > self.deadline_datetime:
            status_text = "[OVERDUE]"
        else:
            status_text = "[ACTIVE]"

        creation_str = self.creation_datetime.strftime('%Y-%m-%d %H:%M')
        deadline_str = self.deadline_datetime.strftime('%Y-%m-%d %H:%M') if self.deadline_datetime else 'N/A'
        time_status = self.get_time_status()

        return (f"ID: {self.id} | Status: {status_text}\n"
                f"  Description: {self.description}\n"
                f"  Created On: {creation_str}\n"
                f"  Deadline: {deadline_str} ({time_status})")

    def to_file_format(self) -> str:
        """
        Converts the task object into a comma-separated string suitable for saving to file.
        Uses ISO format for datetimes to ensure accurate parsing later.
        """
        # Convert datetime objects to string; use 'None' string for missing deadline
        creation_str = self.creation_datetime.isoformat()
        deadline_str = self.deadline_datetime.isoformat() if self.deadline_datetime else 'None'
        return f"{self.id},{self.description},{self.is_completed},{creation_str},{deadline_str}"

# --- ToDoListManager Class ---
class ToDoListManager:
    """
    Manages the collection of To-Do tasks, including file operations and various
    task management functionalities.
    """
    def __init__(self, filename: str = TASK_FILE):
        """
        Initializes the ToDoListManager. Loads tasks from the specified file.

        Args:
            filename (str): The name of the file to store tasks.
        """
        self.filename = filename
        self.tasks: list[Task] = []
        self._next_id = 1  # Used to generate unique IDs for new tasks
        self._load_tasks() # Load tasks when the manager starts

    def _load_tasks(self):
        """
        Loads tasks from the specified file. Handles file not found, empty file,
        and malformed lines. Updates _next_id based on the highest existing task ID.
        """
        self.tasks = [] # Clear current tasks before loading
        max_id = 0
        if not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0:
            print(f"No existing tasks file found or file '{self.filename}' is empty. Starting with an empty list.")
            return

        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line: # Skip empty lines
                        continue
                    parts = line.split(',', 4) # Split into at most 5 parts: ID,Desc,Complete,Created,Deadline
                    if len(parts) == 5:
                        try:
                            task_id = int(parts[0])
                            description = parts[1]
                            is_completed = parts[2].lower() == 'true'
                            creation_dt = datetime.datetime.fromisoformat(parts[3])
                            # Handle optional deadline
                            deadline_dt = datetime.datetime.fromisoformat(parts[4]) if parts[4] != 'None' else None

                            task = Task(task_id, description, is_completed, creation_dt, deadline_dt)
                            self.tasks.append(task)
                            if task_id > max_id:
                                max_id = task_id
                        except (ValueError, IndexError, TypeError) as e:
                            print(f"Warning: Skipping malformed line {line_num} in '{self.filename}': '{line}' - Error: {e}")
                    else:
                        print(f"Warning: Skipping malformed line {line_num} in '{self.filename}': '{line}' - Expected 5 parts, got {len(parts)}.")
            self._next_id = max_id + 1
            print(f"Tasks loaded successfully from '{self.filename}'. Next available ID: {self._next_id}")
        except IOError as e:
            print(f"Error loading tasks from '{self.filename}': {e}")
            self.tasks = [] # Clear tasks to prevent corrupted data issues
        except Exception as e:
            print(f"An unexpected error occurred while loading tasks: {e}")
            self.tasks = []

    def _save_tasks(self):
        """
        Saves the current list of tasks to the specified file.
        Overwrites existing content.
        """
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                for task in self.tasks:
                    f.write(task.to_file_format() + '\n')
            # print(f"Tasks saved to '{self.filename}'.") # Uncomment for debugging
        except IOError as e:
            print(f"Error saving tasks to '{self.filename}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving tasks: {e}")

    def add_task(self):
        """
        Prompts the user for a task description and an optional deadline.
        Adds the new task to the list with the current timestamp as creation time.
        """
        print("\n--- Add New Task ---")
        description = input("Enter task description: ").strip()
        if not description:
            print("Task description cannot be empty.")
            return

        deadline = _parse_datetime_input("Enter deadline", optional=True)

        try:
            # Create a new Task object with the next available ID and current time
            new_task = Task(self._next_id, description, False, datetime.datetime.now(), deadline)
            self.tasks.append(new_task)
            self._next_id += 1 # Increment for the next task
            self._save_tasks() # Save changes to file
            print(f"Task added: {new_task.description} (ID: {new_task.id})")
        except ValueError as e:
            print(f"Error adding task: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while adding task: {e}")


    def remove_task(self):
        """
        Prompts the user for a task ID and removes the corresponding task.
        """
        print("\n--- Remove Task ---")
        if not self.tasks:
            print("No tasks to remove.")
            return
        
        # Display tasks with IDs for user reference
        self.view_all_tasks()

        try:
            task_id_input = input("Enter the ID of the task to remove: ").strip()
            if not task_id_input:
                print("No ID entered. Returning to menu.")
                return

            task_id = int(task_id_input)
            
            initial_task_count = len(self.tasks)
            # Create a new list excluding the task to be removed
            self.tasks = [task for task in self.tasks if task.id != task_id]

            if len(self.tasks) < initial_task_count:
                self._save_tasks()
                print(f"Task with ID {task_id} removed successfully.")
            else:
                print(f"Task with ID {task_id} not found.")
        except ValueError:
            print("Invalid input. Please enter a valid number for the ID.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def complete_task(self):
        """
        Prompts the user for a task ID and marks the corresponding task as complete.
        """
        print("\n--- Complete Task ---")
        if not self.tasks:
            print("No tasks to complete.")
            return

        self.view_all_tasks() # Show all tasks for user reference

        try:
            task_id_input = input("Enter the ID of the task to mark as complete: ").strip()
            if not task_id_input:
                print("No ID entered. Returning to menu.")
                return

            task_id = int(task_id_input)
            found_and_updated = False
            for task in self.tasks:
                if task.id == task_id:
                    if not task.is_completed:
                        task.is_completed = True # Mark as complete
                        self._save_tasks()
                        print(f"Task with ID {task_id} marked as complete.")
                        found_and_updated = True
                        break
                    else:
                        print(f"Task with ID {task_id} is already completed.")
                        found_and_updated = True
                        break
            if not found_and_updated:
                print(f"Task with ID {task_id} not found.")
        except ValueError:
            print("Invalid input. Please enter a valid number for the ID.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def edit_task(self):
        """
        Allows the user to edit the description, deadline, or completion status of an existing task.
        """
        print("\n--- Edit Task ---")
        if not self.tasks:
            print("No tasks to edit. Add some first!")
            return

        self.view_all_tasks() # Show all tasks with IDs

        try:
            task_id_input = input("Enter the ID of the task to edit: ").strip()
            if not task_id_input:
                print("No ID entered. Returning to menu.")
                return

            task_id = int(task_id_input)
            task_to_edit: Task | None = None
            for task in self.tasks:
                if task.id == task_id:
                    task_to_edit = task
                    break

            if task_to_edit is None:
                print(f"Task with ID {task_id} not found.")
                return

            print(f"\n--- Editing Task ID: {task_to_edit.id} ---")
            print(f"Current Description: {task_to_edit.description}")
            print(f"Current Deadline: {task_to_edit.deadline_datetime.strftime('%Y-%m-%d %H:%M') if task_to_edit.deadline_datetime else 'N/A'}")
            print(f"Current Status: {'Completed' if task_to_edit.is_completed else 'Active'}")

            updated = False

            # Edit Description
            new_description = input(f"Enter new description (current: '{task_to_edit.description}', leave blank to keep): ").strip()
            if new_description:
                task_to_edit.description = new_description
                updated = True

            # Edit Deadline
            new_deadline_input = input(f"Enter new deadline (current: '{task_to_edit.deadline_datetime.strftime('%Y-%m-%d %H:%M') if task_to_edit.deadline_datetime else 'N/A'}', YYYY-MM-DD HH:MM, 'clear' to remove, leave blank to keep): ").strip().lower()
            if new_deadline_input == 'clear':
                if task_to_edit.deadline_datetime is not None:
                    task_to_edit.deadline_datetime = None
                    updated = True
            elif new_deadline_input:
                try:
                    parsed_deadline = datetime.datetime.strptime(new_deadline_input, '%Y-%m-%d %H:%M')
                    task_to_edit.deadline_datetime = parsed_deadline
                    updated = True
                except ValueError:
                    print("Invalid new deadline format. Keeping current deadline.")

            # Edit Completion Status
            new_status_input = input(f"Mark as complete? (y/n, current: {'y' if task_to_edit.is_completed else 'n'}, leave blank to keep): ").strip().lower()
            if new_status_input == 'y' and not task_to_edit.is_completed:
                task_to_edit.is_completed = True
                updated = True
            elif new_status_input == 'n' and task_to_edit.is_completed:
                task_to_edit.is_completed = False
                updated = True

            if updated:
                self._save_tasks()
                print("Task updated successfully!")
            else:
                print("No changes made to the task.")

        except ValueError:
            print("Invalid input. Please enter a valid number for the ID.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def view_all_tasks(self, sort_by: str = 'id', filter_by_status: str = 'all'):
        """
        Displays tasks based on sorting and filtering criteria.

        Args:
            sort_by (str): How to sort tasks ('id', 'creation_date', 'deadline').
            filter_by_status (str): Which tasks to show ('all', 'active', 'completed', 'overdue').
        """
        print("\n--- All Tasks ---")
        if not self.tasks:
            print("No tasks found.")
            return

        filtered_tasks = []
        now = datetime.datetime.now()

        for task in self.tasks:
            include_task = False
            if filter_by_status == 'all':
                include_task = True
            elif filter_by_status == 'active':
                # Active means not completed and not overdue (if deadline exists)
                if not task.is_completed and (task.deadline_datetime is None or task.deadline_datetime > now):
                    include_task = True
            elif filter_by_status == 'completed':
                if task.is_completed:
                    include_task = True
            elif filter_by_status == 'overdue':
                # Overdue means not completed and deadline has passed
                if not task.is_completed and task.deadline_datetime and task.deadline_datetime <= now:
                    include_task = True
            
            if include_task:
                filtered_tasks.append(task)

        if not filtered_tasks:
            print(f"No {filter_by_status} tasks found.")
            return

        # Sorting logic
        if sort_by == 'creation_date':
            display_list = sorted(filtered_tasks, key=lambda t: t.creation_datetime)
        elif sort_by == 'deadline':
            # Sort by deadline, None deadlines go to the end
            display_list = sorted(filtered_tasks, key=lambda t: t.deadline_datetime if t.deadline_datetime is not None else datetime.datetime.max)
        else: # Default to sort by ID
            display_list = sorted(filtered_tasks, key=lambda t: t.id)


        for task in display_list:
            print(task)
            print("-" * 30) # Separator for readability

    def filter_tasks_menu(self):
        """Presents options to filter tasks and calls view_all_tasks with filter."""
        print("\n--- Filter Tasks ---")
        print("1. Show All Tasks")
        print("2. Show Active Tasks")
        print("3. Show Completed Tasks")
        print("4. Show Overdue Tasks")
        print("5. Back to Main Menu")

        choice = input("Enter your choice: ").strip()
        filter_option = 'all'

        if choice == '1':
            filter_option = 'all'
        elif choice == '2':
            filter_option = 'active'
        elif choice == '3':
            filter_option = 'completed'
        elif choice == '4':
            filter_option = 'overdue'
        elif choice == '5':
            return # Go back to main menu
        else:
            print("Invalid choice. Showing all tasks by default.")

        self.view_all_tasks(sort_by='deadline', filter_by_status=filter_option)

    def sort_tasks_menu(self):
        """Presents options to sort tasks and calls view_all_tasks with sort criteria."""
        print("\n--- Sort Tasks ---")
        print("1. Sort by Task ID (Default)")
        print("2. Sort by Creation Date")
        print("3. Sort by Deadline")
        print("4. Back to Main Menu")

        choice = input("Enter your choice: ").strip()
        sort_option = 'id' # Default

        if choice == '1':
            sort_option = 'id'
        elif choice == '2':
            sort_option = 'creation_date'
        elif choice == '3':
            sort_option = 'deadline'
        elif choice == '4':
            return # Go back to main menu
        else:
            print("Invalid choice. Sorting by Task ID.")
        
        self.view_all_tasks(sort_by=sort_option)

    def clear_completed_tasks(self):
        """
        Removes all tasks that are currently marked as completed.
        """
        print("\n--- Clear Completed Tasks ---")
        initial_count = len(self.tasks)
        self.tasks = [task for task in self.tasks if not task.is_completed]
        
        if len(self.tasks) < initial_count:
            self._save_tasks()
            print(f"{initial_count - len(self.tasks)} completed task(s) cleared successfully.")
        else:
            print("No completed tasks to clear.")

# --- Main Application Logic ---
def display_menu():
    """Displays the main menu options to the user."""
    print("\n--- To-Do List App Menu ---")
    print("1. Add New Task")
    print("2. Remove Task")
    print("3. Mark Task as Complete")
    print("4. Edit Task")
    print("5. View Tasks (with Filter/Sort Options)")
    print("6. Clear All Completed Tasks")
    print("7. Exit")
    print("---------------------------")

def main():
    """
    The main function to run the To-Do List application.
    """
    manager = ToDoListManager()

    print("\nWelcome to the Enhanced To-Do List App!")

    while True:
        display_menu()
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            manager.add_task()
        elif choice == '2':
            manager.remove_task()
        elif choice == '3':
            manager.complete_task()
        elif choice == '4':
            manager.edit_task()
        elif choice == '5': # View Tasks with Filter/Sort Sub-menu
            print("\n--- View Tasks Options ---")
            print("1. Filter Tasks by Status")
            print("2. Sort Tasks by Property")
            print("3. Back to Main Menu")
            view_choice = input("Enter your choice: ").strip()
            if view_choice == '1':
                manager.filter_tasks_menu()
            elif view_choice == '2':
                manager.sort_tasks_menu()
            elif view_choice == '3':
                pass # Go back to main menu
            else:
                print("Invalid choice. Returning to main menu.")

        elif choice == '6':
            manager.clear_completed_tasks()
        elif choice == '7':
            print("Exiting To-Do List App. Goodbye!")
            break # Exit the main loop
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main()

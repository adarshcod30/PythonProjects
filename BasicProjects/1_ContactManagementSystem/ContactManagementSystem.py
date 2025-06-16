# New python project

import os
import re
import csv

# --- Constants ---
DATABASE_FILE = "database.txt"
CSV_EXPORT_FILE = "contacts_export.csv"
VALID_GROUPS = ["Home", "Office"]  # Valid categories for contact groups

# --- ContactManager Class ---


class ContactManager:
    def __init__(self, database_file: str = DATABASE_FILE):
        """
        Initializes the ContactManager.
        Loads existing contacts from the specified database file at startup.

        Args:
            database_file (str): The name of the text file where contacts are
                stored.
        """
        self.database_file = database_file
        self.contacts: list[dict] = []  # Stores contacts as a list of dictionaries
        self._load_contacts()  # Load existing contacts when the manager is created

    def _load_contacts(self):
        """
        Loads contact data from the database file into the `self.contacts` list.
        Handles cases where the file doesn't exist or is empty.
        Includes basic error handling for file reading issues.
        """
        self.contacts = []  # Start with an empty list before loading
        if not os.path.exists(self.database_file):
            print(
                f"Database file '{self.database_file}' not found. A new one will be created upon first save."
            )
            return  # No file means no contacts to load yet

        try:
            with open(self.database_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(
                    f, 1
                ):  # Enumerate for line number in warnings
                    line = line.strip()  # Remove leading/trailing whitespace
                    if line:  # Process non-empty lines
                        parts = line.split(",")  # Split by comma
                        if (
                            len(parts) == 4
                        ):  # Expecting 4 parts: Name, Contact, Email, Group
                            self.contacts.append(
                                {
                                    "Name": parts[0],
                                    "Contact": parts[1],
                                    "Email": parts[2],
                                    "Group": parts[3],
                                }
                            )
                        else:
                            print(
                                f"Warning: Skipping malformed line {line_num} in '{self.database_file}': '{line}'. Expected 4 comma-separated values."
                            )
            print(
                f"Contacts loaded successfully from '{self.database_file}'. Total: {len(self.contacts)}."
            )
        except IOError as e:
            # Catch file I/O errors (e.g., permission issues)
            print(f"Error reading database file '{self.database_file}': {e}")
            self.contacts = (
                []
            )  # Clear contacts to prevent working with potentially corrupted data
        except Exception as e:
            # Catch any other unexpected errors during loading
            print(f"An unexpected error occurred while loading contacts: {e}")
            self.contacts = []

    def _save_contacts(self):
        """
        Saves the current list of contacts from memory back to the database file.
        Overwrites the existing file with the current state of contacts.
        Includes basic error handling for file writing issues.
        """
        try:
            with open(self.database_file, "w", encoding="utf-8") as f:
                for contact in self.contacts:
                    # Write each contact as a comma-separated line
                    f.write(
                        f"{contact['Name']},{contact['Contact']},{contact['Email']},{contact['Group']}\n"
                    )
            # print(f"Contacts saved to '{self.database_file}'.")  # Uncomment for debugging
        except IOError as e:
            # Catch file I/O errors (e.g., disk full, permission issues)
            print(f"Error writing to database file '{self.database_file}': {e}")
        except Exception as e:
            # Catch any other unexpected errors during saving
            print(f"An unexpected error occurred while saving contacts: {e}")

    def _is_contact_duplicate(self, name: str, contact_num: str) -> bool:
        """
        Checks if a contact with the same Name (case-insensitive) and
        Contact Number already exists in the current list.

        Args:
            name (str): The name to check for duplication.
            contact_num (str): The contact number to check for duplication.

        Returns:
            bool: True if a duplicate is found, False otherwise.
        """
        for existing_contact in self.contacts:
            if (
                existing_contact["Name"].lower() == name.lower()
                and existing_contact["Contact"] == contact_num
            ):
                return True
        return False

    def _validate_input(self, field_name: str, value: str) -> bool:
        """
        Performs basic validation for individual input fields.

        Args:
            field_name (str): The name of the field being validated (e.g., "Name", "Contact").
            value (str): The value entered by the user.

        Returns:
            bool: True if the input is valid, False otherwise (prints error message).
        """
        value = value.strip()  # Clean whitespace from input

        if not value:
            print(f"Error: {field_name} cannot be empty.")
            return False

        if field_name == "Contact":
            if not value.isdigit():  # Check if all characters are digits
                print("Error: Contact number must contain only digits.")
                return False
            if len(value) < 7:  # Simple check for a reasonable minimum length
                print("Warning: Contact number seems short. Please check its validity.")
        elif field_name == "Email":
            # Basic regex for email format: checks for @ and at least one . after @
            if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                print("Error: Invalid email format. (e.g., user@example.com)")
                return False
        elif field_name == "Group":
            if value not in VALID_GROUPS:
                print(
                    f"Error: Invalid group. Please choose from {', '.join(VALID_GROUPS)}."
                )
                return False
        return True  # Input is valid for the specified field

    def _display_single_contact(self, contact: dict, index: int | None = None):
        """
        Prints a single contact's details in a formatted way.
        Optionally includes an index for user reference.

        Args:
            contact (dict): The contact dictionary to display.
            index (int | None): An optional 1-based index to display before the contact.
        """
        prefix = f"Contact {index}:" if index is not None else ""
        print(f"\n{prefix}")
        print(f"  Name: {contact['Name']}")
        print(f"  Contact: {contact['Contact']}")
        print(f"  Email: {contact['Email']}")
        print(f"  Group: {contact['Group']}")
        print("-" * 30)  # Separator for readability

    def add_contact(self):
        """
        Prompts the user for Name, Contact, Email, and Group.
        Validates inputs, checks for duplicates, and adds the new contact
        to the list, then saves to the database file.
        """
        print("\n--- Add New Contact ---")

        # Get and validate Name
        name = input("Enter Name: ").strip()
        if not self._validate_input("Name", name):
            return

        # Get and validate Contact Number
        contact_num = input("Enter Contact Number: ").strip()
        if not self._validate_input("Contact", contact_num):
            return

        # Get and validate Email
        email = input("Enter Email Address: ").strip()
        if not self._validate_input("Email", email):
            return

        # Get and validate Group
        group = input(f"Enter Group ({'/'.join(VALID_GROUPS)}): ").strip()
        if not self._validate_input("Group", group):
            return

        # Check for duplicate contacts
        if self._is_contact_duplicate(name, contact_num):
            print(
                f"Error: A contact with Name '{name}' and Contact '{contact_num}' already exists."
            )
            return

        # Create the new contact dictionary
        new_contact = {
            "Name": name,
            "Contact": contact_num,
            "Email": email,
            "Group": group,
        }

        self.contacts.append(new_contact)  # Add to the in-memory list
        self._save_contacts()  # Save the updated list to file
        print("Contact added successfully!")

    def view_all_contacts(self, sorted_by_name: bool = True):
        """
        Displays all contacts currently loaded, optionally sorted by name.
        Each contact is displayed with a 1-based ID for user reference.

        Args:
            sorted_by_name (bool): If True, contacts are displayed sorted alphabetically by name.
        """
        print("\n--- All Contacts ---")
        if not self.contacts:
            print("No contacts found in the database. Add some first!")
            return

        # Create a display list, sorted if requested
        display_list = (
            sorted(self.contacts, key=lambda c: c["Name"].lower())
            if sorted_by_name
            else self.contacts
        )

        for i, contact in enumerate(display_list):
            self._display_single_contact(contact, i + 1)  # Display with 1-based index

    def view_specific_contact_by_id(self):
        """
        Prompts the user to enter a displayed ID number, then shows the details
        of the corresponding contact.
        """
        print("\n--- View Specific Contact by ID ---")
        if not self.contacts:
            print("No contacts to view. Please add some first.")
            return

        # First, display all contacts so the user knows the IDs
        self.view_all_contacts(sorted_by_name=True)  # Display sorted list with IDs

        try:
            idx_input = input("Enter the ID number of the contact to view: ").strip()
            if not idx_input:
                print("No ID entered. Returning to main menu.")
                return

            contact_id = int(idx_input)  # Convert input to integer

            # Validate if the ID is within the valid range of displayed contacts
            if 1 <= contact_id <= len(self.contacts):
                # Since view_all_contacts shows a sorted list, we need to pick from that
                sorted_contacts = sorted(self.contacts, key=lambda c: c["Name"].lower())
                selected_contact = sorted_contacts[
                    contact_id - 1
                ]  # Adjust for 0-based indexing
                print("\n--- Details for Selected Contact ---")
                self._display_single_contact(selected_contact)
            else:
                print(
                    f"Invalid ID '{contact_id}'. Please enter a number within the displayed range (1 to {len(self.contacts)})."
                )
        except ValueError:
            print("Invalid input. Please enter a whole number for the ID.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def search_by_name(self):
        """
        Searches for contacts whose names start with the provided string (case-insensitive).
        Displays all matching contacts, sorted alphabetically.
        """
        print("\n--- Search by Name ---")
        search_name_prefix = input("Enter name prefix to search: ").strip()
        if not search_name_prefix:
            print("Search prefix cannot be empty.")
            return

        # Filter contacts that match the prefix
        found_contacts = [
            contact
            for contact in self.contacts
            if contact["Name"].lower().startswith(search_name_prefix.lower())
        ]

        if not found_contacts:
            print(f"No contacts found starting with '{search_name_prefix}'.")
            return

        print(f"\nContacts found starting with '{search_name_prefix}':")
        # Display found contacts, sorted by name
        for i, contact in enumerate(
            sorted(found_contacts, key=lambda c: c["Name"].lower())
        ):
            self._display_single_contact(contact, i + 1)

    def search_by_group(self):
        """
        Searches for contacts belonging to a specific group (Home or Office, case-insensitive).
        Displays all matching contacts, sorted alphabetically by name.
        """
        print("\n--- Search by Group ---")
        group_input = input(
            f"Enter group to search ({'/'.join(VALID_GROUPS)}): "
        ).strip()
        # Validate group input
        if not self._validate_input("Group", group_input):
            return

        # Filter contacts that belong to the specified group
        found_contacts = [
            contact
            for contact in self.contacts
            if contact["Group"].lower() == group_input.lower()
        ]

        if not found_contacts:
            print(f"No contacts found in the '{group_input}' group.")
            return

        print(f"\nContacts found in '{group_input}' group:")
        # Display found contacts, sorted by name
        for i, contact in enumerate(
            sorted(found_contacts, key=lambda c: c["Name"].lower())
        ):
            self._display_single_contact(contact, i + 1)

    def update_contact(self):
        """
        Allows updating an existing contact's details.
        The user identifies the contact to update by its Name and Contact Number.
        The user can then provide new values, leaving fields blank to keep current values.
        """
        print("\n--- Update Contact ---")
        if not self.contacts:
            print("No contacts to update. Add some first!")
            return

        self.view_all_contacts(sorted_by_name=True)  # Show all contacts for reference

        # Get identifiers for the contact to update
        name_to_find = input("Enter the Name of the contact to update: ").strip()
        contact_num_to_find = input(
            "Enter the Contact Number of the contact to update: "
        ).strip()

        target_index = -1
        # Find the actual index of the contact in the internal (unsorted) list
        for i, contact in enumerate(self.contacts):
            if (
                contact["Name"].lower() == name_to_find.lower()
                and contact["Contact"] == contact_num_to_find
            ):
                target_index = i
                break

        if target_index == -1:
            print(
                f"No contact found with Name '{name_to_find}' and Contact '{contact_num_to_find}'."
            )
            return

        contact_to_update = self.contacts[target_index]
        print("\n--- Current Contact Details ---")
        self._display_single_contact(
            contact_to_update, index=None
        )  # Show current details without ID

        print("Enter new values (leave blank to keep current value):")

        # Prompt for new values, providing current value as a hint
        new_name = input(f"New Name (current: '{contact_to_update['Name']}'): ").strip()
        new_contact_num = input(
            f"New Contact (current: '{contact_to_update['Contact']}'): "
        ).strip()
        new_email = input(
            f"New Email (current: '{contact_to_update['Email']}'): "
        ).strip()
        new_group = input(
            f"New Group (current: '{contact_to_update['Group']}', options: {', '.join(VALID_GROUPS)}): "
        ).strip()

        updated_flag = False  # Flag to track if any field was actually updated

        # Update fields only if new value is provided and valid
        if new_name and self._validate_input("Name", new_name):
            contact_to_update["Name"] = new_name
            updated_flag = True
        if new_contact_num and self._validate_input("Contact", new_contact_num):
            contact_to_update["Contact"] = new_contact_num
            updated_flag = True
        if new_email and self._validate_input("Email", new_email):
            contact_to_update["Email"] = new_email
            updated_flag = True
        if new_group and self._validate_input("Group", new_group):
            contact_to_update["Group"] = new_group
            updated_flag = True

        if updated_flag:
            self._save_contacts()  # Save changes to file
            print("Contact updated successfully!")
        else:
            print("No changes were made or invalid input provided for updates.")

    def delete_contact(self):
        """
        Deletes a contact from the database.
        The user identifies the contact to delete by its Name and Contact Number.
        """
        print("\n--- Delete Contact ---")
        if not self.contacts:
            print("No contacts to delete. Add some first!")
            return

        self.view_all_contacts(sorted_by_name=True)  # Show all contacts for reference

        name_to_delete = input("Enter Name of contact to delete: ").strip()
        contact_to_delete = input("Enter Contact Number of contact to delete: ").strip()

        initial_count = len(
            self.contacts
        )  # Store initial count to check if deletion occurred

        # Create a new list containing only contacts that DO NOT match the deletion criteria.
        # This is a safe way to remove items while iterating.
        self.contacts = [
            contact
            for contact in self.contacts
            if not (
                contact["Name"].lower() == name_to_delete.lower()
                and contact["Contact"] == contact_to_delete
            )
        ]

        if len(self.contacts) == initial_count:
            # If the list length hasn't changed, no matching contact was found
            print(
                f"No contact found with Name '{name_to_delete}' and Contact '{contact_to_delete}'."
            )
        else:
            self._save_contacts()  # Save the modified list to file
            print("Contact(s) deleted successfully!")

    def export_contacts_to_csv(self, filename: str = CSV_EXPORT_FILE):
        """
        Exports all contacts to a CSV (Comma Separated Values) file.
        The CSV file can be opened by spreadsheet programs like Excel.

        Args:
            filename (str): The name of the CSV file to create/overwrite.
        """
        print(f"\n--- Exporting Contacts to CSV ({filename}) ---")
        if not self.contacts:
            print("No contacts to export.")
            return

        try:
            # Open the file in write mode, with newline='' to prevent extra blank rows in CSV
            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Name", "Contact", "Email", "Group"]  # Define CSV header
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()  # Write the first row (headers)
                writer.writerows(
                    self.contacts
                )  # Write all contact dictionaries as rows

            print(f"Contacts successfully exported to '{filename}'!")
        except IOError as e:
            print(f"Error exporting contacts to '{filename}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred during CSV export: {e}")


# --- Main Menu and Program Execution ---


def main_menu():
    """
    Displays the main interactive menu for the Contact Management System.
    Handles user input to call the appropriate ContactManager methods.
    """
    manager = (
        ContactManager()
    )  # Create an instance of the ContactManager, which loads data

    while True:
        print("\n--- Contact Management System Menu ---")
        print("1. Add New Contact")
        print("2. View All Contacts (Sorted by Name)")
        print("3. View Specific Contact by ID")  # New: View by displayed index
        print("4. Search by Name Prefix")
        print("5. Search by Group")
        print("6. Update Existing Contact")  # New: Update contact details
        print("7. Delete Contact")
        print("8. Export Contacts to CSV")  # New: Export data
        print("9. Exit")
        print("--------------------------------------")

        choice = input("Enter your choice (1-9): ").strip()

        # Call the corresponding method based on user's choice
        if choice == "1":
            manager.add_contact()
        elif choice == "2":
            manager.view_all_contacts(sorted_by_name=True)
        elif choice == "3":
            manager.view_specific_contact_by_id()
        elif choice == "4":
            manager.search_by_name()
        elif choice == "5":
            manager.search_by_group()
        elif choice == "6":
            manager.update_contact()
        elif choice == "7":
            manager.delete_contact()
        elif choice == "8":
            manager.export_contacts_to_csv()
        elif choice == "9":
            print("Exiting Contact Management System. Goodbye!")
            break  # Exit the loop and end the program
        else:
            print("Invalid choice. Please enter a number between 1 and 9.")


if __name__ == "__main__":
    main_menu()

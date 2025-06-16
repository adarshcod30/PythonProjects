import os
import hashlib # For password hashing
import datetime # For recording transaction timestamps

# --- Configuration ---
USERS_FILE = 'users.txt'
TRANSACTIONS_FILE = 'transactions.txt'

# Valid categories for employment
VALID_CATEGORIES = ['freelancer', 'full time', 'part time']

# --- Helper Functions ---

def _hash_password(password: str) -> str:
    """Hashes a password using SHA256 for basic security."""
    return hashlib.sha256(password.encode()).hexdigest()

def _display_message(message: str):
    """Prints a message with a separator for better readability."""
    print("-" * 40)
    print(message)
    print("-" * 40)

# --- User Class ---

class User:
    """
    Represents a user of the financial tracking system.
    Stores personal details and hashed password.
    """
    def __init__(self, account_no: str, hashed_password: str, name: str, category: str):
        """
        Initializes a User object.

        Args:
            account_no (str): Unique account number for the user.
            hashed_password (str): SHA256 hashed password.
            name (str): User's full name.
            category (str): Employment category (e.g., 'freelancer').
        """
        self.account_no = account_no
        self.hashed_password = hashed_password
        self.name = name
        self.category = category

    def verify_password(self, password: str) -> bool:
        """Checks if the provided plain-text password matches the stored hashed password."""
        return self.hashed_password == _hash_password(password)

    def to_file_format(self) -> str:
        """Converts user data to a string format for saving to file."""
        return f"{self.account_no}:{self.hashed_password}:{self.name}:{self.category}"

    def __str__(self):
        """String representation for displaying user info."""
        return (f"Account No: {self.account_no}\n"
                f"Name: {self.name}\n"
                f"Category: {self.category}")

# --- Transaction Class ---

class Transaction:
    """
    Represents a single financial transaction (income or expense).
    """
    def __init__(self, account_no: str, timestamp: datetime.datetime,
                 trans_type: str, amount: float, description: str):
        """
        Initializes a Transaction object.

        Args:
            account_no (str): The account number of the user who made the transaction.
            timestamp (datetime.datetime): The exact date and time of the transaction.
            trans_type (str): Type of transaction ('Income' or 'Expense').
            amount (float): The amount of the transaction.
            description (str): A brief description of the transaction.
        """
        self.account_no = account_no
        self.timestamp = timestamp
        self.type = trans_type # 'Income' or 'Expense'
        self.amount = amount
        self.description = description

    def to_file_format(self) -> str:
        """Converts transaction data to a string format for saving to file."""
        # Use ISO format for datetime to ensure accurate parsing later
        return f"{self.account_no},{self.timestamp.isoformat()},{self.type},{self.amount},{self.description}"

    def __str__(self):
        """String representation for displaying transaction details."""
        timestamp_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        sign = '+' if self.type == 'Income' else '-'
        return (f"  [{timestamp_str}] | Type: {self.type} | Amount: {sign}${self.amount:,.2f} | "
                f"Description: {self.description}")

# --- FinancialTracker Class ---

class FinancialTracker:
    """
    Manages all user accounts and financial transactions, including file I/O.
    """
    def __init__(self, users_file: str = USERS_FILE, transactions_file: str = TRANSACTIONS_FILE):
        """
        Initializes the FinancialTracker.
        Loads existing users and transactions from respective files.
        """
        self.users_file = users_file
        self.transactions_file = transactions_file
        self._users: dict[str, User] = {}          # Stores User objects by account number
        self._transactions: list[Transaction] = [] # Stores all Transaction objects

        self._load_users()
        self._load_transactions()

    def _load_users(self):
        """Loads user data from the users file into memory."""
        self._users = {} # Clear existing users before loading
        if not os.path.exists(self.users_file) or os.path.getsize(self.users_file) == 0:
            _display_message(f"No existing user file found or '{self.users_file}' is empty. Starting with no registered users.")
            return

        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line: continue # Skip empty lines

                    parts = line.split(':', 3) # Split into at most 4 parts
                    if len(parts) == 4:
                        account_no, hashed_password, name, category = parts
                        if category not in VALID_CATEGORIES:
                            print(f"Warning: Invalid category '{category}' for user '{account_no}' on line {line_num}. Skipping.")
                            continue
                        self._users[account_no] = User(account_no, hashed_password, name, category)
                    else:
                        print(f"Warning: Malformed user data on line {line_num} in '{self.users_file}': '{line}'. Skipping.")
            _display_message(f"Users loaded successfully from '{self.users_file}'. Total: {len(self._users)}.")
        except IOError as e:
            _display_message(f"Error loading users from '{self.users_file}': {e}")
            self._users = {} # Clear to prevent corrupted state
        except Exception as e:
            _display_message(f"An unexpected error occurred while loading users: {e}")
            self._users = {}

    def _save_users(self):
        """Saves current user data from memory to the users file (overwrites)."""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                for user in self._users.values():
                    f.write(user.to_file_format() + '\n')
            # print(f"Users saved to '{self.users_file}'.") # Uncomment for debugging
        except IOError as e:
            _display_message(f"Error saving users to '{self.users_file}': {e}")
        except Exception as e:
            _display_message(f"An unexpected error occurred while saving users: {e}")

    def _load_transactions(self):
        """Loads transaction data from the transactions file into memory."""
        self._transactions = [] # Clear existing transactions before loading
        if not os.path.exists(self.transactions_file) or os.path.getsize(self.transactions_file) == 0:
            _display_message(f"No existing transactions file found or '{self.transactions_file}' is empty. Starting with no transactions.")
            return

        try:
            with open(self.transactions_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line: continue

                    parts = line.split(',', 4) # Split into at most 5 parts
                    if len(parts) == 5:
                        try:
                            account_no = parts[0]
                            timestamp = datetime.datetime.fromisoformat(parts[1])
                            trans_type = parts[2]
                            amount = float(parts[3])
                            description = parts[4]

                            # Basic validation for loaded transaction
                            if trans_type not in ['Income', 'Expense'] or amount < 0:
                                print(f"Warning: Invalid transaction data on line {line_num} for user '{account_no}'. Skipping.")
                                continue
                            
                            self._transactions.append(Transaction(account_no, timestamp, trans_type, amount, description))
                        except (ValueError, TypeError) as e:
                            print(f"Warning: Malformed transaction data on line {line_num} in '{self.transactions_file}': {e}. Skipping.")
                    else:
                        print(f"Warning: Malformed transaction data on line {line_num} in '{self.transactions_file}': '{line}'. Skipping.")
            _display_message(f"Transactions loaded successfully from '{self.transactions_file}'. Total: {len(self._transactions)}.")
        except IOError as e:
            _display_message(f"Error loading transactions from '{self.transactions_file}': {e}")
            self._transactions = []
        except Exception as e:
            _display_message(f"An unexpected error occurred while loading transactions: {e}")
            self._transactions = []


    def _append_transaction_to_file(self, transaction: Transaction):
        """Appends a single transaction to the transactions file."""
        try:
            with open(self.transactions_file, 'a', encoding='utf-8') as f: # 'a' for append mode
                f.write(transaction.to_file_format() + '\n')
            # print(f"Transaction appended to '{self.transactions_file}'.") # Debugging
        except IOError as e:
            _display_message(f"Error appending transaction to '{self.transactions_file}': {e}")
        except Exception as e:
            _display_message(f"An unexpected error occurred while appending transaction: {e}")


    def signup(self) -> bool:
        """
        Guides the user through the signup process, creating a new account.
        Returns True on successful signup, False otherwise.
        """
        _display_message("--- Create New Account (Sign Up) ---")
        while True:
            account_no = input("Enter a new Account Number (digits only): ").strip()
            if not account_no.isdigit():
                print("Account Number must contain only digits.")
            elif account_no in self._users:
                print(f"Account Number '{account_no}' already exists. Please choose another.")
            else:
                break
        
        password = input("Enter a password: ").strip()
        if not password:
            print("Password cannot be empty.")
            return False

        name = input("Enter your Full Name: ").strip()
        if not name:
            print("Name cannot be empty.")
            return False

        while True:
            category = input(f"Enter your Category ({'/'.join(VALID_CATEGORIES)}): ").strip().lower()
            if category in VALID_CATEGORIES:
                break
            else:
                print(f"Invalid category. Please choose from {', '.join(VALID_CATEGORIES)}.")
        
        hashed_password = _hash_password(password)
        try:
            new_user = User(account_no, hashed_password, name, category)
            self._users[account_no] = new_user
            self._save_users() # Save updated users list to file
            _display_message(f"Account '{account_no}' created successfully! Please login.")
            return True
        except ValueError as e:
            _display_message(f"Signup error: {e}")
            return False
        except Exception as e:
            _display_message(f"An unexpected error occurred during signup: {e}")
            return False

    def login(self) -> User | None:
        """
        Authenticates a user. Returns the User object if successful, None otherwise.
        """
        _display_message("--- Account Login ---")
        account_no = input("Enter your Account Number: ").strip()
        password = input("Enter your Password: ").strip()

        user = self._users.get(account_no)
        if user and user.verify_password(password):
            _display_message(f"Welcome, {user.name}! You are logged in.")
            return user
        else:
            _display_message("Invalid Account Number or Password.")
            return None

    def add_transaction(self, current_user_account_no: str):
        """
        Prompts the user for transaction details and adds it to the system.
        """
        _display_message("--- Add New Transaction ---")
        while True:
            amount_str = input("Enter Amount: ").strip()
            try:
                amount = float(amount_str)
                if amount <= 0:
                    print("Amount must be a positive number.")
                else:
                    break
            except ValueError:
                print("Invalid amount. Please enter a number (e.g., 100.50).")

        while True:
            trans_type = input("Enter Type (Income/Expense): ").strip().capitalize()
            if trans_type in ['Income', 'Expense']:
                break
            else:
                print("Invalid type. Please enter 'Income' or 'Expense'.")
        
        description = input("Enter Description (e.g., Salary, Groceries): ").strip()
        if not description:
            print("Description cannot be empty.")
            # Optionally, return or ask again if description is mandatory
            description = "N/A" # Default if left empty for simplicity

        timestamp = datetime.datetime.now() # Auto-capture current time

        try:
            new_transaction = Transaction(current_user_account_no, timestamp, trans_type, amount, description)
            self._transactions.append(new_transaction)
            self._append_transaction_to_file(new_transaction) # Append to file immediately
            _display_message("Transaction added successfully!")
            print(new_transaction) # Show the added transaction
        except ValueError as e:
            _display_message(f"Error adding transaction: {e}")
        except Exception as e:
            _display_message(f"An unexpected error occurred while adding transaction: {e}")


    def view_financial_report(self, current_user_account_no: str):
        """
        Generates and displays a financial report for the current user,
        including total income, total expenses, balance, and all transactions.
        """
        _display_message(f"--- Financial Report for Account: {current_user_account_no} ---")
        
        user_transactions = [
            t for t in self._transactions if t.account_no == current_user_account_no
        ]

        if not user_transactions:
            print("No transactions recorded for this account yet.")
            print("Current Balance: $0.00")
            return

        total_income = sum(t.amount for t in user_transactions if t.type == 'Income')
        total_expense = sum(t.amount for t in user_transactions if t.type == 'Expense')
        current_balance = total_income - total_expense

        print(f"Total Income:    +${total_income:,.2f}")
        print(f"Total Expenses:  -${total_expense:,.2f}")
        print(f"Current Balance:  ${current_balance:,.2f}")
        print("\n--- Transaction History ---")
        
        # Sort transactions by timestamp for chronological display
        sorted_transactions = sorted(user_transactions, key=lambda t: t.timestamp)

        for i, transaction in enumerate(sorted_transactions):
            print(f"Transaction {i+1}:")
            print(transaction)
        
        _display_message("Report End.")


# --- Main Application Loop ---

def run_app():
    """
    Main function to run the Personal Finance Tracker application.
    Handles the main menu logic and user interaction.
    """
    tracker = FinancialTracker() # Initialize the tracker, which loads existing data
    current_user: User | None = None # Stores the currently logged-in user

    while True:
        if current_user is None: # Not logged in
            print("\n--- Main Menu ---")
            print("1. Login")
            print("2. Sign Up (Create New Account)")
            print("3. Exit")
            choice = input("Enter your choice: ").strip()

            if choice == '1':
                current_user = tracker.login()
            elif choice == '2':
                tracker.signup()
            elif choice == '3':
                _display_message("Exiting Personal Finance Tracker. Goodbye!")
                break # Exit the main loop
            else:
                _display_message("Invalid choice. Please enter 1, 2, or 3.")
        else: # Logged in
            print(f"\n--- Logged in as: {current_user.name} ({current_user.account_no}) ---")
            print("1. Add New Transaction")
            print("2. View Financial Report")
            print("3. View My Personal Details")
            print("4. Logout")
            choice = input("Enter your choice: ").strip()

            if choice == '1':
                tracker.add_transaction(current_user.account_no)
            elif choice == '2':
                tracker.view_financial_report(current_user.account_no)
            elif choice == '3':
                _display_message("--- Your Personal Details ---")
                print(current_user)
            elif choice == '4':
                _display_message(f"Logging out {current_user.name}...")
                current_user = None # Clear current user to return to login menu
            else:
                _display_message("Invalid choice. Please enter 1, 2, 3, or 4.")

# --- Run the application ---
if __name__ == "__main__":
    run_app()

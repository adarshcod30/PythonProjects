
"""
Basic Social Media Platform

This program simulates a simple social media platform with user signup,
login, and posting functionalities. It uses classes for organization
and file handling for data persistence. Passwords are hashed for basic security.
"""

import os
import hashlib # For password hashing

# --- Configuration ---
USERS_FILE = 'users.txt'
POSTS_FILE = 'posts.txt'
# Format for users.txt: username:hashed_password
# Format for posts.txt: username:post_content

# --- Cell 1: User Class ---

class User:
    """
    Represents a social media platform user.
    """
    def __init__(self, username: str, hashed_password: str):
        """
        Initializes a User object.

        Args:
            username (str): The user's unique username.
            hashed_password (str): The SHA256 hashed password for the user.
        """
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Username cannot be empty.")
        if not isinstance(hashed_password, str) or not hashed_password.strip():
            raise ValueError("Hashed password cannot be empty.")

        self.username = username.strip()
        self.hashed_password = hashed_password.strip()

    def verify_password(self, password: str) -> bool:
        """
        Verifies if the given plain-text password matches the stored hashed password.

        Args:
            password (str): The plain-text password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return self.hashed_password == hashlib.sha256(password.encode()).hexdigest()

    def __str__(self):
        """Returns a string representation of the User."""
        return f"User(username='{self.username}')"

# --- Cell 2: Post Class ---

class Post:
    """
    Represents a single post made by a user.
    """
    def __init__(self, username: str, content: str):
        """
        Initializes a Post object.

        Args:
            username (str): The username of the author of the post.
            content (str): The content of the post.
        """
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Post author username cannot be empty.")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Post content cannot be empty.")

        self.username = username.strip()
        self.content = content.strip()

    def to_file_format(self) -> str:
        """
        Converts the post object into a string format suitable for saving to file.
        """
        # Using a simple delimiter for simplicity. For complex content,
        # one might need more robust serialization (e.g., JSON).
        return f"{self.username}:{self.content}"

    def __str__(self):
        """Returns a string representation of the Post."""
        return f"@{self.username}: {self.content}"

# --- Cell 3: SocialMediaPlatform Class ---

class SocialMediaPlatform:
    """
    Manages user accounts (signup, login) and posts.
    Handles loading and saving data to files.
    """
    def __init__(self, users_file: str = USERS_FILE, posts_file: str = POSTS_FILE):
        """
        Initializes the SocialMediaPlatform. Loads existing users and posts.

        Args:
            users_file (str): The file path for storing user credentials.
            posts_file (str): The file path for storing posts.
        """
        self.users_file = users_file
        self.posts_file = posts_file
        self._users: dict[str, User] = {} # Stores User objects by username
        self._posts: list[Post] = []     # Stores Post objects

        self._load_users()
        self._load_posts()

    def _load_users(self):
        """
        Loads user data from the users file into memory.
        """
        if not os.path.exists(self.users_file) or os.path.getsize(self.users_file) == 0:
            print(f"No existing user file found or '{self.users_file}' is empty. Starting with no registered users.")
            return

        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(':', 1) # Split only on the first colon
                    if len(parts) == 2:
                        username, hashed_password = parts[0], parts[1]
                        try:
                            self._users[username] = User(username, hashed_password)
                        except ValueError as e:
                            print(f"Warning: Malformed user data on line {line_num} in '{self.users_file}': {e} - skipping line.")
                    else:
                        print(f"Warning: Skipping malformed line {line_num} in '{self.users_file}': '{line}' - Expected 'username:hashed_password'.")
            print(f"Users loaded successfully from '{self.users_file}'.")
        except IOError as e:
            print(f"Error loading users from '{self.users_file}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while loading users: {e}")
            self._users = {} # Clear users if unexpected error to prevent corrupted data

    def _save_users(self):
        """
        Saves current user data from memory to the users file.
        """
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                for user in self._users.values():
                    f.write(f"{user.username}:{user.hashed_password}\n")
            # print(f"Users saved to '{self.users_file}'.")
        except IOError as e:
            print(f"Error saving users to '{self.users_file}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving users: {e}")

    def _load_posts(self):
        """
        Loads post data from the posts file into memory.
        """
        if not os.path.exists(self.posts_file) or os.path.getsize(self.posts_file) == 0:
            print(f"No existing posts file found or '{self.posts_file}' is empty. Starting with no posts.")
            return

        try:
            with open(self.posts_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(':', 1) # Split on first colon
                    if len(parts) == 2:
                        username, content = parts[0], parts[1]
                        try:
                            self._posts.append(Post(username, content))
                        except ValueError as e:
                            print(f"Warning: Malformed post data on line {line_num} in '{self.posts_file}': {e} - skipping line.")
                    else:
                        print(f"Warning: Skipping malformed line {line_num} in '{self.posts_file}': '{line}' - Expected 'username:content'.")
            print(f"Posts loaded successfully from '{self.posts_file}'.")
        except IOError as e:
            print(f"Error loading posts from '{self.posts_file}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while loading posts: {e}")
            self._posts = [] # Clear posts if unexpected error

    def _save_posts(self):
        """
        Saves current post data from memory to the posts file.
        """
        try:
            with open(self.posts_file, 'w', encoding='utf-8') as f:
                for post in self._posts:
                    f.write(post.to_file_format() + '\n')
            # print(f"Posts saved to '{self.posts_file}'.")
        except IOError as e:
            print(f"Error saving posts to '{self.posts_file}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving posts: {e}")

    def signup(self, username: str, password: str) -> bool:
        """
        Registers a new user.

        Args:
            username (str): The desired username.
            password (str): The desired password (will be hashed).

        Returns:
            bool: True if signup is successful, False otherwise (e.g., username taken).
        """
        if not username.strip() or not password.strip():
            print("Username and password cannot be empty.")
            return False

        if username.strip() in self._users:
            print(f"Error: Username '{username}' already taken. Please choose another.")
            return False

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            new_user = User(username.strip(), hashed_password)
            self._users[new_user.username] = new_user
            self._save_users()
            print(f"User '{new_user.username}' signed up successfully!")
            return True
        except ValueError as e:
            print(f"Signup error: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during signup: {e}")
            return False

    def login(self, username: str, password: str) -> User | None:
        """
        Logs in a user by verifying credentials.

        Args:
            username (str): The username to log in with.
            password (str): The plain-text password.

        Returns:
            User | None: The User object if login is successful, None otherwise.
        """
        if not username.strip() or not password.strip():
            print("Username and password cannot be empty.")
            return None

        user = self._users.get(username.strip())
        if user and user.verify_password(password):
            print(f"Welcome, {user.username}! You are logged in.")
            return user
        else:
            print("Invalid username or password.")
            return None

    def create_post(self, author_username: str, content: str):
        """
        Creates a new post for a given user.

        Args:
            author_username (str): The username of the post author.
            content (str): The content of the post.
        """
        if not content.strip():
            print("Post content cannot be empty.")
            return

        try:
            new_post = Post(author_username, content)
            self._posts.append(new_post)
            self._save_posts()
            print("Post created successfully!")
        except ValueError as e:
            print(f"Error creating post: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while creating post: {e}")

    def get_user_posts(self, username: str) -> list[Post]:
        """
        Retrieves all posts made by a specific user.

        Args:
            username (str): The username of the author.

        Returns:
            list[Post]: A list of Post objects by the specified user.
        """
        return [post for post in self._posts if post.username == username]

    def get_all_posts(self) -> list[Post]:
        """
        Retrieves all posts from all users.
        """
        return list(self._posts) # Return a copy

# --- Cell 4: Main Application Logic ---

def display_main_menu():
    """Displays the main menu options."""
    print("\n--- Welcome to the Social Media Platform ---")
    print("1. Login")
    print("2. Sign Up")
    print("3. Exit")
    print("--------------------------------------------")

def display_logged_in_menu(username: str):
    """Displays the menu for a logged-in user."""
    print(f"\n--- Logged in as: {username} ---")
    print("1. Create a new post")
    print("2. View my posts")
    print("3. View all platform posts") # Added this for a more complete experience
    print("4. Logout")
    print("----------------------------------")

def main():
    """
    The main function to run the social media application.
    """
    platform = SocialMediaPlatform()
    current_user: User | None = None

    while True:
        if current_user is None:
            display_main_menu()
            choice = input("Enter your choice: ").strip()

            if choice == '1': # Login
                username = input("Enter username: ").strip()
                password = input("Enter password: ").strip()
                current_user = platform.login(username, password)
            elif choice == '2': # Sign Up
                username = input("Enter new username: ").strip()
                password = input("Enter new password: ").strip()
                if platform.signup(username, password):
                    pass # User signed up, optionally prompt to login now
            elif choice == '3': # Exit
                print("Thank you for using the platform. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        else: # User is logged in
            display_logged_in_menu(current_user.username)
            choice = input("Enter your choice: ").strip()

            if choice == '1': # Create Post
                content = input("Enter your post content: ").strip()
                platform.create_post(current_user.username, content)
            elif choice == '2': # View My Posts
                my_posts = platform.get_user_posts(current_user.username)
                if my_posts:
                    print(f"\n--- Posts by {current_user.username} ---")
                    for i, post in enumerate(my_posts, 1):
                        print(f"{i}. {post}")
                else:
                    print("You haven't made any posts yet.")
            elif choice == '3': # View All Platform Posts
                all_posts = platform.get_all_posts()
                if all_posts:
                    print("\n--- All Posts on the Platform ---")
                    # Sort posts by username for easier viewing, or by a timestamp if we added one
                    for i, post in enumerate(sorted(all_posts, key=lambda p: p.username), 1):
                        print(f"{i}. {post}")
                else:
                    print("No posts have been made on the platform yet.")
            elif choice == '4': # Logout
                print(f"Logging out {current_user.username}...")
                current_user = None
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()

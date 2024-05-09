import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class User:
    def __init__(self, username, password, user_type):
        self.username = username
        self.password = password
        self.user_type = user_type

class Participant(User):
    def __init__(self, username, password, age, height, weight):
        super().__init__(username, password, "participant")
        self.age = age
        self.height = height
        self.weight = weight

class Manager(User):
    def __init__(self, username, password, position):
        super().__init__(username, password, "manager")
        self.position = position

class Database:
    def __init__(self):
        self.connection = sqlite3.connect("user_credentials.db")
        self.cursor = self.connection.cursor()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                user_type TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                age INTEGER,
                height REAL,
                weight REAL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS managers (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                position TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        self.connection.commit()

    def insert_user(self, user):
        self.cursor.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)",
                            (user.username, user.password, user.user_type))

        if isinstance(user, Participant):
            self.cursor.execute("INSERT INTO participants (user_id, age, height, weight) VALUES ((SELECT id FROM users WHERE username = ?), ?, ?, ?)",
                                (user.username, user.age, user.height, user.weight))
        elif isinstance(user, Manager):
            self.cursor.execute("INSERT INTO managers (user_id, position) VALUES ((SELECT id FROM users WHERE username = ?), ?)",
                                (user.username, user.position))

        self.connection.commit()

    def update_user(self, user):
        self.cursor.execute("UPDATE users SET password=?, user_type=? WHERE username=?",
                            (user.password, user.user_type, user.username))

        if isinstance(user, Participant):
            self.cursor.execute("UPDATE participants SET age=?, height=?, weight=? WHERE user_id=(SELECT id FROM users WHERE username = ?)",
                                (user.age, user.height, user.weight, user.username))
        elif isinstance(user, Manager):
            self.cursor.execute("UPDATE managers SET position=? WHERE user_id=(SELECT id FROM users WHERE username = ?)",
                                (user.position, user.username))

        self.connection.commit()

    def delete_user(self, username):
        self.cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        self.connection.commit()

class AddUserWindow:
    def __init__(self, parent):
        self.parent = parent
        self.add_user_window = tk.Toplevel(parent)
        self.add_user_window.title("Add User")

        ttk.Label(self.add_user_window, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.add_user_window, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(self.add_user_window, text="User Type:").grid(row=2, column=0, padx=5, pady=5)

        self.username_entry = ttk.Entry(self.add_user_window)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        self.password_entry = ttk.Entry(self.add_user_window, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        self.user_type_entry = ttk.Combobox(self.add_user_window, values=["participant", "manager"])
        self.user_type_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(self.add_user_window, text="Add User", command=self.add_user).grid(row=3, columnspan=2, pady=5)

    def add_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_type = self.user_type_entry.get()

        user = None
        if user_type == "participant":
            user = Participant(username, password, 0, 0, 0)  # Default values for age, height, and weight
        elif user_type == "manager":
            user = Manager(username, password, "Position")

        if user:
            db = Database()
            db.insert_user(user)
            messagebox.showinfo("Success", "User added successfully")
            self.add_user_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid user type")

class ModifyUserWindow:
    def __init__(self, parent):
        self.parent = parent
        self.modify_user_window = tk.Toplevel(parent)
        self.modify_user_window.title("Modify User")

        self.tree = ttk.Treeview(self.modify_user_window, columns=("Username", "User Type"), show="headings")
        self.tree.heading("Username", text="Username")
        self.tree.heading("User Type", text="User Type")

        self.populate_treeview()

        self.tree.pack(expand=True, fill="both")

        ttk.Button(self.modify_user_window, text="Modify User", command=self.modify_user).pack(pady=10)

    def populate_treeview(self):
        db = Database()
        users = db.cursor.execute("SELECT username, user_type FROM users").fetchall()
        for user in users:
            self.tree.insert("", "end", values=user)

    def modify_user(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a user")
            return

        item_values = self.tree.item(selected_item, "values")
        username = item_values[0]

        password = messagebox.askstring("Password", f"Enter new password for {username}:")
        user_type = messagebox.askstring("User Type", f"Enter new user type for {username} (participant/manager):")

        if not password or not user_type:
            messagebox.showerror("Error", "Password or user type cannot be empty")
            return

        db = Database()
        user = User(username, password, user_type)
        db.update_user(user)
        messagebox.showinfo("Success", "User information updated successfully")

class DeleteUserWindow:
    def __init__(self, parent):
        self.parent = parent
        self.delete_user_window = tk.Toplevel(parent)
        self.delete_user_window.title("Delete User")

        ttk.Label(self.delete_user_window, text="Username:").grid(row=0, column=0, padx=5, pady=5)

        self.username_entry = ttk.Entry(self.delete_user_window)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(self.delete_user_window, text="Delete User", command=self.delete_user).grid(row=1, columnspan=2, pady=5)

    def delete_user(self):
        username = self.username_entry.get()

        db = Database()
        db.delete_user(username)
        messagebox.showinfo("Success", "User deleted successfully")
        self.delete_user_window.destroy()

class ManagerInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Manager Interface")
        self.root_width = 600
        self.root_height = 400

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - self.root_width) // 2
        y = (screen_height - self.root_height) // 2

        self.root.geometry(f"{self.root_width}x{self.root_height}+{x}+{y}")

        self.create_widgets()

    def create_widgets(self):
        ttk.Button(self.root, text="Add User", command=self.open_add_user_window).pack(pady=5)
        ttk.Button(self.root, text="Modify User", command=self.open_modify_user_window).pack(pady=5)
        ttk.Button(self.root, text="Delete User", command=self.open_delete_user_window).pack(pady=5)

    def open_add_user_window(self):
        AddUserWindow(self.root)

    def open_modify_user_window(self):
        ModifyUserWindow(self.root)

    def open_delete_user_window(self):
        DeleteUserWindow(self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = ManagerInterface(root)
    root.mainloop()

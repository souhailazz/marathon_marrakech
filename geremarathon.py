import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class User:
    def __init__(self, username, password, user_type):
        self.__username = username
        self.__password = password
        self.__user_type = user_type

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    def get_user_type(self):
        return self.__user_type

class Participant(User):
    def __init__(self, username, password, age, height, weight, nationality, marathon_type):
        super().__init__(username, password, "participant")
        self.__age = age
        self.__height = height
        self.__weight = weight
        self.__nationality = nationality
        self.__marathon_type = marathon_type

    def get_age(self):
        return self.__age

    def get_height(self):
        return self.__height

    def get_weight(self):
        return self.__weight

    def get_nationality(self):
        return self.__nationality

    def get_marathon_type(self):
        return self.__marathon_type

class Manager(User):
    def __init__(self, username, password, position, email):
        super().__init__(username, password, "manager")
        self.__position = position
        self.__email = email

    def get_position(self):
        return self.__position

    def get_email(self):
        return self.__email

class Database:
    def __init__(self, db_name):
        self.db_name = db_name

    def create_tables(self):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                user_type TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                age INTEGER,
                height REAL,
                weight REAL,
                nationality TEXT,
                marathon_type TEXT,

                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS managers (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                position TEXT,
                email TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        connection.commit()
        connection.close()

    def insert_sample_data(self):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)", ("participant", "password", "participant"))
            cursor.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)", ("manager", "password", "manager"))

            connection.commit()

        connection.close()

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")

        self.root_width = 400
        self.root_height = 200

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - self.root_width) // 2
        y = (screen_height - self.root_height) // 2

        self.root.geometry(f"{self.root_width}x{self.root_height}+{x}+{y}")

        self.username_label = ttk.Label(root, text="Username:")
        self.username_label.grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.username_entry = ttk.Entry(root)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = ttk.Label(root, text="Password:")
        self.password_label.grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.password_entry = ttk.Entry(root, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = ttk.Button(root, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.signup_button = ttk.Button(root, text="Sign Up", command=self.show_signup)
        self.signup_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.db = Database("user_credentials.db")
        self.db.create_tables()
        self.db.insert_sample_data()




    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        connection = sqlite3.connect("user_credentials.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        if user:

            user_type = user[3]
            nationality = self.get_nationality(username)  # Get nationality
            self.root.destroy()
            if user_type == "participant":
                participant_interface(nationality, username)  # Pass username to participant interface
            elif user_type == "manager":
                manager_interface()
        else:
            messagebox.showerror("Error", "Invalid username or password")

        connection.close()

    def get_nationality(self, username):
     connection = sqlite3.connect("user_credentials.db")
     cursor = connection.cursor()
     cursor.execute("SELECT user_type FROM users WHERE username = ?", (username,))
     user_type = cursor.fetchone()[0]  # Fixed the variable name
    
     if user_type == "participant":
        cursor.execute("SELECT nationality FROM participants WHERE user_id = (SELECT id FROM users WHERE username = ?)", (username,))
        result = cursor.fetchone()
        if result:
            nationality = result[0]
            return nationality
        else:
            messagebox.showerror("Error", "User not found in participants")
            return None
     else:
        return None



        

    def show_signup(self):
        self.root.withdraw()  # Hide login window
        signup_window = tk.Tk()
        signup_window.title("Sign Up")

        signup_window_width = 400
        signup_window_height = 300

        screen_width = signup_window.winfo_screenwidth()
        screen_height = signup_window.winfo_screenheight()

        x = (screen_width - signup_window_width) // 2
        y = (screen_height - signup_window_height) // 2

        signup_window.geometry(f"{signup_window_width}x{signup_window_height}+{x}+{y}")

        def on_close():
            self.root.deiconify()  # Show login window again
            signup_window.destroy()

        signup_window.protocol("WM_DELETE_WINDOW", on_close)

        def on_user_type_select(event):
            selected_type = self.user_type_entry.get()
            if selected_type == "participant":
                self.show_participant_fields()
            elif selected_type == "manager":
                self.show_manager_fields()

        ttk.Label(signup_window, text="Username:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        ttk.Label(signup_window, text="Password:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        ttk.Label(signup_window, text="User Type:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)

        self.username_entry_signup = ttk.Entry(signup_window)
        self.username_entry_signup.grid(row=0, column=1, padx=5, pady=5)
        self.password_entry_signup = ttk.Entry(signup_window, show="*")
        self.password_entry_signup.grid(row=1, column=1, padx=5, pady=5)
        self.user_type_entry = ttk.Combobox(signup_window, values=["participant", "manager"], state="readonly")
        self.user_type_entry.grid(row=2, column=1, padx=5, pady=5)
        self.user_type_entry.bind("<<ComboboxSelected>>", on_user_type_select)

        self.age_label = ttk.Label(signup_window, text="Age:")
        self.age_entry = ttk.Entry(signup_window)
        self.weight_label = ttk.Label(signup_window, text="Weight:")
        self.weight_entry = ttk.Entry(signup_window)
        self.height_label = ttk.Label(signup_window, text="Height:")
        self.height_entry = ttk.Entry(signup_window)
        self.nationality_label = ttk.Label(signup_window, text="Nationality:")
        self.nationality_entry = ttk.Entry(signup_window)
        self.post_label = ttk.Label(signup_window, text="Post:")
        self.post_entry = ttk.Entry(signup_window)

        signup_button = ttk.Button(signup_window, text="Add User", command=self.add_user)
        signup_button.grid(row=7, column=0, columnspan=2, pady=5)

        signup_window.mainloop()

    def show_participant_fields(self):
        self.age_label.grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)
        self.age_entry.grid(row=3, column=1, padx=5, pady=5)
        self.weight_label.grid(row=4, column=0, sticky=tk.E, padx=5, pady=5)
        self.weight_entry.grid(row=4, column=1, padx=5, pady=5)
        self.height_label.grid(row=5, column=0, sticky=tk.E, padx=5, pady=5)
        self.height_entry.grid(row=5, column=1, padx=5, pady=5)
        self.nationality_label.grid(row=6, column=0, sticky=tk.E, padx=5, pady=5)
        self.nationality_entry.grid(row=6, column=1, padx=5, pady=5)
        self.post_label.grid_forget()
        self.post_entry.grid_forget()

    def show_manager_fields(self):
        self.age_label.grid_forget()
        self.age_entry.grid_forget()
        self.weight_label.grid_forget()
        self.weight_entry.grid_forget()
        self.height_label.grid_forget()
        self.height_entry.grid_forget()
        self.post_label.grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)
        self.post_entry.grid(row=3, column=1, padx=5, pady=5)

    def add_user(self):
        username = self.username_entry_signup.get()
        password = self.password_entry_signup.get()
        user_type = self.user_type_entry.get()

        connection = sqlite3.connect("user_credentials.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        connection.close()

        if existing_user:
            messagebox.showerror("Error", "Username already exists")
            return

        connection = sqlite3.connect("user_credentials.db")
        cursor = connection.cursor()

        cursor.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)", (username, password, user_type))
        if user_type == "participant":
            cursor.execute("INSERT INTO participants (user_id, age, height, weight, nationality) VALUES ((SELECT id FROM users WHERE username = ?), ?, ?, ?,?)",
                           (username, self.age_entry.get(), self.height_entry.get(), self.weight_entry.get(),self.nationality_entry.get()))
        elif user_type == "manager":
            cursor.execute("INSERT INTO managers (user_id, position, email) VALUES ((SELECT id FROM users WHERE username = ?), ?, ?)",
                           (username, self.post_entry.get(), ""))
        connection.commit()

        connection.close()
        messagebox.showinfo("Success", "User added successfully")
        self.root.deiconify()  


def participant_interface(nationality, username):
    def select_marathon(marathon):
        marathon_type = marathon.split(" ")[0]  

        connection = sqlite3.connect("user_credentials.db")
        cursor = connection.cursor()
        cursor.execute("SELECT marathon_type FROM participants WHERE user_id = (SELECT id FROM users WHERE username = ?)", (username,))
        previous_marathon_type = cursor.fetchone()
        
        if previous_marathon_type and previous_marathon_type[0]:
            messagebox.showerror("Error", "You have already chosen a marathon type")
            connection.close()
            return

        cursor.execute("UPDATE participants SET marathon_type = ? WHERE user_id = (SELECT id FROM users WHERE username = ?)", (marathon_type, username))
        connection.commit()
        connection.close()

        messagebox.showinfo("Success", f"You have chosen {marathon}")
        participant_window.destroy()

    participant_window = tk.Tk()
    participant_window.title("Participant Interface")
    participant_window_width = 600
    participant_window_height = 400

    screen_width = participant_window.winfo_screenwidth()
    screen_height = participant_window.winfo_screenheight()

    x = (screen_width - participant_window_width) // 2
    y = (screen_height - participant_window_height) // 2

    participant_window.geometry(f"{participant_window_width}x{participant_window_height}+{x}+{y}")

    ttk.Label(participant_window, text="Choose Marathon Type:").pack(pady=10)

    if nationality == "moroccan":
        marathon_options = ["Half Marathon (150 DHS)", "Full Marathon (350 DHS)"]
    else:
        marathon_options = ["Half Marathon (200 DHS)", "Full Marathon (500 DHS)"]

    for option in marathon_options:
        ttk.Button(participant_window, text=option, command=lambda opt=option: select_marathon(opt)).pack(pady=5)

    participant_window.mainloop()
def center_window(window, width, height):
         screen_width = window.winfo_screenwidth()
         screen_height = window.winfo_screenheight()
         x = (screen_width - width) // 2
         y = (screen_height - height) // 2
         window.geometry(f"{width}x{height}+{x}+{y}")

def manager_interface():
    def show_all_window():
        # Create a new window to display all participants
        show_all_window = tk.Toplevel()
        show_all_window.title("All Participants")

        # Create a Treeview widget to display participant data
        tree = ttk.Treeview(show_all_window, columns=("Username", "Age", "Height", "Weight", "Nationality", "Marathon Type"), show="headings")
        tree.heading("Username", text="Username")
        tree.heading("Age", text="Age")
        tree.heading("Height", text="Height")
        tree.heading("Weight", text="Weight")
        tree.heading("Nationality", text="Nationality")
        tree.heading("Marathon Type", text="Marathon Type")

        # Populate the Treeview with participant data from the database
        connection = sqlite3.connect("user_credentials.db")
        cursor = connection.cursor()
        cursor.execute("SELECT u.username, p.age, p.height, p.weight, p.nationality, p.marathon_type FROM users u INNER JOIN participants p ON u.id = p.user_id")
        participants = cursor.fetchall()
        for participant in participants:
            tree.insert("", "end", values=participant)
        connection.close()

        tree.pack(expand=True, fill="both")
    def add_user_window():
        add_user_window = tk.Toplevel(manager_window)
        add_user_window.title("Add User")

        ttk.Label(add_user_window, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(add_user_window, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(add_user_window, text="User Type:").grid(row=2, column=0, padx=5, pady=5)

        username_entry = ttk.Entry(add_user_window)
        username_entry.grid(row=0, column=1, padx=5, pady=5)
        password_entry = ttk.Entry(add_user_window, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)
        user_type_entry = ttk.Combobox(add_user_window, values=["participant", "manager"])
        user_type_entry.grid(row=2, column=1, padx=5, pady=5)

        def add_user():
            username = username_entry.get()
            password = password_entry.get()
            user_type = user_type_entry.get()

            connection = sqlite3.connect("user_credentials.db")
            cursor = connection.cursor()

            cursor.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)", (username, password, user_type))
            connection.commit()

            connection.close()
            messagebox.showinfo("Success", "User added successfully")
            add_user_window.destroy()

        ttk.Button(add_user_window, text="Add User", command=add_user).grid(row=3, columnspan=2, pady=5)

    def modify_user_window():
        modify_window = tk.Toplevel()
        modify_window.title("Modify Participant")

        tree = ttk.Treeview(modify_window, columns=("Username", "Age", "Height", "Weight","nationality","marathon_type"), show="headings")
        tree.heading("Username", text="Username")
        tree.heading("Age", text="Age")
        tree.heading("Height", text="Height")
        tree.heading("Weight", text="Weight")

        connection = sqlite3.connect("user_credentials.db")
        cursor = connection.cursor()
        cursor.execute("SELECT u.username, p.age, p.height, p.weight,p.nationality,p.marathon_type FROM users u INNER JOIN participants p ON u.id = p.user_id")
        participants = cursor.fetchall()
        for participant in participants:
            tree.insert("", "end", values=participant)
        connection.close()

        tree.pack(expand=True, fill="both")

        def update_participant():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Please select a participant")
                return

            item_values = tree.item(selected_item, "values")
            username = item_values[0]

            updated_age = age_entry.get()
            updated_height = height_entry.get()
            updated_weight = weight_entry.get()
            updated_nationality=nationality_entry.get()
            updated_marathontype=marathontype_entry.get()



            connection = sqlite3.connect("user_credentials.db")
            cursor = connection.cursor()
            cursor.execute("UPDATE participants SET age=?, height=?, weight=? , nationality=? , marathon_type=? WHERE user_id=(SELECT id FROM users WHERE username=?)",
                           (updated_age, updated_height, updated_weight, updated_nationality,updated_marathontype, username  ))
            connection.commit()
            connection.close()

            messagebox.showinfo("Success", "Participant information updated successfully")
            modify_window.destroy() 



        ttk.Label(modify_window, text="New Age:").pack(pady=5)
        age_entry = ttk.Entry(modify_window)
        age_entry.pack(pady=5)

        ttk.Label(modify_window, text="New Height:").pack(pady=5)
        height_entry = ttk.Entry(modify_window)
        height_entry.pack(pady=5)

        ttk.Label(modify_window, text="New Weight:").pack(pady=5)
        weight_entry = ttk.Entry(modify_window)
        weight_entry.pack(pady=5) 

        ttk.Label(modify_window, text="New nationality:").pack(pady=5)
        nationality_entry = ttk.Entry(modify_window)
        nationality_entry.pack(pady=5)

        ttk.Label(modify_window, text="New marathon type:").pack(pady=5)
        marathontype_entry = ttk.Entry(modify_window)
        marathontype_entry.pack(pady=5)

        ttk.Button(modify_window, text="Update Participant", command=update_participant).pack(pady=10)

        modify_window.mainloop()

    def delete_user_window():
        delete_window = tk.Toplevel(manager_window)
        delete_window.title("Delete User")

        ttk.Label(delete_window, text="Enter Username:").pack(pady=5)
        username_entry = ttk.Entry(delete_window)
        username_entry.pack(pady=5)

        def delete_user():
            username = username_entry.get()

            connection = sqlite3.connect("user_credentials.db")
            cursor = connection.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            connection.commit()
            connection.close()

            messagebox.showinfo("Success", "User deleted successfully")
            delete_window.destroy()

        ttk.Button(delete_window, text="Delete User", command=delete_user).pack(pady=5)

   

    manager_window = tk.Tk()
    manager_window.title("Manager Interface")

    # Center the manager window
    manager_width = 600
    manager_height = 600
    center_window(manager_window, manager_width, manager_height)

    # Add buttons to the manager window
    ttk.Button(manager_window, text="Add User", command=add_user_window).pack(pady=10)
    ttk.Button(manager_window, text="Modify Participant", command=modify_user_window).pack(pady=10)
    ttk.Button(manager_window, text="Delete User", command=delete_user_window).pack(pady=10) 
    ttk.Button(manager_window, text="Show All Participants", command=show_all_window).pack(pady=10)

    manager_window.mainloop()


root = tk.Tk()
app = LoginApp(root)
root.mainloop()

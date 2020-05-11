# ****** Account Storage ******

# *******************************

# ****** Importing Modules ******
import hashlib
import os
import sqlite3
from contextlib import contextmanager
from tkinter import *
from tkinter import messagebox

# ****** Welcome Window ******
root = Tk()
root.geometry('300x130')
root.title('Welcome')
root.resizable(width=False, height=False)

heading = Label(root, text='Account Storage', font=('Courier', 24, 'bold'), justify=CENTER)
heading.pack(pady=(10, 0))

login_btn = Button(root, text='Login', command=lambda: login(root), font=('Courier', 16))
signup_btn = Button(root, text='Sign Up', command=lambda: signup(root), font=('Courier', 16))

login_btn.pack(pady=(15, 5), ipadx=17)
signup_btn.pack(pady=5, ipadx=7)


# ****** Database Class ******
class Database:

    def __init__(self):
        pass

    # *** Creating context manager to manage database connection ***
    @staticmethod
    @contextmanager
    def open_database():
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        yield cur
        conn.commit()
        conn.close()

    # *** Creating table to store all user's and their hash passwords ***
    def create_users_table(self):
        with self.open_database() as cur:
            try:
                cur.execute("CREATE TABLE users(username text PRIMARY KEY, salt bytes, key bytes)")
                return "Successfully created table"
            except sqlite3.OperationalError:
                return "Table already exits"

    # *** Checking if user already exits or not ***
    def check_user_exits_or_not(self, username):
        with self.open_database() as cur:
            cur.execute("SELECT * FROM users WHERE username=:username", {'username': username})
            if cur.fetchone():
                return True
            return False

    # *** Sign Up ***
    def add_user_to_db(self, username, salt, key):
        with self.open_database() as cur:
            cur.execute("INSERT INTO users VALUES(:username, :salt, :key)", {'username': username, 'salt': salt, 'key': key})

    # *** Login ***
    def validate_user(self, username, password):
        if not self.check_user_exits_or_not(username):
            return "User does not exits"
        with self.open_database() as cur:
            cur.execute("SELECT * FROM users WHERE username=:username", {'username': username})
            user_data = cur.fetchall()
            salt = user_data[0][1]
            key = user_data[0][2]
            new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_100)
            if new_key == key:
                return True
            return False

    # *** Creating table to store user's accounts and passwords ***
    def create_user_account_storage_table(self):
        with self.open_database() as cur:
            try:
                cur.execute("""CREATE TABLE account_storage(
                                username text,
                                account text,
                                password text,
                                FOREIGN KEY(username) REFERENCES users(username) ON DELETE SET NULL
                            )""")
                return "Successfully created table"
            except sqlite3.OperationalError:
                return "Table already exits"

    # *** Adding new accounts and passwords ***
    def save_account_details(self, username, account, password):
        with self.open_database() as cur:
            cur.execute("INSERT INTO account_storage VALUES(:username, :account, :password)", {'username': username, 'account': account, 'password': password})

    # *** Retriving all records ***
    def view_all_records_of_a_user(self, username):
        with self.open_database() as cur:
            cur.execute("SELECT account, password FROM account_storage WHERE username=:username", {'username': username})
            result = cur.fetchall()
            return result

    # *** Editing passwords for accounts ***
    def edit_password(self, account, password):
        with self.open_database() as cur:
            cur.execute("UPDATE account_storage SET password=:password WHERE account=:account", {'password': password, 'account': account})

    # *** Deleting accounts ***
    def delete_account(self, account):
        with self.open_database() as cur:
            cur.execute("DELETE FROM account_storage WHERE account=:account", {'account': account})


# ****** Creating database file if it does not exists ******

db = Database()
db.create_users_table()
db.create_user_account_storage_table()

# ****** Functions ******

def signup(root):
    root.withdraw()
    user = SignUp(root)

def login(root):
    root.withdraw()
    user = Login(root)

# ****** User Class ******
class User:

    def __init__(self, root, username):
        self.username = username
        window = self.window = Toplevel(root)
        self.window.title(f'{self.username}')
        self.window.geometry('300x150')
        self.window.resizable(width=False, height=False)

        self.username_label = Label(window, text=f'{self.username}', font=('Courier', 24, 'bold'))
        self.add_account = Button(window, text='Add New Account', command=self.add_new_account_display, font=('Courier', 16))
        self.view_accounts = Button(window, text='View All Accounts', command=self.view_all_accounts, font=('Courier', 16))

        self.username_label.pack(pady=20)
        self.add_account.pack(pady=10)
        self.view_accounts.pack(pady=(0, 10))

    # *** Displaying adding account window ***
    def add_new_account_display(self):
        account = self.account = Toplevel(self.window)
        self.account.title('Add New Account')
        self.account.geometry('350x200')
        self.account.resizable(width=False, height=False)

        self.label = Label(account, text='Add New Account', font=('Courier', 24, 'bold'))
        self.account_name_label = Label(account, text='Account: ', font=('Courier', 16))
        self.account_name_entry = Entry(account, font=('Courier', 16))
        self.password_label = Label(account, text='Password: ', font=('Courier', 16))
        self.password_entry = Entry(account, show='*', font=('Courier', 16))
        self.save_btn = Button(account, text='Save', command=self.save_account_and_password, font=('Courier', 16))

        self.label.grid(row=0, column=0, columnspan=2, padx=(20, 0), pady=(10, 20))
        self.account_name_label.grid(row=1, column=0, sticky=W, padx=(10, 0), pady=(0, 10))
        self.account_name_entry.grid(row=1, column=1, sticky=E, pady=(0, 10))
        self.password_label.grid(row=2, column=0, sticky=W, padx=(10, 0))
        self.password_entry.grid(row=2, column=1, sticky=E)
        self.save_btn.grid(row=3, column=0, columnspan=2, pady=20, ipadx=7)

    # *** Saving account and password ***
    def save_account_and_password(self):
        db = Database()
        username = self.username
        account = self.account_name_entry.get()
        password = self.password_entry.get()

        db.save_account_details(username, account, password)
        response = messagebox.showinfo("Success", f"Your account has been successfully saved\nUsername: {username}\nAccount: {account}\nPassword: {password}")

        if response:
            self.account_name_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')

    # *** Displaying user's all accounts with respective passwords ***
    def view_all_accounts(self):
        db = Database()
        records = db.view_all_records_of_a_user(self.username)

        if records:
            results = self.results = Toplevel(self.window)
            self.results.title('All Records')
            self.results.geometry('600x300')

            self.label = Label(results, text='All Records', font=('Courier', 24, 'bold'))
            self.label.grid(row=0, column=0, columnspan=4, padx=(20, 0), pady=(10, 10))

            self.account_label = Label(results, text='Account', font=('Courier', 20))
            self.password_label = Label(results, text='Password', font=('Courier', 20))
            self.edit_label = Label(results, text='Edit', font=('Courier', 20))
            self.delete_label = Label(results, text='Delete', font=('Courier', 20))

            self.account_label.grid(row=1, column=0, pady=5, sticky=N)
            self.password_label.grid(row=1, column=1, pady=5, sticky=N)
            self.edit_label.grid(row=1, column=2, pady=5, sticky=N)
            self.delete_label.grid(row=1, column=3, pady=5, sticky=N)

            count = 0
            row_count = 2
            for record in records:
                account = Label(results, text=f"{record[0]}", font=('Courier', 16))
                password = Label(results, text=f"{record[1]}", font=('Courier', 16))
                edit = Button(results, text='Edit', command=lambda record=record: self.edit(record), font=('Courier', 16))
                delete = Button(results, text='X', command=lambda record=record: self.delete(record), fg='red', font=('Courier', 16, 'italic'))

                account.grid(row=row_count+1, column=0, sticky=W)
                password.grid(row=row_count+1, column=1, sticky=W)
                edit.grid(row=row_count+1, column=2, sticky=E)
                delete.grid(row=row_count+1, column=3, sticky=E)

                row_count += 1
                count += 1
        else:
            results = self.results = Toplevel(self.window)
            self.results.title('View All Records')
            self.results.geometry('500x150')

            label = Label(results, text='No Records To Show', font=('Courier', 32, 'bold'))
            label.pack(side=TOP, expand=YES, fill=BOTH)

    # *** Editing passwords and not accounts ***
    def edit(self, record):
        edit_window = self.edit_window = Toplevel(self.window)
        self.edit_window.title('Edit')
        self.edit_window.geometry('350x200')
        self.edit_window.resizable(width=False, height=False)

        self.label = Label(edit_window, text='Edit Password', font=('Courier', 18, 'bold'))
        self.account_label = Label(edit_window, text='Account: ', font=('Courier', 16))
        self.account_entry = Entry(edit_window, font=('Courier', 16))
        self.password_label = Label(edit_window, text='Password: ', font=('Courier', 16))
        self.password_entry = Entry(edit_window, font=('Courier', 16))
        self.save = Button(edit_window, text='Edit', command=lambda account=record[0]: self.save_changes(account), font=('Courier', 16))

        self.label.grid(row=0, column=0, columnspan=2, padx=(20, 0), pady=(10, 20))
        self.account_label.grid(row=1, column=0, sticky=W, padx=(10, 0), pady=(0, 10))
        self.account_entry.grid(row=1, column=1, sticky=E, pady=(0, 10))
        self.password_label.grid(row=2, column=0, sticky=W, padx=(10, 0))
        self.password_entry.grid(row=2, column=1, sticky=E)
        self.save.grid(row=3, column=0, columnspan=2, padx=(20, 0), pady=10, ipadx=15)

        self.account_entry.insert(0, record[0])
        self.password_entry.insert(0, record[1])

    # *** Saving the edited password ***
    def save_changes(self, account):
        db = Database()
        password = self.password_entry.get()
        response = messagebox.askyesno('Edit', 'Are you sure you want to change your password')
        if response:
            db.edit_password(account, password)
            self.results.destroy()
            self.view_all_accounts()
        self.edit_window.destroy()

    # *** Deleting an account with its password ***
    def delete(self, record):
        db = Database()
        response = messagebox.askyesno('Delete', 'Are you sure you want to delete this account')
        if response:
            db.delete_account(record[0])
            self.results.destroy()
            self.view_all_accounts()

# ****** SignUp Class ******
class SignUp:

    def __init__(self, root):
        window = self.window = Toplevel(root)
        self.window.title('Sign Up')
        self.window.geometry('350x200')
        self.window.resizable(width=False, height=False)

        self.label = Label(window, text='Sign Up', font=('Courier', 18, 'bold'))
        self.username_label = Label(window, text='Username: ', font=('Courier', 16))
        self.username_entry = Entry(window, font=('Courier', 16))
        self.password_label = Label(window, text='Password: ', font=('Courier', 16))
        self.password_entry = Entry(window, show='*', font=('Courier', 16))
        self.submit_btn = Button(window, text='Sign Up', command=self.signup_user, font=('Courier', 16))
        self.goback_btn = Button(window, text='Go Back', command=self.go_back, font=('Courier', 16))

        self.label.grid(row=0, column=0, columnspan=2, padx=(20, 0), pady=(10, 20))
        self.username_label.grid(row=1, column=0, sticky=W, padx=(10, 0), pady=(0, 10))
        self.username_entry.grid(row=1, column=1, sticky=E, pady=(0, 10))
        self.password_label.grid(row=2, column=0, sticky=W, padx=(10, 0))
        self.password_entry.grid(row=2, column=1, sticky=E)
        self.submit_btn.grid(row=3, column=0, columnspan=2, padx=(20, 0), pady=10, ipadx=15)
        self.goback_btn.grid(row=4, column=0, columnspan=2, ipadx=7, sticky=E)

    # *** Signing up user ***
    def signup_user(self):
        db = Database()
        self.username = self.username_entry.get()
        password = self.password_entry.get()

        if db.check_user_exits_or_not(self.username):
            messagebox.showerror('Sign Up', f'{self.username} is already taken\nPlease try someother name')
        else:
            salt = os.urandom(32)
            key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_100)
            db.add_user_to_db(self.username, salt, key)
            messagebox.showinfo('Success', 'Your account has been successfully created')

    # *** Going back to the root window ***
    def go_back(self):
        self.window.destroy()
        root.deiconify()

# ****** Login Class ******
class Login:

    # *** Attempts user can make to enter correct password ***
    attempts = 5

    def __init__(self, root):
        window = self.window = Toplevel(root)
        self.window.title('Login')
        self.window.geometry('350x200')
        self.window.resizable(width=False, height=False)

        self.label = Label(window, text='Login', font=('Courier', 18, 'bold'))
        self.username_label = Label(window, text='Username: ', font=('Courier', 16))
        self.username_entry = Entry(window, font=('Courier', 16))
        self.password_label = Label(window, text='Password: ', font=('Courier', 16))
        self.password_entry = Entry(window, show='*', font=('Courier', 16))
        self.submit_btn = Button(window, text='Login', command=self.login_user, font=('Courier', 16))
        self.goback_btn = Button(window, text='Go Back', command=self.go_back, font=('Courier', 16))

        self.label.grid(row=0, column=0, columnspan=2, padx=(20, 0), pady=(10, 20))
        self.username_label.grid(row=1, column=0, sticky=W, padx=(10, 0), pady=(0, 10))
        self.username_entry.grid(row=1, column=1, sticky=E, pady=(0, 10))
        self.password_label.grid(row=2, column=0, sticky=W, padx=(10, 0))
        self.password_entry.grid(row=2, column=1, sticky=E)
        self.submit_btn.grid(row=3, column=0, columnspan=2, padx=(20, 0), pady=10, ipadx=15)
        self.goback_btn.grid(row=4, column=0, columnspan=2, ipadx=7, sticky=E)

    # *** Logging in user ***
    def login_user(self):
        db = Database()
        self.username = self.username_entry.get()
        password = self.password_entry.get()
        if db.validate_user(self.username, password) == "User does not exits":
            answer = messagebox.askquestion('Login', f'{self.username} does not exits\nDo you want to create an account')
            if answer == 'yes':
                self.window.destroy()
                user = SignUp(root)
            return None
        if db.validate_user(self.username, password):
            self.window.destroy()
            user = User(root, self.username)
        if not db.validate_user(self.username, password):
            if self.attempts == 0:
                window.quit()
            messagebox.showerror('Login', f'Wrong Password\nYou have {self.attempts-1} attempts remaining')
            self.attempts -= 1

    # *** Going back to the root window ***
    def go_back(self):
        self.window.destroy()
        root.deiconify()

# *******************
root.mainloop()

# *******************************

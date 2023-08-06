# Importation

from tkinter import *
from tkinter import messagebox
import mysql.connector as MC 
from mysql.connector import errorcode

# Var

u1 = open("user.txt", "r")

global lg
global LoginFrame
lg = Tk()
LoginFrame = Frame(lg, width=350, height=350, bg="white")

# Def

class login():
    # Windows

    def setTitle(title):
        lg.title(title)
        lg.geometry('925x500+300+200')
        lg.resizable(False, False)

    # LoginSetup

    class form():

        # Form

        def form(title="Sign in", titleSize="20", titleColor="#57a1f8" ,positionX="300", positionY="70"):

            # Frame

            LoginFrame.place(x=positionX, y=positionY)

            # Title

            LoginHeading = Label(LoginFrame, text=title, fg=titleColor,bg='white', font=(titleSize))
            LoginHeading.place(x=150, y=5)

            
        # User

        def userInput(placeholder="Username", widht="20"):

            # Global

            global userInputLogin
            
            # Def

            def on_enter(e):
                name = userInputLogin.get()
                if name==placeholder:
                    userInputLogin.delete(0, END)

            def on_leave(e):
                name = userInputLogin.get()
                if name=='':
                    userInputLogin.insert(0, placeholder)

            # Input

            userInputLogin = Entry(LoginFrame, width=widht, fg="black", border=0, bg="white", font=(11))
            userInputLogin.place(x=30, y=80)

            # Placeholder

            userInputLogin.insert(0, placeholder)
            userInputLogin.bind('<FocusIn>', on_enter)
            userInputLogin.bind('<FocusOut>', on_leave)

            # Line

            Frame(LoginFrame, width=295, height=2, bg="black").place(x=25, y=108)

        # Password

        def passwordInput(placeholder="Password", widht="20"):

            # Global

            global passwordInputLogin

            # Def

            def on_enter(e):
                name = passwordInputLogin.get()
                if name==placeholder:
                    passwordInputLogin.delete(0, END)
                passwordInputLogin.config(show="*")

            def on_leave(e):
                name = passwordInputLogin.get()
                if name=='':
                    passwordInputLogin.insert(0, placeholder)
                    passwordInputLogin.config(show="")

            # Input

            passwordInputLogin = Entry(LoginFrame, width=widht, fg="black", border=0, bg="white", font=(11))
            passwordInputLogin.place(x=30, y=150)

            # PLaceholder

            passwordInputLogin.insert(0, placeholder)
            passwordInputLogin.bind('<FocusIn>', on_enter)
            passwordInputLogin.bind('<FocusOut>', on_leave)

            # Line

            Frame(LoginFrame, width=295, height=2, bg="black").place(x=25, y=177)

        # Button

        def buttonLogin(text="Sign in", widht=39, pady=7, bg="#57a1f8", fg="white", border=0):

            def signin():
                username = userInputLogin.get()
                password = passwordInputLogin.get()


                try:
                    if usernameGL != "":
                        if username == usernameGL:
                            if password == passwordGL:
                                print("Correct")
                            else: 
                                messagebox.showerror("Login", "Password is incorrect !")
                        else:
                            messagebox.showerror("Login", "Username is incorrect !")
                except:
                    try:
                        query='select * from '+Table+' where '+TableUser+'=%s and '+TablePassword+'=%s'
                        cursor.execute(query ,(username ,password))
                        row = cursor.fetchone()
                        if row == None:
                            messagebox.showerror('Login', 'Invalid username or/and password')
                        else:
                            messagebox.showinfo('Succes', 'Login is sucessful')
                            u1 = open("user.txt", "w+")
                            u1.write(username)
                            u1.close()
                            print("Welcome "+username)
                    except MC.Error as err:
                        messagebox.showerror("MySQL Error", err)

                    
                    

            buttonLogin = Button(LoginFrame, text=text, width=widht, pady=pady, bg=bg, fg=fg, border=border, command=signin)
            buttonLogin.place(x=35,y=224)

        
        def buttonRegister(text="Register", widht=39, pady=7, bg="#57a1f8", fg="white", border=0):
            buttonRegister = Button(LoginFrame, text=text, width=widht, pady=pady, bg=bg, fg=fg, border=border)
            buttonRegister.place(x=35, y=284)

    def ConfigLogin(username, password):
        global usernameGL
        global passwordGL

        usernameGL = username
        passwordGL = password

    def MySQLConfig(host, username, password, database, table, userTable = "user", passwordTabel = "password"):
        config = {
            'user': username,
            'password': password,
            'host': host,
            'database': database,
            'raise_on_warnings': True
        }

        try:
            # Global

            global cnx
            global Table
            global TableUser
            global TablePassword
            global cursor

            # Code

            cnx = MC.connect(**config)
            Table = table
            TableUser = userTable
            TablePassword = passwordTabel
            cursor = cnx.cursor()
            
        except MC.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                messagebox.showerror("MySQL Error", "Username or password is incorrect !")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                messagebox.showerror("MySQL Error", "No found your datebase")
            else:
                messagebox.showerror("MySQL Error" ,err)
        
    # MainLoop

    def loop():
        lg.mainloop()

username = u1.read()
u1.close()

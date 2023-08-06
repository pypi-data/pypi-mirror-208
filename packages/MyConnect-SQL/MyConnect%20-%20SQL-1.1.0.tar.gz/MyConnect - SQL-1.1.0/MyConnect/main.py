# Import

import AuthLogin
import time
from tkinter import *

# Var

lgn = ""

# Title

AuthLogin.login.setTitle("MyConnect - Login")

# Setup

AuthLogin.login.form.form('Login', '23', '#57a1f8', '300', '70')
AuthLogin.login.form.userInput(widht=25)
AuthLogin.login.form.passwordInput(widht=25)
AuthLogin.login.form.buttonLogin()
# Config login
            

AuthLogin.login.MySQLConfig('localhost', 'root', '', 'user', 'user')

# Loop

AuthLogin.login.loop()

# Connexion : Yes

time.sleep(1)

root = Tk()
root.title("MyConnect - Hello")
root.geometry("800x500")
root.mainloop()
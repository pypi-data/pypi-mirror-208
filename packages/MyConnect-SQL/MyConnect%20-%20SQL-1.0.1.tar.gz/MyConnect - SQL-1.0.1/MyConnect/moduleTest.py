from AuthLogin.AuthLogin import *

if username == "":
    # Title

    login.setTitle("AuthLogin - Login")

    # Setup

    login.form.form('Login', '23', '#57a1f8', '300', '70')
    login.form.userInput(widht=25)
    login.form.passwordInput(widht=25)
    login.form.buttonLogin()

    # Config login
            

    login.MySQLConfig('localhost', 'root', '', 'user', 'user')

    # Loop

    login.loop()
else:
    print("Welcome "+username)

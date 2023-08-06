from MyConnect import AuthLogin

if AuthLogin.username == "":
    # Title

    AuthLogin.login.setTitle("AuthLogin - Login")

    # Setup

    AuthLogin.login.form.form('Login', '23', '#57a1f8', '300', '70')
    AuthLogin.login.form.userInput(widht=25)
    AuthLogin.login.form.passwordInput(widht=25)
    AuthLogin.login.form.buttonLogin()

    # Config login
            

    AuthLogin.login.MySQLConfig('localhost', 'root', '', 'user', 'user')

    # Loop

    AuthLogin.login.loop()
else:
    print("Welcome "+AuthLogin.username)


# 

## Description :

MyConnect is a module that facilitates the creation of login and registration pages 
The module is rather a simplification because if we can say that it compresses the tkinter variables 
(That's why you have to put a login.loop() at the end).


## Installation

Install MyConnect

```bash
  pip install MyConnect
```


    
## Documentation

Create you login page

```py
  from MyConnect import AuthLogin

  # Title

  login.setTitle("MyConnect - Login")

  # Setup

  login.form.form('Login', '23', '#57a1f8', '300', '70')
  login.form.userInput(widht=25)
  login.form.passwordInput(widht=25)
  login.form.buttonLogin()

  # Config login
            

  login.MySQLConfig('localhost', 'root', '', 'user', 'user')

  # Loop

  login.loop()
```



# IMS - Inventory Management Software
#### Video Demo: <URL HERE>
#### Description: 

IMS is a web application written in [Python](https://www.python.org/) with the [Flask](https://flask.palletsprojects.com/en/2.3.x/) Framework, It uses [SQLite](https://www.sqlite.org/index.html) for database management in the backend and [PicoCSS](https://picocss.com/) for the graphical interface in the frontend.

It features authentication and management systems.

The functionality of the authentication system includes:

- Registering a new user
- Logging in and out of the system
- Changing your username and password
- Setting up two-factor authentication
- Recovering your account if you forget your password

In addition, the software includes a set of functionalities that allow users to configure and initialize a management system based on cost center. Users can: 
- Create items and products
- Store supplier information
- Add new suppliers
- Register new purchases
- Register sales

The application enables management of raw materials, components, and finished products, as well as evaluation of an elementary financial state of business performance.

#### Motivation:

This software is our final project for [CS50x](https://cs50.harvard.edu/x/) Harvard University’s introduction to the intellectual enterprises of computer science and the art of programming.

We would especially like to give **a huge thanks** to professor [David J. Malan](https://cs.harvard.edu/malan/) and all [CS50 Staff](https://cs50.harvard.edu/x/2023/staff/) for their clear and engaging teaching style, their generosity besides all the shared knowledge that opened the inmense world of computer science and programming to us.

*This project is developed by [Angel Piña](https://github.com/angelpinha/) & [Nureddyn Ballout](https://github.com/nureddyn/), both students from Barinas - Venezuela.* 🇻🇪

---

## Usage:

### Fast deployment:

If you are in a hurry an just need to run the app, after installing all the dependencies in your local machine, execute the following command in Bash:

```Bash
  python run.py  
```

NOTE: You should be inside the main project folder.

To launch the application, user should do the following steps:

- Install Python > 3.4 on your computer.

To install the Virtual Development Environment:

```Bash
  python -m venv venv

# OR

  python -m venv .venv
```

NOTE: venv folder for Linux and MacOS can be named `.venv` to make the venv folder hidden.

Virtual environment activation:

Windows:
```
  # In cmd.exe
  venv\Scripts\activate.bat

  # In PowerShell
  venv\Scripts\Activate.ps1
```

Linux and MacOS:

```Bash
  source venv/bin/activate

# OR

  source .venv/bin/activate

# Given the case
```

Once the virtual environment is activated, you should install all project dependencies by running:

```Bash
  pip install -e .
```

NOTE: This step could be done only the first time you try to run the app.

To know which packages are used by the app, you can run inside the Virtual Environment:

```Bash
pip list --local
```

Once all packages are installed into the Virtual Environment, you can run the app by entering the following command:

For normal usage:
```Bash
  flask run
```

For development usage:
```Bash
  flask --debug run
```

The project should be hosted on the following adress by default:

http://127.0.0.1:5000/

Enjoy!

---


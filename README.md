# IMS - Inventory Management Software
## Video Demo:

You can watch a brief App Video Demo by clicking on the following [Youtube](https://youtu.be/kaeJOYoBBm4) link:

https://youtu.be/kaeJOYoBBm4

## Motivation:

This software is our final project for [CS50x](https://cs50.harvard.edu/x/) Harvard University’s introduction to the intellectual enterprises of computer science and the art of programming.

We would especially like to give a **huge thanks** to professor [David J. Malan](https://cs.harvard.edu/malan/) and all [CS50 Staff](https://cs50.harvard.edu/x/2023/staff/) for their clear and engaging teaching style, their generosity besides all the shared knowledge that opened the inmense world of computer science and programming to us.

*This project is developed by [Angel Piña](https://github.com/angelpinha/) & [Nureddyn Ballout](https://github.com/nureddyn/), both students from Barinas - Venezuela.* 🇻🇪

## Description: 

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

## Usage:

### Requirements:

  - Install Python > 3.4 on your computer.

### Creating a Virtual Environment:

Inside the **root folder** of the project, you should execute:

```Bash
  python -m venv .venv
```

### Activating the Virtual Environment:

You can Activate the Virtual Environment depending of your computer's operating system:

**Activating in Windows:**
```
  # In cmd.exe
  venv\Scripts\activate.bat

  # In PowerShell
  venv\Scripts\Activate.ps1
```

**Activating in Linux and MacOS:**

```Bash
  source .venv/bin/activate
```

### Installing Dependencies:

Once the Virtual Environment has been Activated, you should install all project dependencies by running:

```Bash
  pip install -e .
```

To list which dependencies are being used by the App, you can run the following command inside the Activated Virtual Environment:

```Bash
pip list --local
```

### Deploying the App:

Once all packages are installed into the Activated Virtual Environment, you can run the App by entering the following command:

**For Normal usage:**
```Bash
  flask run
```

**For Development usage:**
```Bash
  flask --debug run
```

### Fast deployment:

Once you've Activated the Virtual Environment and installed all the dependencies used by the App, you can fast deploy the App by executing the following command:

```Bash
  python run.py  
```

### Using the App:

To use the App you should enter the following adress in your web browser:

http://127.0.0.1:5000/

Enjoy! 😎

### Deactivating the Virtual Environment:

You can fast Deactivate the Virtual Environment by **closing** the command line interface that you've used to deploy the App.

Otherwise, you can run the following command in the console:

```Bash
  deactivate
```

### Uninstalling the App:

*Assuming that all the installations were executed inside the Activated Virtual Environment*. You can uninstall all the dependencies used by the App by **deleting the project folder** and all its contents.

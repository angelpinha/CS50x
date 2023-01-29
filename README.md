# CS50x - Final Project

CS50x - Harvard's Introduction to Computer Science - Final Project

---

## Usage:

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

This project is developed by: [Angel Piña](https://github.com/angelpinha/) & [Nureddyn Ballout](https://github.com/nureddyn/)

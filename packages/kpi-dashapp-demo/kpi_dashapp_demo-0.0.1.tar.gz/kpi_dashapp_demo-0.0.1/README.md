## Dash web application for KPI monitory and visualization

This repo is a package for building a dash web application for KPI monitory and visualization. It is a Proof of Concept for how dash can be used to automate the calculation of KPI.

## How to run the app

To run this application, you should first create a virtual environment, clone 
the repo and install it as a package. This can be achieved from the terminal as 
follows:

1. Create virtual environment from terminal 
These commands are for MacOS and the virtual environment is named as env

```python3 venv env```

2. Activate virtual environment
```source env/bin/activate```

3. Clone repo 
```git clone https://github.com/agbleze/kpi_dashapp.git ```

4. Install it 
```pip install .```


Once installed, you can run the app from your terminal as follows:
```python -m kpi_dashapp_demo```


## Expected behaviour

The URL for accessing the app will be shown in the terminal as http://127.0.0.1:8040. Port 8040 is used by default and incase you are already using it, then 
you can provide a new port number or shutdown the application at port 8040 in 
case that is your preference. 










### Running the app
The app can be run using the command in the terminal below
```
python app.py
```

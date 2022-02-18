# Traiding tool with Binance and Kucoin 
This repo contains a [Dash app](https://plotly.com/dash/) for traiding using Binance and Kucoin public APIs information. To run it, we recommend to create a virtual environment and install required dependencies.

## Create a virtual environment
To run the app, first create a virtual environment using python module `virtualenv`:
> `$ python -m virtualenv <env name>`

and activate it
- Mac/Linux: `$ source <env name>/bin/activate`
- Windows: `$ source <env name>/Scripts/activate`

If you name your environment something different from `my_env`, do not forget to add it to the `.gitignore` file. When finished, remember to deactivate virtual environment
> `$ deactivate`

## Install dependencies
Then install dependencies with pip:
> `$ pip install -r requirements.txt`

## Create a configuration file
You need to provide a configuration file with actual and test API tokens for Binance and Kucoin. Create a `secret.cfg` and **do not publish or share it**
```
[BINANCE]
ACTUAL_API_KEY = <your-actual-api-key>
ACTUAL_SECRET_KEY = <your-actual-secret-key>
```

## Run the app in your browser
and finally run it
> `$ python app.py`



# Traiding tool with Binance 
This repo contains a [Dash app](https://plotly.com/dash/) for traiding using Binance public API information.

# Local installation

## Binance API Keys

Binance API is the application programming interface (API) for the Binance platform, which allows users to programmatically interact with the Binance ecosystem. The API allows users to access the Binance platform's data and functionality, such as placing orders, checking account balances, and managing their assets.

Binance testnet, on the other hand, is a separate environment from the main Binance platform, where users can test their applications without using real funds. The testnet is identical to the main platform in terms of functionality, but it uses separate servers and networks, and its own set of test coins.

To use the application it is necessary to have the required API keys in the environments: 
  * `API-KEY`
  * `SECRET-KEY` 

To get the testet keys in the test enviroment follow [these steps](https://www.binance.com/en/support/faq/how-to-test-my-functions-on-binance-testnet-ab78f9a1b8824cf0a106b4229c76496d).

To get your real Binance API keys, you will need to have a Binance account. If you don't have an account yet, you can create one [here](https://www.binance.com/en/register?ref=12327366). To get the keys follow [these steps](https://www.binance.com/en/support/faq/how-to-download-and-set-up-binance-code-api-af014f44f45845debf79b4cf81333a25).



## Installation

To install the dependencies for this project, you will need to have pip installed on your system. If you don't have pip, you can install it by following the instructions [here](https://pip.pypa.io/en/stable/installing/).

Once you have pip installed, navigate to the directory where your `requirements.txt` file is located and run the following command:

```
pip install -r requirements.txt
```

This will install all of the dependencies listed in the `requirements.txt` file.

Next, you will need to fill the `secret.cfg` file with the appropriate information. This file typically contains sensitive information such as API keys or passwords, so be sure to keep it secure. The contents of the file can be found in `secret.cfg.template`:

```
[ENVIRONMENT]
ENV = LOCAL

[BINANCE]
ACTUAL-API-KEY = 
ACTUAL-SECRET-KEY = 
TEST-API-KEY = 
TEST-SECRET-KEY = 
```

Once you have filled in the `secret.cfg` file with the correct information, you can move on to executing `db_exec.py`. This script is is used to set up the SQLite database for the project, so you need to run it before you can use the main program. To execute the script, run the following command:

```
python db_exec.py
```

Finally, once the database has been set up you will find a `trading_tool.db` file in your root directory. Now you can run the `cryptotradingtool.py` script to use the main program. To do this, run the following command:

```
python cryptotradingtool.py
```

This will launch the main program and you can begin using it in a web browser following the localhost direction provided in the console.

```
 * Running on http://127.0.0.1:5000 
```



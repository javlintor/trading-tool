# The `test_strategy` function takes a `strategy` object as an argument
# and prints information about the strategy object to the console
def test_strategy(strategy):

    # Print the first few rows of the `df` attribute of the `strategy` object
    # along with its class
    print("df", strategy.df.head())
    print("class of df", type(strategy.df.head()))

    # Print the `a` and `b` attributes of the `start_wallet` attribute of the `strategy` object
    print("start_wallet.a", strategy.start_wallet.a)
    print("start_wallet.b", strategy.start_wallet.b)

    # Print the `a` and `b` attributes of the `end_wallet` attribute of the `strategy` object
    # along with its class
    print("end_wallet.a", strategy.end_wallet.a)
    print("end_wallet.b", strategy.end_wallet.b)
    print("class of end_wallet", type(strategy.end_wallet))

    # Print the output of the `get_operations` method of the `strategy` object
    # along with its class
    print("get_operations", strategy.get_operations().head())
    print("class of get_opeations", type(strategy.get_operations().head()))

    # Print the output of the `get_n_operations` method of the `strategy` object
    # along with its class
    print("get_n_operations", strategy.get_n_operations())
    print("class of get_n_opeations", type(strategy.get_n_operations()))

    # Print the output of the `get_n_operations_by_hour` method of the `strategy` object
    # along with its class
    print("get_n_operations_by_hour", strategy.get_n_operations_by_hour())
    print("class of get_n_operations_by_hour", type(strategy.get_n_operations_by_hour()))

    # Print the output of the `get_mean_operation_time` method of the `strategy` object
    # along with its class
    print("get_mean_operation_time", strategy.get_mean_operation_time())
    print("class of get_mean_operation_time", type(strategy.get_mean_operation_time()))

    # Print the output of the `get_n_good_operations` method of the `strategy` object
    # along with its class
    print("get_n_good_operations", strategy.get_n_good_operations())
    print("class of get_n_good_operations", type(strategy.get_n_good_operations()))

    # Print the output of the `get_n_bad_operations` method of the `strategy` object
    # along with its class
    print("get_n_bad_operations", strategy.get_n_bad_operations())
    print("class of get_n_bad_operations", type(strategy.get_n_bad_operations()))

    # Print the output of the `get_periods` method of the `strategy` object
    # along with its class
    print("get_periods", strategy.get_periods())
    print("class of get_periods", type(strategy.get_periods()))

    # Print the output of the `get_profitabilities` method of the `strategy` object
    # along with its class
    print("get_profitabilities", strategy.get_profitabilities())
    print("class of get_profitabilities", type(strategy.get_profitabilities()))

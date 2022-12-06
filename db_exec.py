from exec.create import main as create_main
from exec.insert_assets import main as i_assets_main
from exec.insert_symbols import main as i_symbols_main
from exec.insert_klines_1d import main as i_klines_main

def main():
    create_main()  # Create the database
    i_assets_main()  # Insert assets into the database
    i_symbols_main()  # Insert symbols into the database
    i_klines_main()  # Insert 1-day klines into the database

if __name__ == "__main__":
    main()
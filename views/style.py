import re

colors = {"background": "#12181b", "text": "white"}
table_colors = {"background": "#2a2e35", "header": "#12181b"}

GRAY5 = "#2a2e35"
LIGHT_GREEN = "#44B78B"
ORANGE = "#d06c14"

def format_number(num, decimal_places):
    dp = f"{num:.{str(decimal_places)}f}"
    return dp

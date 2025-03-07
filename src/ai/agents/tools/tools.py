import math
from langchain_core.tools import tool
from datetime import datetime

@tool
def epoch_converter(date_str):
    date_obj =datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    epoch_time = int(date_obj.timestamp())
    return epoch_time



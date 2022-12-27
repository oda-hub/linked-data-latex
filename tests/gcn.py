import requests
import re

def cite(num):
    if int(num) == 100:
        return "Hurley1998_gcn100"
    else:
        return num


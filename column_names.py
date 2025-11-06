import pandas as pd
import numpy as np


def check_simple(string: str)->bool:
    return string != "nan" and string != "Y" and string != "->" and string != "SEAT" and string != "GATE" and string != "/" and string.find(":") == -1 and string != "BOARDING PASS" and string != "E-TICKET"


def check_dif(string: str)->bool:
    return len(string.split()) < 4 and not(string.isdigit())

def filter_elem(string):
    return check_simple(string) and len(string.split()) < 4

def maked_dict_name(coords, names):
    result = {}
    for pos in range(len(coords)):
        result[names[pos][:-1]] = coords[pos]
    return result


class Names:
    names_file = ""
    df = ""
    flag_init = 0
    def __init__(self, names, card):
        self.df = pd.read_excel(card, sheet_name=0, header=None)
        self.names_file = open(names, "r")
        self.flag_init = 1

    def get_cords(self):
        if self.flag_init == 0:
            return {}
        rows, cols = self.df.shape
        coords = (np.dstack(np.indices((rows, cols)))).reshape(-1, 2)
        coords = list(filter(lambda cord: filter_elem(str(self.df.iat[cord[0], cord[1]])), coords))
        names = self.names_file.readlines()
        return maked_dict_name(coords, names)


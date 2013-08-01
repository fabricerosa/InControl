
def str_to_dt(dte):
    dte = str(dte)
    dte = string.strip(dte)
    if len(dte) == 10:
        y = int(dte[0:4])
        m = int(dte[5:7])
        d = int(dte[8:])
        return datetime.date(y, m, d) 
    else:
        return None
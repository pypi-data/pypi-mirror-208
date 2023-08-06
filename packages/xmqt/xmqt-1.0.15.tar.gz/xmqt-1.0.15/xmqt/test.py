import numpy as np
import pandas as pd
import datetime as dt

from CAL.PyCAL import *


cal = Calendar('China.SSE')
tradeDateList=cal.bizDatesList(Date(2022,1,1), Date(2025,12,31))
tradeDates=[str(d) for d in tradeDateList]
print(tradeDates)

tradeDateNp = np.array(tradeDates)  # tradeDate 在‘阿岛格：2022年股市法定交易日期‘已经介绍的方法


def get_ExpireWeek_of_month(year, month, day):
    end = int(dt.datetime(year, month, day).strftime("%W"))
    begin = int(dt.datetime(year, month, 1).strftime("%W"))
    expireWeek = end - begin + 1
    # if first day of the month is great equal than Thirsday,expireWeek is 5th week, not 4th week, week 1,2,3,4,5 ->0,1,2,3,4
    # keep 4th week (expireWeek=4)as expire week
    if dt.datetime(year, month, 1).isoweekday() >= 4:
        expireWeek = expireWeek - 1

    return expireWeek


def getExpireDateList():
    tdf = pd.DataFrame(tradeDates, columns=['tradeDate'])
    tdf['dt'] = tdf['tradeDate'].apply(lambda df: dt.datetime.strptime(df, '%Y-%m-%d'))
    tdf['wday'] = tdf['dt'].apply(lambda df: df.isoweekday())
    tdf['wth'] = tdf['dt'].apply(lambda df: get_ExpireWeek_of_month(df.year, df.month, df.day))
    expDate = tdf[(tdf['wth'] == 4) & (tdf['wday'] == 3)]['tradeDate'].values
    return expDate


if __name__ == '__main__':
    e = getExpireDateList()
    print
    "',\n'".join(e)
import pandas as pd
import numpy as np
import operator
from tqdm import tqdm


def get_dynamic_vp(data: pd.DataFrame) -> pd.DataFrame:

    """
    Given the canonical dataframe recorded, this function returns a dataframe with volume in ASK / BID restarted at the
    of a given day.
    :param data: canonical dataframe recorded (tick-by-tick wth the DOM attached)
    :return: ask and bid numpy array (respectively)
    """

    dates = data.Date.unique()
    datas = list()

    for date in dates:

        print(f'Dynamic VP processing date {date}')
        ask = data[(data.Date == date) & (data.TradeType == 2)]  # get the ask per date...
        bid = data[(data.Date == date) & (data.TradeType == 1)]  # get the bid per date...

        ask['AskVolume_VP'] = np.cumsum(ask.Volume)
        ask['BidVolume_VP'] = np.zeros(ask.shape[0])
        bid['AskVolume_VP'] = np.zeros(bid.shape[0])
        bid['BidVolume_VP'] = np.cumsum(bid.Volume)

        single_date = pd.concat([ask, bid], axis=0)
        single_date.sort_values(['Date', 'Time'], ascending=[True, True], inplace=True)
        single_date['AskVolume_VP'] = single_date['AskVolume_VP'].replace(to_replace=0, method='ffill').astype(np.int64)  # Fill zeros with last cumulative value
        single_date['BidVolume_VP'] = single_date['BidVolume_VP'].replace(to_replace=0, method='ffill').astype(np.int64)  # Fill zeros with last cumulative value

        datas.append(single_date)

    return pd.concat(datas)


def get_daily_moving_POC(df: pd.DataFrame) -> np.array:

    """
    Given the canonical dataframe recorded, this function returns the Point of Control (i.e. POC) that is moving during
    the day giving the volume sentiment of uptrending market or choppy market of downtrending market.
    :param df: anonical dataframe recorded
    :return: numpy array for the daily moving poc
    """

    volume = np.array(df.Volume)
    price = np.array(df.Price)
    date = np.array(df.Date)
    poc_final = {}
    len_ = len(price)
    poc_ = np.zeros(len_)

    poc_final[price[0]] = volume[0]
    poc_[0] = price[0]

    for i in tqdm(range(1, len_ - 1)):
        cp = price[i]
        if date[i] != date[i - 1]:
            poc_final.clear()
            poc_final[cp] = volume[i]
            poc_[i] = cp
        else:
            if cp in poc_final:
                poc_final[cp] += volume[i]
            else:
                poc_final[cp] = volume[i]
            poc_[i] = max(poc_final.items(), key=operator.itemgetter(1))[0]

    poc_[len_ - 1] = price[len_ - 1]

    return poc_



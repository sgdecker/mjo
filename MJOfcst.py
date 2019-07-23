import numpy as np
import pandas as pd


def get_data():
    mjo_df = pd.read_pickle('mjo.pickle.xz')
    deg_day_df = pd.read_pickle('deg_days5.pickle.xz')
    df = mjo_df.join(deg_day_df, how='inner')

    mjo_mask = df.columns.isin(['RMM1', 'RMM2'])
    dd_mask = df.columns.isin(['cdd_anom', 'hdd_anom'])

    # MJO is available two days prior
    cols_to_shift = df.columns[mjo_mask]
    df[cols_to_shift] = df[cols_to_shift].shift(2)

    # Forecast is for 16-20 day period, so 17 days after today is center.
    cols_to_shift = df.columns[dd_mask]
    df[cols_to_shift] = df[cols_to_shift].shift(-17)

    return df


def criteria_filter(c, r):
    res = np.sqrt((c['RMM1'] - r[0])**2 + (c['RMM2'] - r[1])**2) < .5

    return res


def find_analogs(df, today, rmm):
    # Look for analogs within 45 days of today's date
    # between the years indicated
    first_year = 1981
    last_year = 2018
    tdelt = pd.to_timedelta(45, 'D')

    periods = []
    for y in range(first_year, last_year+1):
        try:
            mid = pd.Timestamp(year=y, month=today.month, day=today.day)
        except ValueError:  # Leap day!
            mid = pd.Timestamp(year=y, month=3, day=1)
        prd = pd.period_range(mid - tdelt, mid + tdelt)
        for p in prd:
            periods.append(p.to_timestamp())
    periods = pd.to_datetime(periods)
    candidates = df.loc[periods]

    criteria = criteria_filter(candidates, rmm)
    analogs = candidates[criteria]

    return(analogs)


# Input data
today = pd.Timestamp('2019-7-22')
cur_rmm1 = -1.2411472
cur_rmm2 = -0.88222831

df = get_data()
analogs = find_analogs(df, today, (cur_rmm1, cur_rmm2))
print(analogs['cdd_anom'].describe())

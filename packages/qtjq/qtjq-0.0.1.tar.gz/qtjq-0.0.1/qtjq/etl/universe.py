import datetime
import pandas as pd
import jqdata as jqd
import qtc.ext.multiprocessing as mp
import qtc.utils.datetime_utils as dtu
import qtjq.utils as qtjqu


def compile_sec_data_single_date(dateid, all_sec_cols=False):
    datestr = dtu.dateid_to_datestr(dateid=dateid, sep='-')
    secs = get_all_securities(types='stock', date=datestr)
    secs.index.name = 'code'
    secs_cnt = len(secs)

    factors = ['price_no_fq',
               'market_cap', 'circulating_market_cap',
               'TVMA20']
    fvs = qtjqu.load_factor_values(
        jq_codes=secs.index.to_list(),
        factors=factors,
        end_date=datestr, count=1,
    )
    fvs_cnt = len(fvs)

    sec_data = pd.merge(secs.reset_index(),
                        fvs.reset_index(),
                        on='code', how='right')

    for date_col in ['trade_date', 'start_date', 'end_date']:
        sec_data[date_col] = pd.to_datetime(sec_data[date_col])

    sec_data.rename(columns={'code': 'jq_code'}, inplace=True)
    #     sec_data['ts_code'] = sec_data['jq_code'].apply(
    #         lambda x: x.replace('.XSHE', '.SZ').replace('.XSHG', 'SH')
    #     )

    #     cols = ['trade_date','jq_code','display_name','start_date','end_date'] + factors

    if not all_sec_cols:
        cols = ['trade_date', 'jq_code'] + factors
        sec_data = sec_data[cols]

    return sec_data


def compile_sec_data(start_date, end_date):
    dateids = [int(date.strftime('%Y%m%d'))
               for date in jqd.get_trade_days(start_date=start_date, end_date=end_date)]
    sec_data = mp.run_multi_dateids_joblib(
        dateids=dateids,
        func=compile_sec_data_single_date,
        concat_axis=0,
        n_jobs=4
    )

    return sec_data
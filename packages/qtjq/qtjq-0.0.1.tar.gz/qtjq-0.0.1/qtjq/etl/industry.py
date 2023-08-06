import pandas as pd
import jqfactor as jqf
import qtc.utils.datetime_utils as dtu
import qtc.utils.misc_utils as mu
import qtjq.utils as qtjqu
from qtc.ext.logging import set_logger
logger = set_logger()


DATA_TYPE_DB_CONFIG = dict()


def load_industries(dateid, secs=None,
                    batch_size=40):
    datestr = dtu.dateid_to_datestr(dateid=dateid)
    if secs is None:
        secs = get_all_securities(types=['stock'], date=datestr)
        secs = secs.index.to_list()
    else:
        secs = list(mu.iterable_to_tuple(secs, raw_type='str'))

    if len(secs) == 0:
        return None

    industries = get_industry(security=secs, date=datestr)
    x = list()
    for jq_code, v in industries.items():
        for ind_type, ind_code in v.items():
            x.append({'jq_code': jq_code, 'industry_type': ind_type, 'industry_code': ind_code['industry_code']})

    industries = pd.DataFrame(x).pivot('jq_code', 'industry_type', 'industry_code')

    return industries


# def persist_industry(dateid,
#                      source='VENDOR', destinations='DB',
#                      **db_config):
#     pkl_gz_file = f'factor_values_{dateid}.pkl.gz'
#     if source=='VENDOR':
#         factor_values = load_all_factor_values(dateid=dateid)
#     elif source=='FC':
#         factor_values = pd.read_pickle(pkl_gz_file)
#     else:
#         raise Exception(f'source={source} not supported in [VENDOR|FC] !')
#
#     factor_info = jqf.get_all_factors()
#     factor_info = factor_info[factor_info['factor']!='price_no_fq']
#
#     factors = factor_info['factor'].to_list()
#     cne5_factors = ['size', 'beta', 'momentum', 'residual_volatility', 'non_linear_size',
#                     'book_to_price_ratio', 'liquidity', 'earnings_yield', 'growth', 'leverage']
#     factors = [f for f in factors if f not in cne5_factors] + cne5_factors
#
#     cols = ['trade_date', 'ts_code'] + factors
#     factor_values = factor_values[cols]
#
#     for destination in mu.iterable_to_tuple(destinations, raw_type='str'):
#         if destination=='FC':
#             factor_values.to_pickle(pkl_gz_file, compression='gzip')
#             logger.info(f'destination={destination}: {pkl_gz_file}')
#         elif destination=='DB':
#             data_type = 'FACTOR_VALUE'
#             conn, database = qtjqu.get_conn_data_type(data_type=data_type,
#                                                       **db_config)
#             schema = 'joinquant'
#             table_name = 'FactorValue'
#             factor_values.to_sql(table_name,
#                                  con=conn, schema=schema,
#                                  if_exists='append', index=False)
#
#             logger.info(f'{data_type} with shape {factor_values.shape} '
#                         f'persisted into "{database}"."{schema}"."{table_name}" .')
#         else:
#             raise Exception(f'destination={destination} not supported in [FC|DB] !')

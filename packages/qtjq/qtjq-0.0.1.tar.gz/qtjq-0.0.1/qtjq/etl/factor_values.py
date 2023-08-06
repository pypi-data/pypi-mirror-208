import pandas as pd
import jqfactor as jqf
import qtc.utils.datetime_utils as dtu
import qtc.utils.misc_utils as mu
import qtjq.utils as qtjqu
from qtjq.etl.factor_info import CNE5_FACTORS
from qtc.ext.logging import set_logger
logger = set_logger()


DATA_TYPE_DB_CONFIG = dict()


# def persist_cne5(dateid, securities=None,
#                  **db_config):
#     global DATA_TYPE_DB_CONFIG
# 
#     datestr = dtu.dateid_to_datestr(dateid=dateid)
#     if securities is None:
#         securities = get_all_securities(types=['stock'], date=datestr)
#         securities = securities.index.to_list()
#     else:
#         securities = list(mu.iterable_to_tuple(securities, raw_type='str'))
# 
#     if len(securities) == 0:
#         return None
# 
#     factor_names = ['size', 'beta', 'momentum', 'residual_volatility', 'non_linear_size',
#                     'book_to_price_ratio', 'liquidity', 'earnings_yield', 'growth', 'leverage']
# 
#     import jqfactor as jqf
#     factor_data = jqf.get_factor_values(
#         securities=securities,
#         factors=factor_names,
#         start_date=datestr, end_date=datestr
#     )
# 
#     data = pd.concat([factor_data[fn].unstack().to_frame(fn) for fn in factor_data.keys()], axis=1)
#     data.index.names = ['ts_code', 'trade_date']
#     data.reset_index(inplace=True)
#     data['trade_date'] = data['trade_date'].dt.strftime('%Y%m%d').astype(int)
#     data['ts_code'] = data['ts_code'].apply(lambda x: x.replace('.XSHE', '.SZ').replace('.XSHG', '.SH'))
#     logger.info(f'data.shape={data.shape}. Examples:\n{data.head()}')
# 
#     conn, database = jqu.get_conn_data_type(data_type='CNE5',
#                                             **db_config)
#     schema = 'joinquant'
#     table_name = 'CNE5'
#     # upsert_method = dbu.create_upsert_method(db_code=database, schema=schema,
#     #                                          extra_update_fields={'UpdateDateTime': "NOW()"})
# 
#     # conn.execute(f'DELETE FROM "{schema}"."{table_name}" WHERE "DateId"={dateid}')
#     num_rows = data.to_sql(table_name,
#                            con=conn, schema=schema,
#                            if_exists='append', index=False)
# 
#     logger.info(f'{table_name} with shape {data.shape} on dateid={dateid} '
#                 f'persisted into "{database}"."{schema}"."{table_name}" .')
# 
#     return data


def load_all_factor_values(dateid, securities=None,
                           batch_size=40):
    datestr = dtu.dateid_to_datestr(dateid=dateid)
    if securities is None:
        securities = get_all_securities(types=['stock'], date=datestr)
        securities = securities.index.to_list()
    else:
        securities = list(mu.iterable_to_tuple(securities, raw_type='str'))

    if len(securities) == 0:
        return None

    factor_info = jqf.get_all_factors()
    factor_info = factor_info[factor_info['factor']!='price_no_fq']

    factor_data = list()
    for category in factor_info['category'].unique():
        factor_names = list(factor_info[factor_info['category'] == category]['factor'].unique())
        N = len(factor_names)
        logger.info(f'=== Processing category={category} with #factors={N} ===')
        batch_idx = 0
        while True:
            start_idx = batch_idx * batch_size
            end_idx = min((batch_idx + 1) * batch_size, N)
            if N > batch_size:
                logger.info(f'Processing ibatch={batch_idx}, start_idx={start_idx}, end_idx={end_idx}')

            fvs = qtjqu.load_factor_values(
                jq_codes=securities,
                factors=factor_names[start_idx:end_idx],
                start_date=datestr, end_date=datestr
            )#.T.stack()

            factor_data.append(fvs)

            if end_idx == N:
                break
            batch_idx += 1

    factor_data = pd.concat(factor_data, axis=1)
    factor_data.columns.name = None
    factor_data.reset_index(inplace=True)

    factor_data['trade_date'] = factor_data['trade_date'].dt.strftime('%Y%m%d').astype(int)
    factor_data['code'] = factor_data['code'].apply(
        lambda x: x.replace('.XSHE', '.SZ').replace('.XSHG', '.SH')
    )
    factor_data.rename(columns={'code': 'ts_code'}, inplace=True)
    logger.info(f'factor_data.shape={factor_data.shape}. Examples:\n{factor_data.head()}')

    return factor_data


def persist_all_factor_values(dateid,
                              source='VENDOR', destinations='DB',
                              **db_config):
    pkl_gz_file = f'factor_values_{dateid}.pkl.gz'
    if source=='VENDOR':
        factor_values = load_all_factor_values(dateid=dateid)
    elif source=='FC':
        factor_values = pd.read_pickle(pkl_gz_file)
    else:
        raise Exception(f'source={source} not supported in [VENDOR|FC] !')

    factor_info = jqf.get_all_factors()
    factor_info = factor_info[factor_info['factor']!='price_no_fq']

    factors = factor_info['factor'].to_list()
    factors = [f for f in factors if f not in CNE5_FACTORS] + CNE5_FACTORS

    cols = ['trade_date', 'ts_code'] + factors
    factor_values = factor_values[cols]

    for destination in mu.iterable_to_tuple(destinations, raw_type='str'):
        if destination=='FC':
            factor_values.to_pickle(pkl_gz_file, compression='gzip')
            logger.info(f'destination={destination}: {pkl_gz_file}')
        elif destination=='DB':
            data_type = 'FACTOR_VALUE'
            conn, database = qtjqu.get_conn_data_type(data_type=data_type,
                                                      **db_config)
            schema = 'joinquant'
            table_name = 'FactorValue'
            factor_values.to_sql(table_name,
                                 con=conn, schema=schema,
                                 if_exists='append', index=False)

            logger.info(f'{data_type} with shape {factor_values.shape} '
                        f'persisted into "{database}"."{schema}"."{table_name}" .')
        else:
            raise Exception(f'destination={destination} not supported in [FC|DB] !')

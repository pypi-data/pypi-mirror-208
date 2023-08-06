import pandas as pd
import jqfactor as jqf
import qtc.utils.db_utils as dbu
import qtjq.utils as qtjqu
from qtc.ext.logging import set_logger
logger = set_logger()


DATA_TYPE_DB_CONFIG = dict()
CNE5_FACTORS = ['size', 'beta', 'momentum', 'residual_volatility', 'non_linear_size',
                'book_to_price_ratio', 'liquidity', 'earnings_yield', 'growth', 'leverage']


## ONLY for init
def prepare_factor_groups():
    factor_info = jqf.get_all_factors()
    factor_info = factor_info[factor_info['factor']!='price_no_fq']
    factor_info.rename(columns={
        'category': 'GroupCode',
        'category_intro': 'GroupDesc'
    }, inplace=True)

    factor_groups = factor_info[['GroupCode', 'GroupDesc']].drop_duplicates(keep='last')
    factor_groups.sort_values('GroupCode', inplace=True)
    factor_groups['GroupId'] = list(range(1, len(factor_groups) + 1))
    factor_groups['ParentGroupId'] = -1
    factor_groups = factor_groups.append({
        'GroupCode': 'style - CNE5',
        'GroupDesc': '风险因子 - 风格因子 - CNE5',
        'GroupId': len(factor_groups) + 1,
        'ParentGroupId': factor_groups[factor_groups['GroupCode'] == 'style']['GroupId'].values[0]
    }, ignore_index=True)
    factor_groups['SourceId'] = 1

    return factor_groups


## ONLY for init
def persist_factor_groups(factor_groups,
                          **db_config):
    # factor_groups = prepare_factor_groups()

    data_type = 'FACTOR_GROUP'
    conn, database = qtjqu.get_conn_data_type(data_type=data_type,
                                              **db_config)
    schema = 'factor'
    table_name = 'FactorGroup'
    # upsert_method = dbu.create_upsert_method(db_code=database, schema=schema,
    #                                          extra_update_fields={'UpdateDateTime': "NOW()"})

    num_rows = factor_groups.to_sql(table_name,
                                    con=conn, schema=schema,
                                    if_exists='append', index=False)

    logger.info(f'{data_type} with shape {factor_groups.shape} '
                f'persisted into "{database}"."{schema}"."{table_name}" .')

    return factor_groups


## ONLY for init
def prepare_factor_info(**db_config):
    factor_info = jqf.get_all_factors()
    factor_info = factor_info[factor_info['factor'] != 'price_no_fq']
    factor_info.rename(columns={
        'factor': 'FactorCode',
        'factor_intro': 'FactorDesc',
        'category': 'GroupCode',
        'category_intro': 'GroupDesc'
    }, inplace=True)

    factor_info.loc[factor_info['FactorCode'].isin(CNE5_FACTORS), 'GroupCode'] = 'style - CNE5'
    #     factor_info['SourceCode'] = 'JQ'
    factor_info['SourceId'] = 1
    factor_info['FactorId'] = factor_info.apply(
        lambda x: qtjqu.produce_factor_id(source_id=x['SourceId'], factor_code=x['FactorCode'])
        #int(int(str(x['SourceId']).ljust(3,'0')) * 1e6 + hash(x['FactorCode'])%(1e6))
    , axis=1) + list(range(1,len(factor_info)+1))

    sql = 'SELECT "GroupCode","GroupId" FROM "factor"."FactorGroup"'

    conn = qtjqu.get_conn_data_type(data_type='FACTOR_GROUP',
                                    **db_config)
    factor_group_code2id = pd.read_sql(sql=sql, con=conn)

    factor_info = pd.merge(factor_info, factor_group_code2id, on='GroupCode', how='left')

    return factor_info


## ONLY for init use
def persist_factor_info(factor_info,
                        **db_config):
    # factor_info = prepare_factor_info()

    data_type = 'FACTOR_INFO'
    conn, database = qtjqu.get_conn_data_type(data_type=data_type,
                                              **db_config)
    schema = 'factor'
    table_name = 'FactorInfo'
    # upsert_method = dbu.create_upsert_method(db_code=database, schema=schema,
    #                                          extra_update_fields={'UpdateDateTime': "NOW()"})

    cols = ['FactorId','FactorCode','FactorDesc','GroupId','SourceId']
    num_rows = factor_info[cols].to_sql(table_name,
                                        con=conn, schema=schema,
                                        if_exists='append', index=False)

    logger.info(f'{data_type} with shape {factor_info[cols].shape} '
                f'persisted into "{database}"."{schema}"."{table_name}" .')

    return factor_info

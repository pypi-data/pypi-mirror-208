import pytz
import pandas as pd
from datetime import datetime
from typing import List, Optional
from robertcommonio.system.io.mongo import MongoAccessor, MongoConfig, MongoFunc
from bson.codec_options import CodecOptions


def test_mongo_utc():
    #accsss = MongoAccessor(config=MongoConfig('106.15.207.63', 27017, 'gateway', 'gateway@123456', 'iot_engine', None, None, None, True, 'Asia/Shanghai'))
    accsss = MongoAccessor(config=MongoConfig('106.15.207.63', 27017, 'gateway', 'gateway@123456', 'iot_engine', None, None, None))
    records = list(accsss.find('proj_log', {'proj_id': '1', 'create_time_utc': {'$gte': datetime(2023, 4, 3, 6, 6, 0), '$lte': datetime(2023, 4, 3, 6, 7, 0)}}))
    print(records)


def test_mongo_utc1():
    accsss = MongoAccessor(config=MongoConfig('106.15.207.63', 27017, 'gateway', 'gateway@123456', 'iot_engine', None, None, None))
    collection = accsss._get_coll('proj_log')
    # collection = accsss._get_coll('proj_log').with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=pytz.timezone('Asia/Shanghai')))
    records = list(collection.find({'proj_id': '1', 'create_time_utc': {'$gte': datetime(2023, 4, 3, 6, 6, 0), '$lte': datetime(2023, 4, 3, 6, 7, 0)}}))
    print(records)


def load_history_data(start_time: datetime, end_time: datetime, interval: str, point_names: Optional[list] = None) -> pd.DataFrame:
    accessor = MongoAccessor(config=MongoConfig('106.15.207.63', 27017, 'gateway', 'gateway@123456', 'iot_engine', None, None, None))
    result = pd.DataFrame()
    if isinstance(accessor, MongoAccessor):
        query_match = {'time': MongoFunc.get_time_query_match(start_time, end_time, interval)}
        if point_names:
            query_match.update({'name': {'$in': point_names}})

        pipe: List = [{'$match': query_match},  # 过滤数据
                      {'$project': MongoFunc.get_time_projection_match(start_time, interval)},
                      # 修改输⼊⽂档的结构， 如重命名、 增加、 删除字段、 创建计算结果
                      {'$unwind': '$value'},  # 会把数组中的数据分多条数据，数组外公共数据相同
                      {'$sort': {'value.time': 1}},  # 将输⼊⽂档排序后输出
                      {'$match': MongoFunc.get_value_query_match(start_time, end_time, interval)},
                      {'$project': {'name': 1, 'value': '$value.value', 'time': '$value.time'}}
                      ]
        collection = accessor._get_coll('proj_history_data_1').with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=pytz.timezone('Asia/Shanghai')))
        query_df = pd.DataFrame(collection.aggregate(pipe, allowDiskUse=True))
        if not query_df.empty:
            query_df = query_df.set_index(['time', 'name'])
            if not query_df.index.is_unique:
                query_df = query_df[~query_df.index.duplicated(keep='first')]
            result = query_df.unstack().droplevel(level=0, axis=1)
    return result


load_history_data(datetime(2023, 3, 24, 6, 40, 0), datetime(2023, 3, 24, 6, 50, 0), 'm1', ['modbus_0'])
import requests
import json
from sqlalchemy.orm import scoped_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
from sqlalchemy import Column, DateTime, String, text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import INTEGER


master_control_address = ''
size = 100
overflow = 0
recycle = 3600
CmsSession = None
Base = declarative_base()


def init(connection_cms, master_control_url='10.162.68.14:8080'):
    global master_control_address
    global CmsSession
    master_control_address = master_control_url
    engine_cms = create_engine(
        connection_cms, pool_size=size, max_overflow=overflow, pool_recycle=recycle)
    # Session.configure(bind=engine)
    session_factory_cms = sessionmaker(bind=engine_cms)
    CmsSession = scoped_session(session_factory_cms)


def get_gear_teeth(wind_farm, turbine):
    try:
        box_name = '齿轮箱高速输出轴径向'
        box_shaft_dict = {}
        box_shaft_list = get_part_attribute(wind_farm, turbine, box_name)
        box_shaft_dict['齿轮箱'] = box_shaft_list[1]
        box_freq_dict = get_fault_frequency_by_map(box_shaft_dict)
        gear_teeth = box_freq_dict['高速级啮合频率'] / box_freq_dict['高速轴转频']
        return gear_teeth
    except:
        return None


# 故障频率表
class FaultFrequency(Base):
    __tablename__ = 'cms_fault_frequency'
    id = Column(INTEGER(11), primary_key=True, comment='主键自增')
    part_attribute_name = Column(String(50), comment="部件类型名")
    part_ascription = Column(String(50), comment="所属部件名")
    fault_type = Column(String(50), comment="故障类型信息")
    fault_frequency = Column(Float, comment="故障频率")
    create_time = Column(DateTime, server_default=text(
        "CURRENT_TIMESTAMP"), comment='创建时间')
    update_time = Column(DateTime, server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='修改时间')

    def __init__(self, part_attribute_name, part_ascription, fault_type, fault_frequency):
        self.part_attribute_name = part_attribute_name
        self.part_ascription = part_ascription
        self.fault_type = fault_type
        self.fault_frequency = fault_frequency


def get_csm_brand(pinyin_code, turbine_num, df_turbine):
    r = df_turbine[(df_turbine['pinyin_code'] == pinyin_code) &
                   (df_turbine['inner_turbine_name'] == turbine_num)]
    if isinstance(r, pd.DataFrame) and (len(r) > 0):
        cms_brand = r['cmsBrand'].iloc[0]
    else:
        cms_brand = None
    return cms_brand


def get_part_attribute(farm_code, turbine_name, point_name):
    url = "http://" + master_control_address + "/cms/getBelongPart"
    headers = {'content-type': 'application/json', 'Connection': 'close'}
    request_data = {"pinyinCode": farm_code,
                    "innerTurbineName": turbine_name, "pointName": point_name}
    res = requests.get(url, params=request_data, headers=headers)
    if res.status_code == 200:
        data = json.loads(res.text)["data"]
        if len(data) > 0:
            part_name = data[0]["part_name"]
            part_attribute_value = data[0]["part_attribute_value"]
            return part_name, part_attribute_value
        else:
            part_name = ''
            part_attribute_value = ''
            return part_name, part_attribute_value
    else:
        part_name = ''
        part_attribute_value = ''
        return part_name, part_attribute_value


# 根据部件集合查询故障频率
def get_fault_frequency_by_map(part_dict):
    fault_frequencys_list = list()
    for part_ascription, part_attribute_name in part_dict.items():
        fault_frequencys = get_fault_frequency(
            part_ascription, part_attribute_name)
        fault_frequencys_list.extend(fault_frequencys)
    if len(fault_frequencys_list) > 0:
        freq_dict = {
            frequency.fault_type: frequency.fault_frequency for frequency in fault_frequencys_list}
        return freq_dict
    else:
        return None


# 根据所属部件查询故障频率
def get_fault_frequency(part_ascription, part_attribute_name):
    session = CmsSession()
    try:
        fault_frequemcys = session.query(FaultFrequency)
        if part_ascription:
            fault_frequemcys = fault_frequemcys.filter_by(
                part_ascription=part_ascription)
        if part_attribute_name:
            fault_frequemcys = fault_frequemcys.filter_by(
                part_attribute_name=part_attribute_name)
        fault_frequemcys = fault_frequemcys.all()
        return fault_frequemcys
    except Exception as e:
        print(str(e))
        session.rollback()
    finally:
        session.close()

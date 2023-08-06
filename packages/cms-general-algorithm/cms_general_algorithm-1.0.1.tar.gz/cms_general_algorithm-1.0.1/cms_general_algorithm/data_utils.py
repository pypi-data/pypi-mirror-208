import pandas as pd
from sanydata import datatools
# import sqlmanage.cms_cloud_service as scc
# import sqlmanage.part_service as sps
import cms_general_algorithm.common as cmm
import cms_general_algorithm.frequncy as cfr


need_columns = ["file_path", "data_time", "sample_fre", "turbine",
                             "point_name", "rms", "kurtosis", 'data_valid', 'rms_vdi', 'speed']


class DataUtils(object):
    def __init__(self, logger=None, wf=None, stub='cloud-data-service-test.sanywind.net:50051'):
        self.es = datatools.EsHandler()
        self.dt = datatools.DataTools()
        self.stub = stub
        self.logger = logger
        if wf is not None:
            self.wf = wf
        else:
            self.wf = datatools.WindFarmInf()

    def get_data_df(self, url):
        '''
        @param url:   数据url
        @return:      数据dataframe，如未获取到，返回None
        从url获取数据
        '''
        return self.dt.get_data(self.stub, [url])

    def get_esfiles(self, windfarm, turbine=None,  start_time=None, end_time=None,
                    data_type='cms', need_columns=need_columns, filter_valid=True,
                    sort_values=True, **kwargs):
        '''
        封装了一下es.get_model_tag。并简单处理
        @param windfarm:   风场
        @param turbine:    风机
        @param start_time: 开始日期"%Y-%m-%d"
        @param end_time:   结束日期"%Y-%m-%d"
        @return:           数据dataframe，如未获取到，返回None
        默认执行如下操作：
            cms数据类型,
            处理时间和采样频率格式，并默认对时间排序。采用频率有的为字符串，有的为数字，需要统一处理一下
            保留df['data_valid'] != 0的有效数据
            默认的列为：["file_path", "data_time", "sample_fre", "turbine", "point_name", "rms", "kurtosis", 'data_valid', 'rms_vdi', 'speed']
        其他es.get_model_tag的参数通过kwargs传入
        '''
        df = self.es.get_model_tag(windfarm, turbine, data_type, start_time=start_time,
                                   end_time=end_time, columns=need_columns, **kwargs)
        if isinstance(df, pd.DataFrame) and (len(df) > 0):
            if filter_valid:
                df = df[df['data_valid'] != 0]
            df['sample_fre'] = pd.to_numeric(df['sample_fre'])
            df['data_time'] = pd.to_datetime(
                df['data_time']).dt.floor('s').dt.tz_localize(None)
            if sort_values:
                df.sort_values('data_time', inplace=True)
            return df
        else:
            return None

    def get_cms_fault_parameter(self, windfarm, turbine, measuring_point=None):
        '''
        获取风机的故障频率基础信息
        @param windfarm:          风场
        @param turbine:           风机
        @param measuring_point:   测点名
        @return:                  故障频率，并网转速，额定转速，风机类型
        component_freq_dict
        '''
        try:
            component_dict = {}
            component_list = cmm.get_part_attribute(
                windfarm, turbine, measuring_point)
            component_dict[component_list[0]] = component_list[1]
            component_freq_dict = cmm.get_fault_frequency_by_map(
                component_dict)
        except:
            component_freq_dict = None
            if self.logger is not None:
                self.logger.info('数据库中无信息', windfarm, turbine,
                                 'get_cms_fault_parameter')

        try:
            grid_speed = self.wf.get_speed_by_turbine(
                windfarm, turbine)['grid_speed'][0]
            rated_speed = self.wf.get_speed_by_turbine(
                windfarm, turbine)['rated_speed'][0]

            turbine_type = self.wf.get_type_by_turbine(windfarm, turbine)
        except:
            grid_speed = None
            rated_speed = None
            turbine_type = None
            if self.logger is not None:
                self.logger.info('数据库中无信息', windfarm, turbine,
                                 'get_cms_fault_parameter')
        return component_freq_dict, grid_speed, rated_speed, turbine_type

    def get_components_info(self, windfarm, turbine, measuring_point=None):
        '''
        获取测点部件信息
        @param windfarm:          风场
        @param turbine:           风机
        @param measuring_point:   测点名
        @return:                  测点部件信息
        '''
        return cmm.get_part_attribute(windfarm, turbine, measuring_point)

    def get_csm_brand(self, windfarm, turbine):
        '''
        获取cms厂家
        @param windfarm:          风场
        @param turbine:           风机
        @return:                  CMS厂家
        '''
        wf1 = self.wf.df_wind_farm_turbine
        r = wf1[(wf1['pinyin_code'] == windfarm) & (
            wf1['inner_turbine_name'] == turbine)]
        if isinstance(r, pd.DataFrame) and (len(r) > 0):
            cms_brand = r['cmsBrand'].iloc[0]
        else:
            cms_brand = None
        return cms_brand

    def get_speed_correct(self, signal, frequency, windfarm, turbine):
        '''
        通过信号，校正转速，一般适用于发电机
        @param signal:            信号
        @param frequency:         信号采样频率
        @param windfarm:          风场
        @param turbine:           风机
        @return:                  校正后转速
        '''
        freq_dict, grid_speed, rated_speed, model = self.get_cms_fault_parameter(
            windfarm, turbine)
        gear_teeth = cmm.get_gear_teeth(windfarm, turbine)

        def get_spectrum_signal(data, start, end, threshold=5):
            # 信噪比10lg(s/n)
            df = data[(data['xf2'] >= start) & (data['xf2'] <= end)]
            index = df['yf2'].idxmax()
            xf2 = df.loc[index, 'xf2']
            yf2 = df.loc[index, 'yf2']
            rms = cfr.get_rms(df['yf2'])
            if yf2 > (threshold * rms):
                return xf2, yf2, rms
            else:
                return None, None, rms
        amp, fre = cfr.fft(signal, frequency)
        data = pd.DataFrame({'xf2': pd.Series(fre), 'yf2': pd.Series(amp)})
        fre_low = (grid_speed - 200) / 60
        fre_high = (rated_speed + 200) / 60
        xf2, yf2, rms = get_spectrum_signal(data, fre_low, fre_high, 5)
        if xf2 is not None:
            if gear_teeth is not None:
                fre_low = xf2 * gear_teeth - 60
                fre_high = xf2 * gear_teeth + 60
                xf_t, yf_t, rms_t = get_spectrum_signal(
                    data, fre_low, fre_high, 3)
                if xf_t is not None:
                    return xf2 * 60
                else:
                    return None
            else:
                return xf2 * 60
        else:
            return None

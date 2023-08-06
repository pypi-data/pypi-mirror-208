import json
import os
import re
import sys
import time
import numpy as np
import pandas as pd
import requests
import urllib3
from azure.storage.blob import BlobServiceClient
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from datetime import timedelta

pd.options.mode.chained_assignment = None
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DataAccess:
    def __init__(self, userid, url, connection_string, container_name):
        self.userid = userid
        self.url = url
        self.connection_string = connection_string
        self.container_name = container_name

    def get_caliberation(self, device_id, metadata, df,onpremise=False):
        """
        :param metadata:
        :param df: Dataframe
        :param device_id: string
        :return: Calibrated dataframe

        Perform cal on original data
             y = mx + c
             if y is greater than max value replace y with max value
             if y is less than min value replace y with min value

        """
        sensor_name_list = list(df.columns)
        sensor_name_list.remove('time')
        if "(" not in sensor_name_list[0]:
            sensor_id_list = sensor_name_list
        else:
            sensor_id_list = [s[s.rfind("(") + 1:s.rfind(")")] for s in sensor_name_list]

        if len(metadata) == 0:
            metadata = DataAccess.get_device_metadata(self, device_id,onpremise=onpremise)
        data = metadata['params']

        for (value1, value2) in zip(sensor_id_list, sensor_name_list):
            df_meta = pd.DataFrame(data[str(value1)])
            df_meta = df_meta.set_index('paramName').transpose()

            if 'm' in df_meta.columns and 'c' in df_meta.columns:
                m = float(df_meta.iloc[0]['m'])
                c = int(str(df_meta.iloc[0]['c']).replace(',',''))

                df[str(value2)] = df[str(value2)].replace('BAD 255', '-99999').replace('-', '99999').replace(
                    'BAD undefined', '-99999').replace('BAD 0', '-99999').replace('true',True).replace('false',False)

                df[str(value2)] = df[str(value2)].astype('float')
                df[str(value2)] = (df[str(value2)] * m) + c
                if 'min' in df_meta.columns:
                    min = int(df_meta.iloc[0]['min'])
                    df[str(value2)] = np.where(df[str(value2)] <= min, min, df[str(value2)])
                if 'max' in df_meta.columns:
                    max = int(str(df_meta.iloc[0]['max']).replace('-', '99999').replace(
                        '1000000000000000000000000000', '99999').replace('100000000000', '99999'))
                    df[str(value2)] = np.where(df[str(value2)] >= max, max, df[str(value2)])
        return df

    def get_device_metadata(self, device_id,onpremise=False):
        """

        :param device_id: string
        :return: Json

         Every detail related to a particular device like device added date, calibration values, sensor details etc

        """
        try:
            if str(onpremise).lower() == 'true':
                url = "http://" + self.url + "/api/metaData/device/" + device_id
            else:
                url = "https://" + self.url + "/api/metaData/device/" + device_id
            header = {'userID': self.userid}
            payload = {}
            response = requests.request('GET', url, headers=header, data=payload, verify=False)

            if response.status_code != 200:
                raw = json.loads(response.text)
                raise ValueError(raw['error'])
            else:
                raw_data = json.loads(response.text)['data']
                return raw_data

        except Exception as e:
            print('Failed to fetch device Metadata')
            print(e)

    def get_sensor_alias(self, device_id, df, raw_metadata,onpremise=False):
        """

        :param raw_metadata: json of device metadata
        :param device_id: string
        :param df: Dataframe
        :return: dataframe with columns having sensor alias

        Maps sensor_alias/ sensor name with corresponding sensor ID
        replaces column names with sensor_alias_sensor_id

        """
        sensors = list(df.columns)
        sensors.remove('time')
        if len(raw_metadata) == 0:
            raw_metadata = DataAccess.get_device_metadata(self, device_id,onpremise=onpremise)
        sensor_spec = 'sensors'
        sensor_param_df = pd.DataFrame(raw_metadata[sensor_spec])
        for sensor in sensors:
            sensor_param_df1 = sensor_param_df[sensor_param_df['sensorId'] == sensor]
            if len(sensor_param_df1) != 0:
                sensor_name = sensor_param_df1.iloc[0]['sensorName']
                sensor_name = sensor_name + " (" + sensor + ")"
                df.rename(columns={sensor:sensor_name},inplace=True)
        return df, raw_metadata

    def time_grouping(self, df, bands,compute=None):
        """

        :param df: DataFrame
        :param bands: 05,1W,1D
        :return: Dataframe

        Group time series DataFrame
        Example: The values in Dataframe are at 30s interval we can group and change the 30s interval to 5 mins, 10 mins, 1 day or 1 week.
        The resultant dataframe contains values at given interval.
        """

        df['Time'] = pd.to_datetime(df['time'])
        df.sort_values("Time", inplace=True)
        df = df.drop(['time'], axis=1)
        df = df.set_index(['Time'])
        df.index = pd.to_datetime(df.index)
        if compute is None:
            df = df.groupby(pd.Grouper(freq=str(bands) + "Min")).mean()
        else:
            df = df.groupby(pd.Grouper(freq=str(bands) + "Min")).apply(compute)
        df.reset_index(drop=False, inplace=True)
        return df

    def get_cleaned_table(self, df):
        """

        :param df: Raw Dataframe
        :return: Pivoted DataFrame

        The raw dataframe has columns like time, sensor, values.
        The resultant dataframe will be time sensor alias - sensor id along with their corresponding values

        """

        df = df.sort_values('time')
        df.reset_index(drop=True, inplace=True)
        results = df.pivot(index='time', columns='sensor', values='value')
        results.reset_index(drop=False, inplace=True)
        return results

    def get_device_details(self,onpremise=False):
        """

        :return: Details Device id and Device Name of a particular account

        Dataframe with columne device ids and device names.

        """
        try:
            if str(onpremise).lower() == 'true':
                url = "http://" + self.url + "/api/metaData/allDevices"
            else:
                url = "https://" + self.url + "/api/metaData/allDevices"
            header = {'userID': self.userid}
            payload = {}
            response = requests.request('GET', url, headers=header, data=payload, verify=False)

            if response.status_code != 200:
                raw = json.loads(response.text)
                raise ValueError(raw['error'])
            else:
                raw_data = json.loads(response.text)['data']
                df_raw = pd.DataFrame(raw_data)
                return df_raw

        except Exception as e:
            print('Failed to fetch device Details')
            print(e)

    def get_dp(self, device_id, sensors=None, n=1, cal=True, end_time=datetime.now(),alias=True, IST=True,onpremise=False):
        """

        :param device_id: string
        :param sensors: IST of sensors
        :param n: number of data points (default: 1)
        :param cal: bool (default: True)
        :param end_time: 'YYYY:MM:DD HH:MM:SS'
        :param IST: bool (default: True) Indian Standard Timezone
        :return: Dataframe with values

        Get Data Point fetches data containing values of last n data points of given sensor at given time.

        """
        try:

            metadata = {}
            if sensors == None:
                metadata = DataAccess.get_device_metadata(self, device_id,onpremise=onpremise)
                data_sensor = metadata['sensors']
                df_sensor = pd.DataFrame(data_sensor)
                sensor_id_list = list(df_sensor['sensorId'])
                sensors = sensor_id_list

            end_time = pd.to_datetime(end_time)
            if IST:
                end_time = end_time - timedelta(hours=5, minutes=30)
            else:
                if end_time == datetime.now:
                    end_time=datetime.now(timezone.utc)
            end_time = int(round(end_time.timestamp()))
            if type(sensors) == list:
                len_sensors = len(sensors)
                if len_sensors == 0:
                    raise Exception('Message: No sensors provided')
                if n < 1:
                    raise ValueError('Incorrect number of data points')
                n = int(n) * len_sensors
                delimiter = ","
                sensor_values = delimiter.join(sensors)
            else:
                raise Exception('Message: Incorrect type of sensors')
            header = {}
            cursor = {'end': end_time, 'limit': n}
            payload = {}
            df = pd.DataFrame()
            counter = 0
            while True:
                for record in range(counter):
                    sys.stdout.write('\r')
                    sys.stdout.write("Approx Records Fetched %d" % (10000 * record))
                    sys.stdout.flush()
                if str(onpremise).lower() == "true":
                    url = "http://" + self.url + "/api/apiLayer/getLimitedDataMultipleSensors/?device=" + device_id + "&sensor=" + sensor_values + "&eTime=" + str(
                        cursor['end']) + "&lim=" + str(cursor['limit']) + "&cursor=true"
                else:
                    url = "https://" + self.url + "/api/apiLayer/getLimitedDataMultipleSensors/?device=" + device_id + "&sensor=" + sensor_values + "&eTime=" + str(
                    cursor['end']) + "&lim=" + str(cursor['limit']) + "&cursor=true"
                response = requests.request("GET", url, headers=header, data=payload)
                raw = json.loads(response.text)
                if response.status_code != 200:
                    raise ValueError(response.status_code)
                if 'success' in raw:
                    raise ValueError(raw)
                else:
                    raw_data = json.loads(response.text)['data']
                    cursor = json.loads(response.text)['cursor']
                    if len(raw_data) != 0:
                        df = pd.concat([df, pd.DataFrame(raw_data)])
                    counter = counter + 1
                if cursor['end'] is None:
                    break
            if len(df) != 0:
                if IST:
                    df['time'] = pd.to_datetime(df['time'], utc=False)
                    df['time'] = df['time'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
                if str(alias).lower() == "true":
                    df, metadata = DataAccess.get_sensor_alias(self, device_id, df, metadata,onpremise=onpremise)
                df = DataAccess.get_cleaned_table(self, df)
                if str(cal).lower() == 'true':
                    df = DataAccess.get_caliberation(self, device_id, metadata, df,onpremise=onpremise)
            return df
        except Exception as e:
            print(e)

    def fetch_data(self, device_id,start_time, end_time=datetime.now(), alias=True,sensors=None, echo=True,onpremise=False,IST=True):
        """
        Fetch data from influxdb using apis in given timeslot
        """
        metadata = {}
        if sensors is None:
            metadata = DataAccess.get_device_metadata(self, device_id,onpremise=onpremise)
            data_sensor = metadata['sensors']
            df_sensor = pd.DataFrame(data_sensor)
            sensor_id_list = list(df_sensor['sensorId'])
            sensors = sensor_id_list

        rawdata_res = []
        temp = ''
        try:
            end_time = datetime.strptime(str(end_time), '%Y-%m-%d %H:%M:%S')
        except Exception:
            if type(end_time) == str:
                end_time = str(end_time) + " 23:59:59"
            pass
        s_time = pd.to_datetime(start_time)
        e_time = pd.to_datetime(end_time)
        if IST:
            s_time = s_time - timedelta(hours=5, minutes=30)
            e_time = e_time - timedelta(hours=5, minutes=30)
        st_time = int(round(s_time.timestamp())) * 10000
        en_time = int(round(e_time.timestamp())) * 10000
        header = {}
        payload = {}
        counter = 0
        cursor = {'start': st_time, 'end': en_time}
        while True:
            if echo:
                for record in range(counter):
                    sys.stdout.write('\r')
                    sys.stdout.write("Approx Records Fetched %d" % (10000 * record))
                    sys.stdout.flush()
            if sensors is not None:
                if str(onpremise).lower() == 'true':
                    url_api = "http://" + self.url + "/api/apiLayer/getAllData?device="
                else:
                    url_api = "https://" + self.url + "/api/apiLayer/getAllData?device="
                if counter == 0:
                    str1 = ","
                    sensor_values = str1.join(sensors)
                    temp = url_api + device_id + "&sensor=" + sensor_values + "&sTime=" + str(
                        st_time) + "&eTime=" + str(
                        en_time) + "&cursor=true&limit=50000"
                else:
                    str1 = ","
                    sensor_values = str1.join(sensors)
                    temp = url_api + device_id + "&sensor=" + sensor_values + "&sTime=" + str(
                        cursor['start']) + "&eTime=" + str(cursor['end']) + "&cursor=true&limit=50000"

            response = requests.request("GET", temp, headers=header, data=payload)
            raw = json.loads(response.text)
            if response.status_code != 200:
                raise ValueError(raw['error'])
            if 'success' in raw:
                raise ValueError(raw['error'])

            else:
                raw_data = json.loads(response.text)['data']
                cursor = json.loads(response.text)['cursor']
                if len(raw_data) != 0:
                    rawdata_res = rawdata_res + raw_data
                counter = counter + 1
            if cursor['start'] is None or cursor['end'] is None:
                break

        df = pd.DataFrame(rawdata_res)
        if len(df) != 0:
            if IST:
                df['time'] = pd.to_datetime(df['time'], utc=False)
                df['time'] = df['time'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
            if len(df.columns) == 2:
                df['sensor'] = sensors[0]
            if str(alias).lower() == "true":
                df, metadata = DataAccess.get_sensor_alias(self, device_id, df, metadata,onpremise=onpremise)
            df = DataAccess.get_cleaned_table(self, df)
        return df

    def data_query(self, device_id, sensors,start_time, end_time=str(datetime.now()), alias=True,cal=True, bands=None,onpremise=False,compute=None,IST=True):
        """

        :param device_id: string
        :param start_time: yyyy-MM-dd HH:MM:SS
        :param end_time: yyyy-MM-dd HH:MM:SS
        :param cal: bool
        :param bands: None
        :param IST: bool Indian Time Zone
        :return: df

        If requested data exists in feature store fetch data from the container.
        IF data is not available the data is fetched from influxdb

        """
        try:
            df = pd.DataFrame()
            metadata = {}
            folder_path = f"{device_id}/"
            blob_svc = BlobServiceClient.from_connection_string(conn_str=self.connection_string)
            container_client = blob_svc.get_container_client(self.container_name)
            processed_blobs = [blob.name[len(folder_path):].lstrip("/").rsplit(".", 1)[0].split("-") for blob in
                               container_client.list_blobs(name_starts_with=folder_path)]
            sorted_blobs = sorted(processed_blobs, key=lambda x: (int(x[1]), int(x[0])))

            date_month_list = []
            for month, year in sorted_blobs:
                val = f"{month}-{year}"
                date_month_list.append(val)

            def check_device(device_id):
                flag = False
                blob_list = container_client.list_blobs()
                for blob in blob_list:
                    split_text = blob.name.split('/')
                    if device_id == split_text[0]:
                        flag = True
                return flag

            def get_dates():
                temp_list = []
                match_start_str = re.search(r'\d{4}-\d{2}-\d{2}', start_time)
                match_end_str = re.search(r'\d{4}-\d{2}-\d{2}', end_time)

                start_t = (datetime.strptime(match_start_str.group(), '%Y-%m-%d').date())
                end_t = (datetime.strptime(match_end_str.group(), '%Y-%m-%d').date())
                curr_date = start_t
                date_list = []
                while curr_date <= end_t:
                    date_list.append(curr_date)
                    curr_date += timedelta(days=1)

                for date_value in date_list:
                    month_value = date_value.month
                    year_value = date_value.year
                    str_format = str(month_value) + '-' + str(year_value)
                    temp_list.append(str_format)

                def sort_dates(dates):
                    def date_key(date_string):
                        return datetime.strptime(date_string, '%m-%Y')
                    return sorted(dates, key=date_key)

                filtered_list = [*set(temp_list)]
                date_range = sort_dates(filtered_list)
                list_of_dates_in_azure = list(set(date_month_list).intersection(date_range))
                return list_of_dates_in_azure

            def read_one(blobfile):
                blob = blob_svc.get_blob_client(self.container_name, device_id + '/' + blobfile + '.parquet')
                with open(blobfile + '.parquet', "wb") as my_blob:
                    blob_data = blob.download_blob()
                    blob_data.readinto(my_blob)
                df = pd.read_parquet(blobfile + '.parquet')
                os.remove(blobfile + '.parquet')
                return df

            def thread_read():
                results = []
                blob_list = get_dates()
                if len(blob_list) !=0:
                    with ThreadPoolExecutor(max_workers=40) as executor:  # function to thread
                        for record in range(len(blob_list)):
                            sys.stdout.write('\r')
                            sys.stdout.write("Please Wait .. ")
                            sys.stdout.flush()
                        results = executor.map(read_one, blob_list)
                    fetched_df = pd.concat(results, axis=0)
                else:
                    fetched_df=pd.DataFrame()
                return fetched_df

            flag = check_device(device_id)
            if flag:
                df = thread_read()
                if len(df) != 0:
                    try:
                        end_time = str(datetime.strptime(str(end_time), '%Y-%m-%d %H:%M:%S'))
                    except Exception:
                        if type(end_time) == str:
                            end_time = str(end_time) + " 23:59:59"
                        pass
                    try:
                        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                        end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
                        df = df[(df['time'] >= start_time) & (df['time'] <= end_time)]
                    except ValueError:
                        df = df[(df['time'] >= start_time) & (df['time'] <= end_time)]
                        pass
                    except Exception as e:
                        print('Message: \t',e)
                    if sensors is None:
                        sensors = list(df.columns)
                        sensors.remove('time')
                    sensor_list_df = list(df.columns)
                    sensor_list_df.remove('time')
                    sensors_filtered = list(set(sensor_list_df).intersection(sensors))
                    if sensors != None and len(sensors_filtered) != 0:
                        sensors_filtered.insert(0,'time')
                        df =  df[sensors_filtered]
                    if len(sensors_filtered) == 0:
                        df = pd.DataFrame()
                    df.reset_index(drop=True, inplace=True)
                    last_date = df['time'].iloc[len(df) - 1]
                    start_date = last_date.date() + timedelta(days=1)
                    end_time = pd.to_datetime(end_time)
                    if last_date.date() != end_time.date():
                        df1 = DataAccess.fetch_data(self, device_id ,start_time=str(start_date), alias=False,end_time=end_time,sensors=sensors, echo=True,onpremise=False,IST=True)
                        df = pd.concat([df, df1])
                    else:
                        df1 = DataAccess.fetch_data(self, device_id,start_time=str(last_date), alias=False,end_time=end_time,sensors=sensors, echo=True,onpremise=False,IST=True)
                        df = pd.concat([df, df1])
                    df.reset_index(drop=True, inplace=True)
            else:
                df_devices = DataAccess.get_device_details(self,onpremise=onpremise)
                device_list = df_devices['devID'].tolist()
                if device_id in device_list:
                    df = DataAccess.fetch_data(self, device_id, start_time,end_time, alias,sensors=sensors,echo=True,onpremise=onpremise,IST=IST)
                else:
                    raise Exception('Message: Device not added in account')
            if len(df) != 0:
                if str(alias).lower() == "true":
                    df,metadata = DataAccess.get_sensor_alias(self,device_id,df,metadata,onpremise=onpremise)

                if str(cal).lower() == 'true':
                    df = DataAccess.get_caliberation(self, device_id, metadata, df,onpremise=onpremise)
                if bands is not None:
                    df = DataAccess.time_grouping(self, df, bands,compute)
                df = df.set_index(['time'])
                df = df.fillna(value=np.nan)
                df.dropna(axis=0, how='all', inplace=True)
                df.reset_index(drop=False, inplace=True)
                df.drop_duplicates(inplace=True)
                if IST == False:
                    df['time'] = pd.to_datetime(df['time']) - timedelta(hours=5,minutes=30)
            return df
        except Exception as e:
            print(e)
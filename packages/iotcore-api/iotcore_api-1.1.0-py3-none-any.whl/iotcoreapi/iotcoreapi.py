"""
iotcoreapi
Class definition
"""
import datetime
import json
import logging
from functools import wraps

import pandas
import pandas as pd
import requests
import urllib3
from pandas import json_normalize
from iotcoreapi.exceptions import IotCoreAPIException
import warnings
import re

from iotcoreapi.nan_treatment import nan_treatment


class IoTCoreAPI:
    @staticmethod
    def _warnings_and_json_wrapper(func):
        """Decorator including InsecureRequestWarning and then JSON() format"""

        def f(*args, **kwargs):
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            rv = func(*args, **kwargs)
            if rv.status_code == 200:
                return rv.json()
            else:
                raise IotCoreAPIException(rv)

        return f

    @staticmethod
    def _no_row_limit_decorator(fnc):
        """Decorator to remove row limit in post methods"""

        @wraps(fnc)
        def wrapper(*args, **kwargs):
            NX = args[0]
            df_nexus = args[1]
            n = len(df_nexus)
            if n > 49999:
                iter = round(n / 49999)
                for j in range(iter):
                    ini = j * 49999
                    fin = (j + 1) * 49999
                    if fin < n:
                        df_nexus_write = df_nexus[ini:fin]
                    else:
                        df_nexus_write = df_nexus[ini:n]
                    response = fnc(NX, df_nexus_write)
            else:
                response = fnc(NX, df_nexus)
            return response

        return wrapper

    def _convert_response(self, response: dict | list[dict], output_format: str,
                          time_format: str = None, nan_method: str = None) -> pd.DataFrame | dict | list[dict]:
        """
        Auxiliary function to transform response in json format to dataframe if indicated in output_format arg.
        Args:
            response: json
            output_format: 'dataframe' or 'json'
            time_format: 'datetime' or 'unix'
            nan_method: method used to drop NaNs. None or 'interpolate', 'bfill', 'ffill', 'mean', 'zerofill'. Only valid for 'dataframe' output_format

        Returns:
            response: json or dataframe
        """
        if output_format == 'dataframe':
            if response:
                response = self._json_normalize_check(response)
                if time_format == 'datetime':
                    response['timeStamp'] = pd.to_datetime(response.timeStamp, unit='s', utc=True)
                if nan_method is not None:
                    response = nan_treatment(response, nan_method)
            else:
                response = pd.DataFrame(columns=['timeStamp', 'uid', 'name', 'value'])
        return response

    def __init__(self, ip: str = "localhost", port: int = 56000, token: str = "", version: str | int = "3.0",
                 logger: logging.Logger = None):
        """
        Init method for iotcoreapi. Needs API configuration parameters

        Args:
            ip: IoT Core base endpoint
            port: API Port. Defaults to 56000
            token: API token
            version: 1.0, 2.0 or 3.0. Defaults to 3.0
            logger: Optional. Logger object to output log messages. If not provided, logger messages will be printed to console
        """
        self.ip = ip
        self.port = str(port)
        self.token = token
        # Check verson number
        version_regex = r'^\d+\.\d+$'
        if not bool(re.match(version_regex, version)):
            raise ValueError('Version number does not match correct format. Should be "1.0", "2.0"...')
        self.version = version
        self._version_number = float(version)
        self._time_formats = ['datetime', 'unix']
        self._output_formats = ['dataframe', 'json']
        self.url_NX = "http://" + ip + ":" + str(port)
        self.header = {
            "nexustoken": self.token,
            "nexusapiversion": self.version,
            "Content-Type": "application/json",
        }
        self.logger = logger
        self._log_print("Created new instance of IoTCoreAPI")

    def _log_print(self, message, severity='info'):
        if self.logger is not None:
            if severity == 'info':
                self.logger.info(message)
            elif severity == 'error':
                self.logger.error(message)
            elif severity == 'debug':
                self.logger.debug(message)
            elif severity == 'warning':
                self.logger.warning(message)
            else:
                raise ValueError('Severity not supported')
        else:
            print(message)

    def _json_normalize_check(self, response: dict | list[dict]) -> pd.DataFrame:
        """
        Intenta convertir a DataFrame la respuesta en json de la API. Si no es posible, es que ha habido un fallo (la respuesta no sigue el formato establecido)

        Args:
            response: json con valor de la llamada a NexusAPI
        """
        try:
            return json_normalize(response)
        except Exception as e:
            self._log_print(f'IoTCoreAPI communication error. Reason: {e}')
            raise Exception(f'IoTCoreAPI communication error. Reason: {e}')

    @_warnings_and_json_wrapper
    def _getResponse(self, url, params=None):
        """GET method using Request"""
        return requests.get(url, verify=False, params=params, headers=self.header)

    @_warnings_and_json_wrapper
    def _postResponse(self, url, body):
        """POST method using Request"""
        return requests.post(url, verify=False, headers=self.header, data=body)

    # --------- CATALOGUE METHODS -----------------

    def catalogue_tags(self, include_attributes: bool = True, output_format: str = 'dataframe') -> dict | pd.DataFrame:
        """Return all tags available for the token

        Args:
            include_attributes (optional): if version >3.0, bool to return attributes or not
            output_format: Result given in 'dataframe' or 'json'. Defaults to 'dataframe'

        Returns:
            response in json or dataframe
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        url = self.url_NX + "/api/Tags"
        if self._version_number >= 3.0:
            params = {"IncludeAttributes": include_attributes}
        else:
            params = None
        return self._convert_response(self._getResponse(url, params), output_format)

    def catalogue_tags_filtered(self, installations: list | str = None, drivers: list | str = None,
                                tags: list | str = None,
                                attributes: list | str = None,
                                output_format: str = 'dataframe') -> dict | pd.DataFrame:
        """Searching for tags that comply with a certain criteria can be achieved with the filtered route. If fields are empty, all tags are returned.

        Args:
            installations: name of the installations
            drivers: name of drivers
            tags: name of tags
            attributes: not implemented yet
            output_format: Result given in 'dataframe' or 'json'. Defaults to 'dataframe'

        Returns:
            response in json or dataframe
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        if self._version_number < 3:
            raise NotImplementedError('Nexus API version must be greater than 3.0')
        # TODO: El metodo original permitirá filtrar por atributos pero como se desconoce como hacerlo y estamos en depuración de momento dejo solo estas tres opciones
        args = locals()
        parameters = {}
        for key in list(args):
            if args[key] is None:
                parameters[key] = []
            elif isinstance(args[key], str):
                parameters[key] = [args[key]]
            else:
                parameters[key] = args[key]
        body = json.dumps(
            {"SearchByInstallationName": parameters['installations'], "SearchByDriverName": parameters['drivers'],
             "SearchByTagName": parameters['tags']})
        url = self.url_NX + "/api/Tags/filtered"
        response = self._postResponse(url, body)
        return self._convert_response(response, output_format)

    def catalogue_tags_attributes(self, output_format: str = 'dataframe') -> dict | pd.DataFrame:
        """Obtaining the list of possible attributes within the system and, when limited to a set of values, the list of possible values

        Args:
            output_format: Result given in 'dataframe' or 'json'. Defaults to 'dataframe'

        Returns:
            response in json or dataframe
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        if self._version_number < 3:
            raise NotImplementedError('Nexus API version must be greater than 3.0')
        url = self.url_NX + "/api/Tags/Attributes"
        response = self._getResponse(url)
        return self._convert_response(response, output_format)

    def catalogue_tags_writable(self, output_format: str = 'dataframe') -> dict | pd.DataFrame:
        """Return tags available for writing. If version is under 3.0, returned array does not have attribute information

        Args:
            output_format: Result given in 'dataframe' or 'json'. Defaults to 'dataframe'

        Returns:
            response in json
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        url = self.url_NX + "/api/Tags/writable"
        response = self._getResponse(url)
        return self._convert_response(response, output_format)

    def catalogue_documents(self, output_format: str = 'dataframe') -> dict | pd.DataFrame:
        """Returns all tagviews shared in the token

        Args:
            output_format: Result given in 'dataframe' or 'json'. Defaults to 'dataframe'

        Returns:
            response in json
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        url_completa = self.url_NX + "/api/Documents"
        response = self._getResponse(url_completa)
        return self._convert_response(response, output_format)

    def catalogue_tagview_detail(self, uid: str, output_format: str = 'dataframe') -> dict | pd.DataFrame:
        """Return all variables from a given tagview

        Args:
            uid: uid of the tagview
            output_format: Result given in 'dataframe' or 'json'. Defaults to 'dataframe'

        Returns:
            response in json
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        url = self.url_NX + "/api/Documents/tagviews/" + uid
        response = self._getResponse(url)
        if output_format == 'dataframe':
            if response:
                response = self._json_normalize_check(response['columns'])
        return response

    def catalogue_alarms(self, group_uid: str = None, output_format: str = 'dataframe') -> list[dict] | pd.DataFrame:
        """Returns information of the alarms in the token

        Args:
            group_uid : Optional. Uid of the group to list. If the group uid is indicated, the list only contains the alarms that belong directly to the group (no digging down in the hierarchy)
            output_format : Result given in 'dataframe' or 'json'. Defaults to 'dataframe'

        Returns:
            response in json or dataframe
            """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        if self._version_number < 2:
            raise NotImplementedError('Version 1.0 does not support alarm methods')
        params = {'GroupUid': group_uid}
        url_completa = self.url_NX + "/api/Alarms"
        response = self._getResponse(url_completa, params)
        return self._convert_response(response, output_format)

    def catalogue_alarm_groups(self, output_format: str = 'dataframe') -> list[dict] | pd.DataFrame:
        """Returns information of the alarm groups in the token

        Args:
            output_format : Result given in 'dataframe' or 'json'. Defaults to 'dataframe'

        Returns:
            response in json
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        if self._version_number < 2:
            raise NotImplementedError('Version 1.0 does not support alarm methods')
        url_completa = self.url_NX + "/api/Alarms/Groups"
        response = self._getResponse(url_completa)
        return self._convert_response(response, output_format)

    # -------- READING OPERATIONS --------

    def read_tags_realtime(self, tags_uids: list[str], output_format: str = 'dataframe',
                           time_format='datetime', nan_method: str = None) -> pd.DataFrame | list[dict]:
        """Reads real time value of the tags provided in the array tags_uids

        Args:
            tags_uids : list with uids of the tags
            output_format : Result given in 'dataframe' or 'json'. Defaults to 'dataframe'
            time_format : 'datetime' or 'unix' if output_format is dataframe. Defaults to datetime
            nan_method: method used to drop NaNs. None or 'interpolate', 'bfill', 'ffill', 'mean', 'zerofill'. Only valid for 'dataframe' output_format

        Returns:
            response in json or dataframe
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        if time_format not in self._time_formats:
            raise ValueError(f'time_format must be in {self._time_formats}')
        body = json.dumps(tags_uids)
        url = self.url_NX + "/api/Tags/realtime"
        response = self._postResponse(url, body)
        response = self._convert_response(response, output_format, time_format, nan_method)
        return response

    def read_tagview_realtime(self, uid: str, uids_tags: list[str] = None,
                              output_format: str = 'dataframe',
                              time_format='datetime', nan_method: str = None) -> pd.DataFrame | list[dict]:
        """Returns real time value for the uids variables provided in a given tagview

        Args:
            uid : uid of the tagview
            uids_tags : list of uids
            output_format : Result given in 'dataframe' or 'json'. Defaults to 'dataframe'
            time_format : 'datetime' or 'unix' if output_format is dataframe. Defaults to datetime
            nan_method: method used to drop NaNs. None or 'interpolate', 'bfill', 'ffill', 'mean', 'zerofill'. Only valid for 'dataframe' output_format

        Returns:
            response in json or dataframe
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        if time_format not in self._time_formats:
            raise ValueError(f'time_format must be in {self._time_formats}')
        if uids_tags is None:
            uids_tags = []
        body = json.dumps(uids_tags)
        url = self.url_NX + "/api/Documents/tagviews/" + uid + "/realtime"
        response = self._postResponse(url, body)
        response = self._convert_response(response, output_format, time_format, nan_method)
        return response

    def read_tags_historic(self, uids: list[str], start_ts: int | float, end_ts: int | float,
                           data_source: str | int = 'RAW', resolution: str | int = 'RES_1_HOUR',
                           agg_operation: str | int = "LAST_VALUE", output_format: str = 'dataframe',
                           time_format='datetime', nan_method: str = None) -> pd.DataFrame | list[dict]:
        """Obtain historic data of the specified tags

        Args:
            uids: list of unique identifiers of the tags whose values must be obtained.
            start_ts: start time in unix time or datetime
            end_ts: end time in unix time or datetime
            data_source: RAW, STATS_PER_HOUR, STATS_PER_DAY o STATS_PER_MONTH. This parameter indicates the historian section to get the information from, being "RAW" the finest data storage available.
            resolution: RES_10_SEC, RES_30_SEC, RES_1_MIN, RES_5_MIN, RES_15_MIN, RES_1_HOUR, RES_1_DAY, RES_1_MONTH o RES_1_YEAR, this parameter only applies if the datasource is RAW.
            agg_operation: MIN, MAX, AVG, LAST_VALUE, SUM. The operation to be applied to obtain the resolution required. Not mandatory, can be null or empty, then applies LAST_VALUE by default.
            output_format : Result given in 'dataframe' or 'json'. Defaults to 'dataframe'
            time_format : 'datetime' or 'unix' if output_format is dataframe. Defaults to datetime
            nan_method: method used to drop NaNs. None or 'interpolate', 'bfill', 'ffill', 'mean', 'zerofill'. Only valid for 'dataframe' output_format

        Returns:
            response in json or dataframe
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        if time_format not in self._time_formats:
            raise ValueError(f'time_format must be in {self._time_formats}')
        if self._version_number < 3:
            raise NotImplementedError('Nexus API version must be greater than 3.0')
        if len(uids) > 100:
            raise AttributeError('Too many tags. Please set the number of tags less or equal than 100')
        # Convert datetime to TS if needed:
        if isinstance(start_ts, datetime.datetime):
            start_ts = start_ts.timestamp()
        if isinstance(end_ts, datetime.datetime):
            end_ts = end_ts.timestamp()
        body = json.dumps(
            {"uids": uids, "startTs": start_ts, "endTs": end_ts, "dataSource": data_source, "resolution": resolution,
             "aggOperation": agg_operation})
        url = self.url_NX + "/api/Tags/historic"
        response = self._postResponse(url, body)
        response = self._convert_response(response, output_format, time_format, nan_method)
        return response

    def read_tags_rawhistoric(self, uids, start_ts, end_ts, output_format: str = 'dataframe',
                              time_format='datetime', nan_method: str = None) -> pd.DataFrame | list[dict]:
        """To obtain raw data with no aggregation or normalization applied

        Args:
            uids: list of unique identifiers of the tags whose values must be obtained.
            start_ts: start time in unix time or datetime
            end_ts: end time in unix time or datetime
            output_format : Result given in 'dataframe' or 'json'. Defaults to 'dataframe'
            time_format : 'datetime' or 'unix' if output_format is dataframe. Defaults to datetime
            nan_method: method used to drop NaNs. None or 'interpolate', 'bfill', 'ffill', 'mean', 'zerofill'. Only valid for 'dataframe' output_format

        Returns:
            response in json or dataframe
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        if time_format not in self._time_formats:
            raise ValueError(f'time_format must be in {self._time_formats}')
        if self._version_number < 3:
            raise NotImplementedError('Nexus API version must be greater than 3.0')
        # Convert datetime to TS if needed:
        if isinstance(start_ts, datetime.datetime):
            start_ts = start_ts.timestamp()
        if isinstance(end_ts, datetime.datetime):
            end_ts = end_ts.timestamp()
        body = json.dumps({"uids": uids, "startTs": start_ts, "endTs": end_ts})
        url = self.url_NX + "/api/Tags/rawhistoric"
        response = self._postResponse(url, body)
        response = self._convert_response(response, output_format, time_format, nan_method)
        return response

    def read_tags_transient(self, uids: list[str], start_ts: int | float, end_ts: int | float,
                            data_source: str | int = None,
                            resolution: str | int = 'RES_1_SEC',
                            output_format: str = 'dataframe',
                            time_format='datetime', nan_method: str = None) -> pd.DataFrame | list[dict]:
        """
        This method works like "Tags in historical mode", but forces the dataSource to be the transient space. Be
        aware that the maximum period (endTs - startTs) than can be asked for in transient mode is 15 min. Also
        please note that resolutions should be according to the span of time (max 15 mins) so there are new options not available
        for historic.

        Args:
            uids: list of unique identifiers of the tags whose values must be obtained. start_ts:
            start_ts: time in unix time or datetime
            end_ts: end time in unix time or datetime. Timespan must be smaller than 15 mins
            data_source: Can be set to null or empty. Not needed
            resolution: RES_1_SEC, RES_200_MIL, RES_500_MIL, any other option makes no sense with the transient data pool.
            output_format : Result given in 'dataframe' or 'json'. Defaults to 'dataframe'
            time_format : 'datetime' or 'unix' if output_format is dataframe. Defaults to datetime
            nan_method: method used to drop NaNs. None or 'interpolate', 'bfill', 'ffill', 'mean', 'zerofill'. Only valid for 'dataframe' output_format

        Returns:
            response in json or dataframe
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        if time_format not in self._time_formats:
            raise ValueError(f'time_format must be in {self._time_formats}')
        if self._version_number < 3:
            raise NotImplementedError('Nexus API version must be greater than 3.0')
        if len(uids) > 100:
            raise AttributeError('Too many tags. Please set the number of tags less or equal than 100')
        # Convert datetime to TS if needed:
        if isinstance(start_ts, datetime.datetime):
            start_ts = start_ts.timestamp()
        if isinstance(end_ts, datetime.datetime):
            end_ts = end_ts.timestamp()
        body = json.dumps(
            {"uids": uids, "startTs": start_ts, "endTs": end_ts, "resolution": resolution})
        url = self.url_NX + "/api/Tags/transient"
        response = self._postResponse(url, body)
        response = self._convert_response(response, output_format, time_format, nan_method)
        return response

    def read_tagview_historic(self, uid: str, start_ts: datetime.datetime | float | int,
                              end_ts: datetime.datetime | float | int, tags_uids: list[str] = None, data_source='RAW',
                              resolution='RES_1_HOUR', output_format: str = 'dataframe',
                              time_format='datetime', nan_method: str = None) -> pd.DataFrame | list[dict]:
        """Read dataview historic data. It is recommended to use read_dataview_history_text_filters instead.

        Args:
            uid: uid of the tagview
            start_ts: start time in unix or datetime
            end_ts: end time in unix or datetime
            tags_uids (optional): list of unique identifier of the tags whose values must be obtained. If None, will take all tags in tagview
            data_source: RAW, STATS_PER_HOUR, STATS_PER_DAY o STATS_PER_MONTH. This parameter indicates the historian section to get the information from, being "RAW" the finest data storage available.
            resolution: RES_10_SEC, RES_30_SEC, RES_1_MIN, RES_5_MIN, RES_15_MIN, RES_1_HOUR, RES_1_DAY, RES_1_MONTH o RES_1_YEAR, this parameter only applies if the datasource is RAW.
            output_format : Result given in 'dataframe' or 'json'. Defaults to 'dataframe'
            time_format : 'datetime' or 'unix' if output_format is dataframe. Defaults to datetime
            nan_method: method used to drop NaNs. None or 'interpolate', 'bfill', 'ffill', 'mean', 'zerofill'. Only valid for 'dataframe' output_format

        Returns:
            A list of objects or dataframe providing information for the requested tags. Every element in the array corresponds to one of the requested tags associated with one timestamp between the startTs and the endTs.
            """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        if time_format not in self._time_formats:
            raise ValueError(f'time_format must be in {self._time_formats}')
        # Convert datetime to TS if needed:
        if isinstance(start_ts, datetime.datetime):
            start_ts = start_ts.timestamp()
        if isinstance(end_ts, datetime.datetime):
            end_ts = end_ts.timestamp()
        if tags_uids is None:
            tags_uids = []
        body = json.dumps(
            {"uids": tags_uids, "startTs": start_ts, "endTs": end_ts, "dataSource": data_source,
             "resolution": resolution})
        url = self.url_NX + "/api/Documents/tagviews/" + uid + "/historic"
        response = self._postResponse(url, body)
        response = self._convert_response(response, output_format, time_format, nan_method)
        return response

    def read_tagview_historic_text_filters(self, uid_tagview: str, start_ts: datetime.datetime | float | int,
                                           end_ts: datetime.datetime | float | int,
                                           filter_txt: str | list[str] = None, data_source: str = 'RAW',
                                           resolution: str = 'RES_1_HOUR', output_format: str = 'dataframe',
                                           time_format: str = 'datetime', nan_method: str = None) -> pd.DataFrame | list[dict]:
        """
        Read dataview historic data but use text filters instead of uids. Also returns data in dataframe format

        Args:
            uid_tagview: uid of the tagview
            start_ts: start time in unix or datetime
            end_ts: end time in unix or datetime
            filter_txt): text filters to search tags in tagviews. If None, will take all tags in tagview
            data_source: RAW, STATS_PER_HOUR, STATS_PER_DAY o STATS_PER_MONTH. This parameter indicates the historian section to get the information from, being "RAW" the finest data storage available.
            resolution: RES_10_SEC, RES_30_SEC, RES_1_MIN, RES_5_MIN, RES_15_MIN, RES_1_HOUR, RES_1_DAY, RES_1_MONTH o RES_1_YEAR, this parameter only applies if the datasource is RAW.
            output_format : Result given in 'dataframe' or 'json'. Defaults to 'dataframe'
            time_format : Optional. 'datetime' or 'unix'. Defaults to datetime
            nan_method: method used to drop NaNs. None or 'interpolate', 'bfill', 'ffill', 'mean', 'zerofill'. Only valid for 'dataframe' output_format

        Returns:
            filtered_hist (dataframe):
                columns:
                    name: name of tag
                    value: value of tag
                    timeStamp: timeStamp in datatetime or unix time
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        if time_format not in self._time_formats:
            raise ValueError(f'time_format must be in {self._time_formats}')
        # Convert datetime to TS if needed:
        if isinstance(start_ts, datetime.datetime):
            start_ts = start_ts.timestamp()
        if isinstance(end_ts, datetime.datetime):
            end_ts = end_ts.timestamp()
        tagview_info = self.catalogue_tagview_detail(uid_tagview)
        tags_uids = []
        if isinstance(filter_txt, list):
            for filter in filter_txt:
                uids_loop = list(tagview_info[tagview_info['name'].str.contains(filter, case=False)].uid)
                tags_uids.extend(uids_loop)
        else:
            if filter_txt:
                tags_uids = list(tagview_info[tagview_info['name'].str.contains(filter_txt, case=False)].uid)
        # Remove duplicate UIDS
        tags_uids = list(set(tags_uids))
        filtered_hist = self.read_tagview_historic(uid_tagview, start_ts, end_ts, tags_uids, data_source, resolution,
                                                   output_format, time_format, nan_method)
        diccio = dict([(i, j) for i, j in zip(tagview_info.uid, tagview_info.name)])
        if isinstance(filtered_hist, pd.DataFrame):
            filtered_hist['name'] = filtered_hist['uid'].map(diccio)
        else:
            for item in filtered_hist:
                item['name'] = diccio[item['uid']]
        return filtered_hist

    def read_tagview_realtime_text_filters(self, uid_tagview: str,
                                           filter_txt: str | list[str] = None,
                                           output_format: str = 'dataframe',
                                           time_format: str = 'datetime',
                                           nan_method: str = None) -> pd.DataFrame | list[dict]:
        """
        Read dataview realtime data but use text filters instead of uids. Also returns data in dataframe format

        Args:
            uid_tagview: uid of the tagview
            filter_txt: text filters to search tags in tagviews. If None, will take all tags in tagview
            output_format : Result given in 'dataframe' or 'json'. Defaults to 'dataframe'
            time_format : Optional. 'datetime' or 'unix'. Defaults to datetime
            nan_method: method used to drop NaNs. None or 'interpolate', 'bfill', 'ffill', 'mean', 'zerofill'. Only valid for 'dataframe' output_format

        Returns:
            filtered_hist (dataframe):
                columns:
                    name: name of tag
                    value: value of tag
                    timeStamp: timeStamp in datatetime or unix time
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        if time_format not in self._time_formats:
            raise ValueError(f'time_format must be in {self._time_formats}')
        tagview_info = self.catalogue_tagview_detail(uid_tagview)
        tags_uids = []
        if isinstance(filter_txt, list):
            for filter in filter_txt:
                uids_loop = list(tagview_info[tagview_info['name'].str.contains(filter, case=False)].uid)
                tags_uids.extend(uids_loop)
        else:
            if filter_txt:
                tags_uids = list(tagview_info[tagview_info['name'].str.contains(filter_txt, case=False)].uid)
        # Remove duplicate UIDS
        tags_uids = list(set(tags_uids))
        filtered_hist = self.read_tagview_realtime(uid_tagview, tags_uids, output_format, time_format, nan_method)
        diccio = dict([(i, j) for i, j in zip(tagview_info.uid, tagview_info.name)])
        if isinstance(filtered_hist, pd.DataFrame):
            filtered_hist['name'] = filtered_hist['uid'].map(diccio)
        else:
            for item in filtered_hist:
                item['name'] = diccio[item['uid']]
        return filtered_hist

    def read_tags_historic_text_filters(self, uids: list[str], start_ts: datetime.datetime | int | float,
                                        end_ts: datetime.datetime | int | float,
                                        filter_txt: str | list[str] = None, data_source: str | int = 'RAW',
                                        resolution: str | int = 'RES_1_HOUR',
                                        agg_operation: str | int = "LAST_VALUE", output_format: str = 'dataframe',
                                        time_format: str = 'datetime', nan_method: str = None) -> pd.DataFrame | list[dict]:
        """Obtain historic data of the specified tags by name

        Args:
            uids: list of unique identifiers of the tags whose values must be obtained.
            start_ts: start time in unix or datetime
            end_ts: end time in unix or datetime
            filter_txt: text filters to search tags in tagviews. If None, will take all tags in tagview
            data_source: RAW, STATS_PER_HOUR, STATS_PER_DAY o STATS_PER_MONTH. This parameter indicates the historian section to get the information from, being "RAW" the finest data storage available.
            resolution: RES_10_SEC, RES_30_SEC, RES_1_MIN, RES_5_MIN, RES_15_MIN, RES_1_HOUR, RES_1_DAY, RES_1_MONTH o RES_1_YEAR, this parameter only applies if the datasource is RAW.
            agg_operation: MIN, MAX, AVG, LAST_VALUE, SUM. The operation to be applied to obtain the resolution required. Not mandatory, can be null or empty, then applies LAST_VALUE by default.
            output_format : Result given in 'dataframe' or 'json'. Defaults to 'dataframe'
            time_format : Optional. 'datetime' or 'unix'. Defaults to datetime
            nan_method: method used to drop NaNs. None or 'interpolate', 'bfill', 'ffill', 'mean', 'zerofill'. Only valid for 'dataframe' output_format

        Returns:
            response in json
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        if time_format not in self._time_formats:
            raise ValueError(f'time_format must be in {self._time_formats}')
        # Convert datetime to TS if needed:
        if isinstance(start_ts, datetime.datetime):
            start_ts = start_ts.timestamp()
        if isinstance(end_ts, datetime.datetime):
            end_ts = end_ts.timestamp()
        if len(uids) > 100:
            raise AttributeError('Too many tags. Please set the number of tags less or equal than 100')
        tag_info = self.catalogue_tags()
        tags_uids = []
        if isinstance(filter_txt, list):
            for filter in filter_txt:
                uids_loop = list(tag_info[tag_info['name'].str.contains(filter, case=False)].uid)
                tags_uids.extend(uids_loop)
        else:
            if filter_txt:
                tags_uids = list(tag_info[tag_info['name'].str.contains(filter_txt, case=False)].uid)
        # Remove duplicate UIDS
        tags_uids = list(set(tags_uids))
        filtered_hist = self.read_tags_historic(tags_uids, start_ts, end_ts, data_source, resolution, agg_operation,
                                                output_format, time_format, nan_method)
        diccio = dict([(i, j) for i, j in zip(tag_info.uid, tag_info.name)])
        if isinstance(filtered_hist, pd.DataFrame):
            filtered_hist['name'] = filtered_hist['uid'].map(diccio)
        else:
            for item in filtered_hist:
                item['name'] = diccio[item['uid']]
        return filtered_hist

    def read_tags_realtime_text_filters(self,
                                        filter_txt: str | list[str] = None,
                                        output_format: str = 'dataframe',
                                        time_format: str = 'datetime',
                                        nan_method: str = None) -> pd.DataFrame | list[dict]:
        """
        Read tags realtime data but use text filters instead of uids. Also returns data in dataframe format

        Args:
            filter_txt: text filters to search tags in tagviews. If None, will take all tags in tagview
            output_format : Result given in 'dataframe' or 'json'. Defaults to 'dataframe'
            time_format : Optional. 'datetime' or 'unix'. Defaults to datetime
            nan_method: method used to drop NaNs. None or 'interpolate', 'bfill', 'ffill', 'mean', 'zerofill'. Only valid for 'dataframe' output_format

        Returns:
            dataframe or json:
                columns:
                    name: name of tag
                    value: value of tag
                    timeStamp: timeStamp in datatetime or unix time
        """
        # Check for valid parameters
        if output_format not in self._output_formats:
            raise ValueError(f'output_format must be in {self._output_formats}')
        if time_format not in self._time_formats:
            raise ValueError(f'time_format must be in {self._time_formats}')
        tag_info = self.catalogue_tags()
        tags_uids = []
        if isinstance(filter_txt, list):
            for filter in filter_txt:
                uids_loop = list(tag_info[tag_info['name'].str.contains(filter, case=False)].uid)
                tags_uids.extend(uids_loop)
        else:
            if filter_txt:
                tags_uids = list(tag_info[tag_info['name'].str.contains(filter_txt, case=False)].uid)
        # Remove duplicate UIDS
        tags_uids = list(set(tags_uids))
        filtered_hist = self.read_tags_realtime(tags_uids, output_format, time_format, nan_method)
        diccio = dict([(i, j) for i, j in zip(tag_info.uid, tag_info.name)])
        if isinstance(filtered_hist, pd.DataFrame):
            filtered_hist['name'] = filtered_hist['uid'].map(diccio)
        else:
            for item in filtered_hist:
                item['name'] = diccio[item['uid']]
        return filtered_hist

    def read_alarm_status(self, alarm_guid: str) -> dict:
        """
        Reads alarm status for a given alarm

        Args:
            alarm_guid : guid of the alarm

        Returns:
            Dictionary with following data:
            {
                "name": "BasicAlarm1",
                "uid": "b926bfb0-3f2f-49df-a2eb-138452296903",
                "status": "ARE",
                "alarmAREDate": "2022-07-12T12:55:28.9274145+02:00",
                "alarmLastUpdate": "2022-07-12T09:58:39.3102729+02:00",
                "alarmCurrentValue": true,
                "resultTimestampActivation": "2022-07-12T09:58:42.3931339+02:00",
                "resultTimestampDeactivation": "2022-07-12T09:55:34.6931883+02:00",
                "lastNotificationTS": "1900-01-01T00:00:00",
                "signalValue": 95.84623491198114,
                "dataComparisonType": ">",
                "dataComparisonValue": 0,
                "signalValueOnLastHisteresis": 80.27092576039533,
                "lastEvent": "New Event: Alarm supervised by the API"
            }
        """
        if self._version_number < 3:
            raise NotImplementedError('Nexus API version must be greater than 3.0')
        url = self.url_NX + "/api/Alarms/Status/" + alarm_guid
        return self._getResponse(url)

    # -------- WRITING OPERATIONS -------------

    def write_tags_insert(self, tags: str | list[str]) -> list[dict]:
        """
        Check if provided tag names exist, then create them if not

        Args:
            tags: tags name or names to be created

        Returns:
            response object in json format:
                [
                   {
                     "Uid" : "unique tag identifier",
                     "Name" : "name of the tag",
                     "Installation" : "name of the installation",
                     "Driver" : "name of the driver",
                     "Attributes": [
                       {
                         "AttributeName":"name of the attribute",
                         "Value":"value of the attribute for this tag"
                       },
                       ...
                     ]
                   },
                   ...
                ]
        """
        # Crear variables que no existen:
        # 1. Si se ha proporcionado un str, pasar a lista
        if isinstance(tags, str):
            tags = [tags]
        body = json.dumps(tags)
        self._log_print(f'Tags to be created: {body}')
        url_post = self.url_NX + "/api/Tags/Insert"
        return self._postResponse(url_post, body)

    def write_tag_insert_or_update(self, tagname, **attributes) -> list[dict]:
        """This method updates a tag with the complete model that may include attributes or modifies the existing tags changing their attributes to the ones indicated in the query.

        Args:
            tagname: name of the new tag
            **attributes: dictionary of attributes and their values

        Returns:
            response in json format

        Examples:
            Call the function with a tag name and any number of attributes
            response = write_tag_insert_or_update(tagname="mytag", attribute1="value1", attribute2="value2", attribute3="value3")
        """
        if self._version_number < 3:
            raise NotImplementedError('Nexus API version must be greater than 3.0')
        attribute_list = [{"attributeName": name, "value": value} for name, value in attributes.items()]
        body = json.dumps([{"Name": tagname, "Attributes": attribute_list}])
        url = self.url_NX + "/api/Tags/InsertOrUpdate"
        return self._postResponse(url, body)

    def write_tags_insert_or_update_by_json(self, tags_and_attributes: list[dict]):
        """This method creates the tags with the complete model that may include attributes or modifies the existing tags changing their attributes to the ones indicated in the query.

        Args:
            tags_and_attributes: json list containing info for each tag:
                [
                    {
                    "Name": "name of the new tag",
                    "Attributes":
                        [
                            {
                            "AttributeName": "NameOfAttribute1",
                            "Value": "ValueOfAttribute1"
                            }
                        ]
                    }
                ],
                ...

        Returns:
            response in json format
        """
        if self._version_number < 3:
            raise NotImplementedError('Nexus API version must be greater than 3.0')
        body = json.dumps(tags_and_attributes)
        url = self.url_NX + "/api/Tags/InsertOrUpdate"
        return self._postResponse(url, body)

    @_no_row_limit_decorator
    def write_tags_historic_insert(self, df: pd.DataFrame, skip_errors: bool = True) -> list[dict]:
        """Update historical data for tags. Tags need to be created with write_tags_insert first.

        Args:
            df: dataframe
                columns:
                    name: name of the tag
                    value : value of the tag
                    timeStamp: timeStamp in unix
            skip_errors = True: If true, not created tags will be dropped from dataframe

        Returns:
            response in json format
        """
        # la funcion mira cuantas variables diferentes contiene el dataframe y comprueba si todas ellas existen
        vbles = list(df.name.unique())
        n_tags = len(vbles)
        # La función comprueba primero si existe la variable en la que se quiere escribir
        url_completa = self.url_NX + "/api/Tags/writable"
        response = requests.get(url_completa, verify=False, headers=self.header)
        variables = response.json()
        variables_pd = pandas.DataFrame(variables)
        variables_names = list(variables_pd.name)

        diccio = dict([(i, j) for i, j in zip(variables_pd.name, variables_pd.uid)])
        df2 = df.copy()

        for j in vbles:
            if j not in variables_names:
                self._log_print(f'Tag {j} was not created. Use write_tags_insert first', severity='error')
                if skip_errors:
                    df2.drop(df.loc[df['name'] == j].index, inplace=True)

        df2['uid'] = df2['name'].map(diccio)
        df2.drop(columns=["name"], inplace=True)
        if df2['timeStamp'].dtype == 'datetime64[ns]':
            warnings.warn('timeStamp in datetime format: please check that it is in UTC')
            self._log_print('timeStamp in datetime format: please check that it is in UTC', severity='warning')
            df2['timeStamp'] = df2['timeStamp'].astype('int64') / 1e9
        payload = pandas.DataFrame.to_json(df2, date_format="epoch", orient="records")
        url_completa = self.url_NX + "/api/Tags/historic/insert"
        response = self._postResponse(url_completa, payload)
        self._log_print(f'Successfully written {n_tags} tags')
        return response

    @_no_row_limit_decorator
    def write_tags_realtime_insert(self, df: pd.DataFrame, skip_errors: bool = True):
        """Update realtime data for tags. Tags need to be created with write_tags_insert first.

        Args:
            df: dataframe
                columns:
                    name: name of the tag
                    value : value of the tag
                    timeStamp (optional): timeStamp in unix. If not provided, will take current time
            skip_errors  = True: If true, not created tags will be dropped from dataframe

        Returns:
            response text (None if OK)
        """
        vbles = list(df.name.unique())
        n_tags = len(vbles)
        # Check if tags exists
        url_completa = self.url_NX + "/api/Tags/writable"
        response = requests.get(url_completa, verify=False, headers=self.header)
        variables = response.json()
        variables_pd = pandas.DataFrame(variables)
        variables_names = list(variables_pd.name)

        diccio = dict([(i, j) for i, j in zip(variables_pd.name, variables_pd.uid)])
        df2 = df.copy()

        for j in vbles:
            if j not in variables_names:
                self._log_print(f'Tag {j} was not created. Use write_tags_insert first', severity='error')
                if skip_errors:
                    df2.drop(df.loc[df['name'] == j].index, inplace=True)

        df2['uid'] = df2['name'].map(diccio)
        df2.drop(columns=["name"], inplace=True)
        if 'timeStamp' in df2.columns and df2['timeStamp'].dtype == 'datetime64[ns]':
            warnings.warn('timeStamp in datetime format: please check that it is in UTC')
            self._log_print('timeStamp in datetime format: please check that it is in UTC', severity='warning')
            df2['timeStamp'] = df2['timeStamp'].astype('int64') / 1e9
        payload = pandas.DataFrame.to_json(df2, date_format="epoch", orient="records")
        url_completa = self.url_NX + "/api/Tags/realtime/insert"
        response = self._postResponse(url_completa, payload)
        self._log_print(f'Successfully written {n_tags} tags')
        return response

    def write_tag_realtime_insert(self, name: str, value: float | int, timeStamp=None):
        """Update realtime data for a single tag. Tag needs to be created with write_tags_insert first.

        Args:
            name: tag name
            value: value of the tag
            timeStamp (optional): time in unix time. If None, will take current time

        Returns:
            response text (None if OK)
        """
        # La función comprueba primero si existe la variable en la que se quiere escribir
        url = self.url_NX + "/api/Tags/writable"
        # self.log_print(url_completa)
        variables = self._getResponse(url)
        variables_norm = self._json_normalize_check(variables)
        variables_names = list(variables_norm.name)

        if name in variables_names:
            variable_uid = list(variables_norm[variables_norm.name == name].uid)[0]
            if timeStamp is None:
                payload = json.dumps(
                    [
                        {
                            'Uid': variable_uid,
                            'Value': value,
                        }
                    ]
                )
            else:
                payload = json.dumps(
                    [
                        {
                            'Uid': variable_uid,
                            'Value': value,
                            'timeStamp': timeStamp
                        }
                    ]
                )
        else:
            raise Exception(f'Tag {name} was not created. Please use write_tags_insert first')

        url_completa = self.url_NX + "/api/Tags/realtime/insert"
        response = self._postResponse(url_completa, payload)
        self._log_print(f'Successfully written {name}: {value}')
        return response

    @_no_row_limit_decorator
    def write_tags_transient_insert(self, df: pd.DataFrame, skip_errors: bool = True) -> list[dict]:
        """Update transient data for tags. Tags need to be created with write_tags_insert first.

        Args:
            df: dataframe
                columns:
                    name: name of the tag
                    value : value of the tag
                    timeStamp: timeStamp in unix
            skip_errors  = True: If true, not created tags will be dropped from dataframe

        Returns:
            response in json format
        """
        # la funcion mira cuantas variables diferentes contiene el dataframe y comprueba si todas ellas existen
        vbles = list(df.name.unique())
        n_tags = len(vbles)
        # La función comprueba primero si existe la variable en la que se quiere escribir
        url_completa = self.url_NX + "/api/Tags/writable"
        response = requests.get(url_completa, verify=False, headers=self.header)
        variables = response.json()
        variables_pd = pandas.DataFrame(variables)
        variables_names = list(variables_pd.name)

        diccio = dict([(i, j) for i, j in zip(variables_pd.name, variables_pd.uid)])
        df2 = df.copy()

        for j in vbles:
            if j not in variables_names:
                self._log_print(f'Tag {j} was not created. Use write_tags_insert first', severity='error')
                if skip_errors:
                    df2.drop(df.loc[df['name'] == j].index, inplace=True)

        df2['uid'] = df2['name'].map(diccio)
        df2.drop(columns=["name"], inplace=True)
        if df2['timeStamp'].dtype == 'datetime64[ns]':
            warnings.warn('timeStamp in datetime format: please check that it is in UTC')
            self._log_print('timeStamp in datetime format: please check that it is in UTC', severity='warning')
            df2['timeStamp'] = df2['timeStamp'].astype('int64') / 1e9
        payload = pandas.DataFrame.to_json(df2, date_format="epoch", orient="records")
        url_completa = self.url_NX + "/api/Tags/transient/insert"
        response = self._postResponse(url_completa, payload)
        self._log_print(f'Successfully written {n_tags} tags')
        return response

    def write_alarm_acknowledge(self, guid: str, status: str) -> str:
        """Used to change the status of an alarm from ANR or ENR to ARE o EXR.

        Args:
            guid: guid of the alarm
            status: 'ARE' or 'EXR', 'ANR' or 'ENR'

        Returns:
            response text (None if OK)
        """
        if self._version_number < 2:
            raise NotImplementedError('Version 1.0 does not support alarm methods')
        if status not in ['ARE', 'EXR', 'ANR', 'ENR']:
            raise ValueError("Status must be 'ARE', 'EXR', 'ANR', 'ENR'")
        else:
            url_completa = self.url_NX + "/api/Alarms/alarm/" + guid + "/acknowledge"
            body = "\"" + status + "\""
            return self._postResponse(url_completa, body)

    def write_alarm_event(self, guid: str, msg: str) -> str:
        """
        Used to insert an event with a message in the history of the alarm. The alarma must be active and enabled.

        Args:
            guid: guid of the alarm
            msg: text of the message
        """
        if self._version_number < 2:
            raise NotImplementedError('Version 1.0 does not support alarm methods')
        url_completa = self.url_NX + "/api/Alarms/alarm/" + guid + "/event"
        body = json.dumps({'Message': msg})
        return self._postResponse(url_completa, body=body)

    # -------- REMOTE OPERATION TO PLC -----------

    def operate_tags(self, df: pd.DataFrame):
        """If the token has access to operate against a Conector associated with a PLC, this method can be used to write values to the actual Plc's tags.

        Args:
            df: dataframe
             columns:
                uid: tag uid
                value: value to write
        """
        url_completa = self.url_NX + "/api/Tags/operate"
        df = df[['uid', 'value']]
        payload = df.to_json(orient='records')
        response = self._postResponse(url_completa, payload)
        self._log_print(response)
        return response

    def operate_tag_single(self, tag_uid: str, value: int | float):
        """If the token has access to operate against a Conector associated with a PLC, this method can be used to write values to the actual Plc's tags.

        Args:
            tag_uid: nombre de la variable a escribir en el PLC
            value: valor de la variable a escribir
        """
        url_completa = self.url_NX + "/api/Tags/operate"
        payload = json.dumps(
            [
                {
                    'Uid': tag_uid,
                    'Value': value,
                }
            ]
        )
        response = self._postResponse(url_completa, payload)
        self._log_print(response)
        return response

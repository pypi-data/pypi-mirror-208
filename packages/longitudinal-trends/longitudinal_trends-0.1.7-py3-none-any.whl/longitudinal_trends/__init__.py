# # import datetime as dt

# # from longitudinal_trends import RequestTrends

# # day_data = RequestTrends('UBI', 'UBI', 'UBI_folder', dt.datetime(2012, 1, 1), dt.datetime(2022,12,31), 'daily') #4017 days

# # day_data.time_series(reference_geo_code=" ")

# import datetime as dt
# from longitudinal_trends import RequestTrends

# # # day_data = RequestTrends('Anxiety', '/m/0k_9', dt.datetime(2021, 11, 1), dt.datetime(2022,10,24), 'daily') #358 Days
# # day_data = RequestTrends('UBI', 'UBI', 'UBI_folder', dt.datetime(2012, 1, 1), dt.datetime(2022,12,31), 'daily') #4017 days
# # week_data = RequestTrends('Anxiety', '/m/0k_9', dt.datetime(2016,11,21), dt.datetime(2022,10,24), 'weekly') #2163 Days | 309 Weeks
# month_data = RequestTrends('UBI', 'universal basic income', 'UBI_folder', dt.datetime(2012, 1, 1), dt.datetime(2022,12,31), 'monthly') #1890 Days | 63 Months

# # day_data.cross_section('US')
# # day_data.cross_section('US-AL')
# # week_data.one_click_function('US-AL')
# # week_data = RequestTrends('UBI', 'UBI', dt.datetime(2016,11,21), dt.datetime(2022,10,24), 'weekly') #2163 Days | 310 Weeks
# # week_data.all_in_one_method()
# # day_data.all_in_one_method(reference_geo_code="IT")
# # week_data.convert_cross_section("US-AK")
# # day_data.convert_cross_section("US-AL")
# # day_data.time_series(reference_geo_code=" ")
# # start, end = dt.datetime(2012, 1, 1), dt.datetime(2022,12,31)
# # print(end-start)
# month_data.time_series(reference_geo_code='IT')

import pandas as pd
import os
import glob
import json

import requests
from pytrends.exceptions import ResponseError
from pytrends.request import TrendReq

import datetime as dt
from dateutil.relativedelta import *
import time

import logging
from rich.console import Console
from rich.logging import RichHandler

from math import ceil
import random

console = Console()

class RequestTrends:

    logging.basicConfig(
        level="INFO", format="%(message)s", datefmt="%d-%b-%Y %H:%M:%S", handlers=[RichHandler(rich_tracebacks=True)]
    )


    def __init__(self, keyword: str, topic: str, folder_name: str, start_date: dt.datetime, end_date: dt.datetime, data_format: str):
        """
            keyword: keyword to get data from Google Trends
            topic: The search terms/topic terms for the keyword in string format (Eg. "/m/0ddwt" for 'Disorder' topic of 'Insomnia')
            start_date: Start Date for search query
            end_date: End Date for search query
            data_format: 'daily', 'weekly', 'monthly'
        """

        self.__logger = logging.getLogger("rich")

        self.keyword = keyword
        self.folder_name = folder_name
        self.topic = topic

        self.start_date = start_date
        self.end_date = end_date
        self.data_format = data_format
        self.TIME_WINDOW = None

        # Calculate total days between start and end dates
        self.__num_of_days = (end_date - start_date).days

        # Validation check for type of data request in addition to valid timeperiod for the requested data format
        if data_format not in ['daily', 'weekly', 'monthly']:
            raise ValueError("data_format should be 'daily'/'weekly'/'monthly'")
        elif data_format == 'monthly':
            self.start_date = dt.datetime(start_date.year, start_date.month, 1)
            if self.__num_of_days < 1890:
                
                raise ValueError("Difference Between Start and End date needs to be more than 1889 days to get monthly data. Given only '{}' days".format(self.__num_of_days))
        elif data_format == 'weekly':
            if self.__num_of_days < 270:
                raise ValueError("Difference Between Start and End date needs to be more than 269 days to get weekly data. Given '{}' days".format(self.__num_of_days))

            self.TIME_WINDOW = 1889
            self.__determine_time_periods()

            check_end_period = (self.__times[-1] - self.__times[-2]).days
            if  check_end_period < 270:
                raise ValueError("Last Time Period is less than 270 days. Given {} ".format(check_end_period))
            
        else:
            self.TIME_WINDOW = 269
            self.__determine_time_periods()

        self.__create_required_directory(self.folder_name)
        self.__create_required_directory('{}/{}'.format(self.folder_name, data_format))

        # Save the parameters into a file for future reference
        params = {
            'keyword': keyword,
            'topic': topic,
            'folder_name': folder_name,
            'start_date': start_date,
            'end_date': end_date,
            'data_format': data_format
        }
        params_fl = '{}/{}/params.txt'.format(folder_name, data_format)
        with open(params_fl, 'w') as fl:
            fl.write(json.dumps(params, indent=4, sort_keys=True, default=str))
        fl.close()

        # Initiaate pytrends request to enquire later
        self.__pytrend = TrendReq(hl='en-US', tz=360)#, requests_args={'headers': {'Cookie': f'NID={nid_cookie}'}})
        self.__logger.info("Pytrend instance have been initiated for longitudinal_trend", extra={"markup": True})


    def __in_notebook(self):
        try:
            from IPython import get_ipython
            if 'IPKernelApp' not in get_ipython().config:  # pragma: no cover
                return False                
        except ImportError:
            return False
        except AttributeError:
            return False
        return True
        

    # This method is intended to create necessary directories at each discretion
    def __create_required_directory(self, folder):
        if not os.path.exists(folder):
            os.mkdir(folder)

    # This method provides list of time periods to fetch data for
    def __determine_time_periods(self):
        timeperiod = ceil(self.__num_of_days/self.TIME_WINDOW)

        self.__times = [self.start_date + dt.timedelta(days=x*self.TIME_WINDOW) for x in range(0, timeperiod+1)]
        self.__times[-1] = self.end_date


    def cross_section(self, geo: str="", resolution: str="COUNTRY"):
        self.__logger.info("Collecting Cross Section Data now")

        res = ["COUNTRY", "REGION", "CITY"]

        print(geo, " Before")
        if (not geo.strip() and resolution != "COUNTRY") or (geo.strip() and resolution not in res):
            self.__logger.info("Incorrect Resolution Provided. Defaulting to 'COUNTRY'")
            resolution = "COUNTRY" 

        print(geo, " After")

        self.__create_required_directory("{}/{}/by_region".format(self.folder_name, self.data_format))

        if self.data_format == 'daily':
            chng_delta = relativedelta(days=1)
            end_delta = relativedelta(days=0)
            form = 'day'
        if self.data_format == 'weekly':
            chng_delta = relativedelta(weeks=1)
            end_delta = relativedelta(weeks=1, days=-1)
            form = 'week'
        if self.data_format == 'monthly':
            chng_delta = relativedelta(months=1)
            end_delta = relativedelta(months=1, days=-1)
            form = 'month'

        current_time = self.start_date

        # Just a touchup for a better filename
        i = 0

        self.__logger.info("Please note that this method may take hours to finish. Have patience.", extra={"markup": True})
        with console.status("Collecting Data...") as stats:
            while True:
                if (self.data_format == 'weekly' and current_time >= self.end_date) or (self.data_format != 'weekly' and current_time > self.end_date):
                    stats.stop()
                    break

                current_end_time = current_time + end_delta
                # print("{}/{}/by_region/{}_{}-{}-{}.csv".format(self.folder_name, self.data_format,  form, i+1, current_time.strftime("%Y%m%d"), current_end_time.strftime("%Y%m%d")))
                if os.path.exists("{}/{}/by_region/{}_{}-{}-{}.csv".format(self.folder_name, self.data_format,  form, i+1, current_time.strftime("%Y%m%d"), current_end_time.strftime("%Y%m%d"))):
                        # print('true')
                        self.__logger.info("Data for {}-{} already collected. Moving to next date...".format(current_time.strftime("%#d/%m/%#Y"), current_end_time.strftime("%#d/%m/%#Y")), extra={"markup": True})
                        current_time += chng_delta
                        i += 1
                else:
                    try:
                        print(geo, " Right Before")
                        self.__pytrend.build_payload(kw_list=[self.topic], geo=geo, 
                                                        timeframe='%s %s' % (current_time.strftime("%Y-%m-%d"), current_end_time.strftime("%Y-%m-%d"))) 
                        time.sleep(5)
                        df = self.__pytrend.interest_by_region(resolution=resolution, inc_geo_code=True, inc_low_vol=True)
                        df = df.rename(columns={self.topic:self.keyword})
                        i += 1
                    except ResponseError as e:

                        self.__logger.info("Please have patience as we reset rate limit ... ", extra={"markup": True})
                        time.sleep(5)
                        continue
                    except:
                        stats.stop() # Stop the animation
                        if not self.__in_notebook():
                            self.__logger.error("[bold red]Whoops![/]", exc_info=1, extra={"markup": True})
                            quit()
                        else:
                            self.__logger.error("[bold red]Whoops![/]", exc_info=1, extra={"markup": True})
                            self.__logger.error("[bold red]Don't worry about 'Assertion Error'. [/]", extra={"markup": True})
                            assert False
                        
                    time.sleep(5)
                    df.to_csv("{}/{}/by_region/{}_{}-{}-{}.csv".format(self.folder_name, self.data_format,  form, i, current_time.strftime("%Y%m%d"), current_end_time.strftime("%Y%m%d")))

                    current_time += chng_delta

            self.__logger.info("[bold green]Successfully Collected Required Data![/]", extra={"markup": True})


    # Time Series Data collection method for 'monthly'
    def __time_series_monthly(self, stats, reference_geo_code: str="US"):
        if os.path.exists("{}/{}/over_time/{}/{}-{}.csv".format(self.folder_name, self.data_format, reference_geo_code, self.start_date.strftime("%Y%m%d"), self.end_date.strftime("%Y%m%d"))):
            stats.stop()
            self.__logger.info("All Data for current request is already collected", extra={"markup": True})
        else:
            try:
                self.__pytrend.build_payload(kw_list=[self.topic], geo=reference_geo_code, 
                                    timeframe='%s %s' % (self.start_date.strftime("%Y-%m-%d"), self.end_date.strftime("%Y-%m-%d"))) 
                time.sleep(5)
                df = self.__pytrend.interest_over_time()

                df = df.rename(columns={self.topic:self.keyword})
                df.to_csv("{}/{}/over_time/{}/{}-{}.csv".format(self.folder_name, self.data_format, reference_geo_code, self.start_date.strftime("%Y%m%d"), self.end_date.strftime("%Y%m%d")))
            
            except ResponseError as e:
                self.__logger.info("Please have patience as we reset rate limit ... ", extra={"markup": True})
                time.sleep(5)
            except:
                stats.stop()
                self.__logger.error("[bold red]Whoops![/]", exc_info=1, extra={"markup": True})


    # Time Series Data collection method for 'weekly'/'daily'
    def __time_series_nmonthly(self, stats, reference_geo_code: str="US"):
        for period in range(len(self.__times)-1):
            start, end = self.__times[period], self.__times[period+1]

            if self.data_format == "weekly":
                num_days = (end - start).days
                if num_days < 270:
                    stats.stop()
                    raise ValueError("For period: {}, days given: {}. Please increase timeline".format(period+1, num_days))
            
            if os.path.exists("{}/{}/over_time/{}/{}-{}-{}.csv".format(self.folder_name, self.data_format, reference_geo_code, period+1, start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))):
                self.__logger.info("Data for {} to {} already collected. Moving to next date...".format(start.strftime("%#d/%m/%#Y"), end.strftime("%#d/%m/%#Y")), extra={"markup": True})
            else:
                try:
                    self.__pytrend.build_payload(kw_list=[self.topic], geo=reference_geo_code, 
                                        timeframe='%s %s' % (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))) 
                    time.sleep(5)
                    df = self.__pytrend.interest_over_time()

                except ResponseError as e:
                    self.__logger.info("Please have patience as we reset rate limit ... ", extra={"markup": True})
                    time.sleep(5)
                    continue
                except:
                    stats.stop()
                    self.__logger.error("[bold red]Whoops![/]", exc_info=1, extra={"markup": True})
                    break

                if df.empty:
                    stats.stop()
                    self.__logger.info("No Data was returned for period: {} -> '{}' to '{}'".format(period+1, start.strftime("%#d/%m/%#Y"), end.strftime("%#d/%m/%#Y")), extra={"markup": True})
                else:                    
                    df = df.rename(columns={self.topic:self.keyword})
                    df.drop('isPartial', axis=1, inplace=True)
                    df.to_csv("{}/{}/over_time/{}/{}-{}-{}.csv".format(self.folder_name, self.data_format, reference_geo_code, period+1, start.strftime("%Y%m%d"), end.strftime("%Y%m%d")))


    def time_series(self, reference_geo_code: str="US"):
        """
            reference_geo_code: Reference reference_geo_code code for Country/State/City. Eg, 'US-Al' for Alabama state of united states.
            *** If unsure of reference_geo_code, run 'cross_section' function as it will give the reference_geo_code Codes of the desired level ***
        """
        with console.status("Collecting Data...") as stats:
            self.__logger.info("Collecting Over Time Data now", extra={"markup": True})

            self.__create_required_directory('{}/{}/over_time'.format(self.folder_name, self.data_format))
            self.__create_required_directory('{}/{}/over_time/{}'.format(self.folder_name, self.data_format, reference_geo_code))

            if self.TIME_WINDOW:
                self.__time_series_nmonthly(stats, reference_geo_code)
            else:
                self.__time_series_monthly(stats, reference_geo_code)


    def concat_time_series(self, reference_geo_code: str="US", zero_replace: float=0.1):
        self.__logger.info("Concatenating Over Time data now", extra={"markup": True})

        # Create Folder to save the concatenated time series data
        self.__create_required_directory("{}/{}/concat_time_series".format(self.folder_name, self.data_format))

        path_to_time_data = "{}/{}/over_time/{}".format(self.folder_name, self.data_format, reference_geo_code)

        dfs = []
        for fl in os.listdir(path_to_time_data):
            dta = path_to_time_data+'/'+fl
            dfs.append(pd.read_csv(dta))

        prev_window = dfs[0]
        prev_window[self.keyword].replace(0, zero_replace, inplace=True)

        for periods in range(1, len(dfs)):
            next_window = dfs[periods]
            next_window[self.keyword].replace(0, zero_replace, inplace=True)
    
            prev_window_multiplier = 100/prev_window.iloc[-1][self.keyword]
            next_window_multiplier = 100/next_window.iloc[0][self.keyword]

            prev_window.iloc[:,1] = prev_window.iloc[:,1] * prev_window_multiplier
            next_window.iloc[:,1] = next_window.iloc[:,1] * next_window_multiplier

            prev_window = pd.concat([prev_window.iloc[:-1,:], next_window])

        prev_window.to_csv("{}/{}/concat_time_series/{}.csv".format(self.folder_name, self.data_format, reference_geo_code), index=False)
        self.__logger.info("[bold green]Concatenation Complete! :) [/]", extra={"markup": True})


    def convert_cross_section(self, reference_geo_code: str="US", zero_replace: float=0.1):
        self.__logger.info("Rescaling cross section Data now", extra={"markup": True})
        
        self.__create_required_directory("{}/{}/converted".format(self.folder_name, self.data_format))
        self.__create_required_directory("{}/{}/converted/{}".format(self.folder_name, self.data_format, reference_geo_code))

        time_series_concat = pd.read_csv("{}/{}/concat_time_series/{}.csv".format(self.folder_name, self.data_format, reference_geo_code), parse_dates=['date'])

        with console.status("Converting...") as stats:
            for ind, row in time_series_concat.iterrows():
                record = row['date'].strftime('%Y%m%d')
                time_ind = float(row[self.keyword])

                snap_file = glob.glob("{}/{}/by_region/*{}*.csv".format(self.folder_name, self.data_format, record))[0]
                fl_name = snap_file.split("\\")[-1]
                col_name = fl_name.split('.')[0]

                snap_df = pd.read_csv(snap_file, keep_default_na=False)
                snap_df[self.keyword].replace(0, zero_replace, inplace=True)

                ref_value = float(snap_df.loc[snap_df['geoCode'].str.contains(reference_geo_code)][self.keyword])
        
                conv_multiplier = float(time_ind/ref_value)

                snap_df.iloc[:,2] = round(snap_df.iloc[:,2] * conv_multiplier, 2)

                if ind==0:
                    conv = snap_df[['geoName', 'geoCode']]

                kwarg = {col_name: list(snap_df[self.keyword])}
                conv = conv.assign(**kwarg)

            stats.stop()
            conv.to_csv("{}/{}/converted/{}/final-converted-{}-{}.csv".format(self.folder_name, self.data_format, reference_geo_code, self.start_date.strftime("%Y%m%d"), self.end_date.strftime("%Y%m%d")), index=False)
            self.__logger.info("[bold green]DONE Converting! :) [/]", extra={"markup": True})
    

    def all_in_one_method(self, geo="", reference_geo_code="US", zero_replace=0.1):
        # At first collect across region data for the particular region/country/dma/city
        self.cross_section(geo)

        # Then Collect over the time longitudinal data
        self.time_series(reference_geo_code)

        # Next Merge/Concatenate over the time data into a single long term trend
        self.concat_time_series(reference_geo_code, zero_replace)

        # Finally rescale all across region data by converting them 
        self.convert_cross_section(reference_geo_code, zero_replace)

        self.__logger.info("[bold green]DONE! :) [/]", extra={"markup": True})
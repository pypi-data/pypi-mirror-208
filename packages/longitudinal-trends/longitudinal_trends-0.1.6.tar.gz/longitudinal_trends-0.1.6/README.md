# longitudinal_trends

## Introduction

This is a python library for downloading cross-section and time-series Google Trends and converting them to longitudinal data.

Although Google Trends provides cross-section and time-series search data, longitudinal Google Trends data are not readily available. There exist several practical issues that make it difficult for researchers to generate longitudinal Google Trends data themselves. First, Google Trends provides normalized counts from zero to 100. As a result, combining different regions' time-series Google Trends data does not create desired longitudinal data. For the same reason, combining cross-sectional Google Trends data over time does not create desired longitudinal data. Second, Google Trends has restrictions on data formats and timeline. For instance, if you want to collect daily data for 2 years, you cannot do so. Google Trends automatically provides weekly data if your request timeline is more than 269 days. Similarly, Google Trends automatically provides monthly data if your request timeline is more than 269 weeks even though you want to collect weekly data.

The longitudinal_trends library resolves the aforementioned issues and allows researchers to generate longitudinal Google Trends.

This library is built on top of another library `pytrends` which also have few dependencies. As long as `Google Trends API`, `pytrends` and all their dependencies work, `longitudinal_trends` will also work!

***Note**: This library is still in planning phase and not fully tested.*

## Table of contents

* Installation
* Requirements
* Initiate `longitudinal_trends`
* Methods
  * `cross_section`
  * `time_series`
  * `concat_time_series`
  * `convert_cross_section`
  * `all_in_one_method`
* Caveats
* Credits
* Disclaimer

## Installation

`pip install longitudinal-trends`

## Requirements

`pip install -r requiremnts.txt`

## Initiate longitudinal_trends

```python
from longitudinal_trends import RequestTrends
import datetime as dt

day_data = RequestTrends(keyword='Insomnia', topic='/m/0ddwt', folder_name='insomnia_save', start_date=dt.datetime(2021, 11, 1), end_date=dt.datetime(2022,10,24), data_format='daily')
```

The initiator call will initiate `pytrends` that initiates the `Google Trends API`. In the initiation stage, two folders will be created automatically

1. Parent folder that the users will choose the name of and
2. Folder corresponding to the data_format.
   So all the daily data will be stored under 'daily' folder for daily data, 'weekly' folder for weekly data and so on.
   **Parameters**

- `keyword`
  - The keyword to be used for collecting google trends data
- `topic`
  - The topic of the keyword. If any topic is to be used instead of search term.
    - For example, '/m/0ddwt' will give google trends data for Insomnia as topic of 'Disorder'.
      - **NOTE**: URL's have certain codes for special characters. For example, `%20` = white space, `%2F` = / (forward slash) etc.
    - If the topic and keyword are the same, then data provided will be for google trends search term and not any particular topic. So, `keyword='Insomnia', topic='Insomnia'` will provide google trends data for Insomnia as search term.
- `folder_name`
  - Name of folder to be created to save all the data
- `start_date`
  - Date to start from
- `end_date`
  - Date to end at
- `data_format`
  - Time basis query
  - Can choose only one from the list: ['daily', 'weekly', 'monthly']

## Methods

### cross_section

```python
day_data.cross_section(geo='US', resolution="REGION")
```

This method will collect cross section data of the given keyword and timeline. It calls `pytrends.interest_by_region()` method from pytrends. The data is automatically saved in →  'folder_name'/'data_format'/by_region. Each file has data for the given region/countries all the country/state google trends index for 1 day/week/month. The filenames tells the date of the data time period and also has an indication of number of day/week/month.

For more information on pytrends `interest_by_region()` method, [check here](https://pypi.org/project/pytrends/#interest-by-region).

**PS**: *This method takes a long time to finish running. For example, it takes around 5 hours to collect 350 days of daily data. The time is mainly due to Google Trends API rate limit.*

**Parameters**

- `geo`
  - Country/Region to collect data from. If left empty, then result will be worldwide i.e. data will be collected for all country. If left empty, defaults to worldwide country level.
- `resolution`
  - 'COUNTRY' returns country level data
  - 'REGION' returns region level data
  - 'CITY' returns city level data
  - Defaults to country

### time_series

```python
day_data.time_series(reference_geo='US-AL')
```

This method will collect over time data. It calls `pytrends.interest_over_time()` method from pytrends. For time series google trends data, by default google will provide weekly data if the days between start and end date is more than 270 days and will provide monthly data if the difference is more than 270 weeks. To tackle that problem, this method will collect the daily/weekly data into chunks less then 270 days/weeks. The collected data will be saved under → 'folder_name'/'data_format'/over_time/'reference_geo

For more information on pytrends `interest_over_time()` method, [check here](https://pypi.org/project/pytrends/#interest-over-time).

**Parameters**

- `reference_geo`
  - Country/State/City to be used as reference point to rescale the data in later part

### concat_time_series

```python
day_data.concat_time_series(reference_geo='US-AL', zero_replace=0.1)
```

This method will concat the time series data collected in `time_series()` method. Because the data points in  `time_series` is independent of each other, they needs to be re-aligned to get correct index for the given time period. This method concatenates `time_series` data for all the period and gives back the combined rescaled `time_series` data for the reference timeline. This rescaled `time_series` data will be used in the next method to rescale the `cross_section` data.

**Parameters**

- `reference_geo`
  - This is the same `geo` code that is used in collecting `time_series` data. If the time_series data for that geo is not collected beforehand, or the file does not exist, it will throw and error. Default is 'US'
- `zero_replace`
  - As data from different time periods are rescaled, sometimes the last/first data point of a period might be zero. Then the calculation will throw error or everything single data point will become zero. To avoid that, we are tweaking the zeroes to be of an insignificant number to carry on with the calculation.

### convert_cross_section

```python
day_data.convert_cross_section(reference_geo='US-AL', zero_replace=0.1)
```

This final method will rescale the cross section data based on the concatenated time series data. This will finally provide the accurate google trends index for each region/country/city over the provided time period.

**Parameters**

- `reference_geo`
  - Same as the reference_geo from `concat_time_series()`. If anyother is used, then the result will not be accurate
- `zero_replace`
  - Same as zero_replace from `concat_time_series()`. It is highly recommended to use the same to avoid incosistent results.

### all_in_one_method

```python
day_data.all_in_one_method(geo='US', reference_geo='US-AL', zero_replace=0.1)
```

This last method combines all the methods together and executes them in the correct sequence. It will collect the cross_section & time_series data, concat the time_series data and finally rescale the cross section data all in one go. All the files will be present for cross reference.

Note that the sequence of the first two methods `cross_section()` & `time_series()` don't matter since they are independent. However, the later two are depended on the first two. `concat_time_series()` is depended on `time_series()` and `convert_cross_section()` is depended on both `concat_time_series()` and `cross_section()`.

**Parameters**

- `geo`
  - Same as `geo` from `cross_section()`
- `reference_geo`
  - Same as `reference_geo` from `time_series()` and `concat_time_series()`
- `zero_replace`
  - Same as `zero_replace` from `concat_time_series()` and `convert_cross_section()`

## Caveats

This is not an Official or Supported API.

`longitudinal_trends` is built on top of `pytrends`. `pytrends` uses `Google Trends API` to collect trends data. So we do not have any control over the accuracy or quality of the trends data. It has been observed during tests that for the same inputs (keyword, topic, data_format, timeline), outputs were little different.

`zero_replace` is used to avoid division errors. But when the `zero_replace` is very small number, and there are a lot of zeroes in the dataset, then the final output will contain very big numbers. However, there is no specific rule or recommendation for the `zero_replace`. Its gonna be a trial & error.

On that note, if the search term is not very popular, then the resultant dataset will contain a lot of zeroes that will hugely impact the final outcome.

## Credits

- `pytrends` library
  - https://github.com/GeneralMills/pytrends/tree/0d6113a3920e7576d4b3459132b5d37fb7ab9bfb

## Disclaimer

This publication was made possible by the generous support of the Qatar Foundation through Carnegie Mellon University in Qatar's Seed Research program. The statements made herein are solely the responsibility of the authors.

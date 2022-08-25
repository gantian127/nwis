# -*- coding: utf-8 -*-
from datetime import datetime

import requests
import pandas as pd
from io import StringIO
import dataretrieval.nwis as nwis


class Nwis:
    def __init__(self):
        self._dataset = None
        self._variable_info = None
        self._site_info = None

    @property
    def data(self):
        return self._dataset

    @property
    def variables(self):
        return self._variable_info

    @property
    def sites(self):
        return self._site_info

    def get_data(self, sites, start, end, service, parameterCd=None, output=None, **kwargs):

        # check user input
        Nwis._check_user_input(sites, start, end, service, output)

        # get data
        nwis_data = Nwis._get_nwis_data(self, sites=sites, start=start, end=end, service=service,
                                        parameterCd=parameterCd, output=output, **kwargs)
        self._dataset = nwis_data

        return nwis_data

    @staticmethod
    def _check_user_input(sites, start, end, service, output):
        # check sites
        if type(sites) is str:
            sites = [sites]

        for site in sites:
            try:
                site_info = nwis.get_record(sites=site, service='site')
                if site_info.empty:
                    raise ValueError("Incorrect USGS site number.")
            except Exception:
                raise ValueError("Incorrect USGS site number.")

        # check start end time
        try:
            start_datetime = datetime.strptime(start, '%Y-%m-%d')
            end_datetime = datetime.strptime(end, '%Y-%m-%d')

            if start_datetime > end_datetime:
                raise ValueError('Incorrect start date.')

        except Exception:
            raise ValueError("Incorrect date format. It needs to be YYYY-MM-DD. ")

        # check service
        if service not in ['dv', 'iv']:
            raise ValueError("Incorrect service option '{}': 'dv' as daily mean data or 'iv' as instantaneous data.".format(service))

        # check output
        if output and output[-3:] != '.nc':
            raise ValueError('Incorrect NetCDF file path for the output.')

    def _get_nwis_data(self, sites, start, end, service, parameterCd=None, output=None, **kwargs):

        # get time series data frame
        ts_df = nwis.get_record(sites=sites, service=service, start=start, end=end, parameterCd=parameterCd, **kwargs)

        if ts_df.empty:
            print('Data is not available for the provided parameters.')
            raise
        else:
            # get site info
            site_info = Nwis._get_site_info(sites=sites)    # sites=['03339000','01542500']
            if not site_info:
                print('Failed to get the site information.')
                raise
            else:
                self._site_info = site_info

            # get variable info
            parameterCd = list(set([name.split('_')[0] for name in ts_df.columns if name.split('_')[0].isnumeric()]))
            variable_info = Nwis._get_variable_info(parameterCd)
            if not variable_info:
                print('Failed to get the variable information.')
                raise
            else:
                self._variable_info = variable_info

            # refine dataframe
            filter_names = []
            for code in parameterCd:
                for pattern in ['', '_Mean', '_hach', '_hach_Mean']:
                    if code+pattern in ts_df.columns:
                        filter_names.append(code+pattern)
                        break

            nwis_df = ts_df[filter_names]  # this removes the max, min, cd columns from the dataframe
            new_col_names = [name.split('_')[0] for name in filter_names]
            nwis_df.columns = new_col_names

            # convert to xarray
            nwis_data = nwis_df.to_xarray()  # in the array, the row is site number, column is time step

            if nwis_df.index.nlevels == 1:
                nwis_data.coords['datetime'] = nwis_df.index.values
            else:
                nwis_data.coords['datetime'] = nwis_df.index.levels[nwis_df.index.names.index('datetime')].values

            # save output file as csv file
            if output:
                try:
                    nwis_data.to_netcdf(output)
                except Exception:
                    print('Failed to write the data in the NetCDF file.')
                    raise

        return nwis_data

    @staticmethod
    def _get_site_info(sites):
        site_info = {}
        site_info_df = nwis.get_record(sites=sites, service='site')
        for index, row in site_info_df.iterrows():
            site_info[row['site_no']] = {
                'site_lat': row['dec_lat_va'],
                'site_lon': row['dec_long_va'],
                'site_altitude': row['alt_va'],
                'site_name': row['station_nm'],
            }

        return site_info

    @staticmethod
    def _get_variable_info(parameterCd):
        variable_info = {}
        parameterCd = [parameterCd] if type(parameterCd) is str else parameterCd
        print(parameterCd)

        for parameter in parameterCd:
            try:
                url = 'https://help.waterdata.usgs.gov/code/parameter_cd_nm_query?' \
                      'parm_nm_cd={}&fmt=rdb'.format(parameter)
                response = requests.get(url)

                headerlines = []
                datalines = []
                count = 0

                text = response.text
                for line in text.splitlines():
                    if line[0] == "#":
                        headerlines.append(line)
                    elif count == 0:
                        columns = line.split()
                        count += 1
                    elif count == 1:
                        types = line.split()
                        count += 1
                    else:
                        datalines.append(line)

                data = "\n".join(datalines)

                variable_info_df = pd.read_csv(
                    StringIO(data),
                    sep="\t",
                    comment="#",
                    header=None,
                    names=columns,
                    dtype={"parameter_cd": str},
                )

            except Exception as e:
                print('Failed to get the variable information from the NWIS system.')
                raise

            variable_info[parameter] = [variable_info_df['SRSName'][0].split(',')[0], variable_info_df['parm_unit'][0]]

        return variable_info

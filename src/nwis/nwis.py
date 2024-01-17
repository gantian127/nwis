from __future__ import annotations

from datetime import datetime

import dataretrieval.nwis as nwis


class Nwis:
    def __init__(self):
        self._dataset = None

    @property
    def dataset(self):
        return self._dataset

    def get_data(self, site, start_date, end_date, data_type="iv", nc_output=None):
        # check user input
        Nwis._check_user_input(site, start_date, end_date, data_type, nc_output)

        # get data
        xr_dataset = Nwis._get_nwis_data(
            site, start_date, end_date, data_type, nc_output
        )
        self._dataset = xr_dataset

        return xr_dataset

    @staticmethod
    def _check_user_input(site, start_date, end_date, data_type, nc_output):
        # check site
        try:
            site_info = nwis.get_record(sites=site, service="site")
            if site_info.empty:
                raise ValueError("Incorrect USGS site number.")
        except Exception:
            raise ValueError("Incorrect USGS site number.")

        # check data_type
        if data_type not in ["dv", "iv"]:
            raise ValueError(
                f"Incorrect data type: 'dv' as daily value or 'iv' as instantaneous value {data_type} "
            )

        # check time
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

            if start_datetime > end_datetime:
                raise ValueError("Incorrect start date.")

        except Exception:
            raise ValueError("Incorrect date format, should be YYYY-MM-DD")

        # check csv_output
        if nc_output and nc_output[-3:] != ".nc":
            raise ValueError("Incorrect NetCDF file path.")

    @staticmethod
    def _get_nwis_data(site, start_date, end_date, data_type, nc_output):
        variable_info = {
            "00060": ["discharge", "cubic feet per second"],
            "00065": ["gage height", "feet"],
            "00010": ["water temperature", "degree celsius"],
            "80154": ["Suspended sediment discharge", "tons per day"],
            "80155": ["Total sediment discharge", "tons per day"],
            "80225": ["Bedload sediment discharge", "tons per day"],
        }

        # get site info
        site_info = nwis.get_record(sites=site, service="site")

        # get time series data frame
        record_df = nwis.get_record(
            sites=site, service=data_type, start=start_date, end=end_date
        )
        filter_names = list(variable_info.keys()) + [
            var_name + "_Mean" for var_name in variable_info.keys()
        ]
        var_col_names = [
            col_name for col_name in record_df.columns if col_name in filter_names
        ]

        if record_df.empty or not var_col_names:
            raise ValueError(
                f"Time series for discharge variables is not available for site {site}."
            )

        time_series_df = record_df[var_col_names]
        time_series_df.columns = [col_name[:5] for col_name in time_series_df.columns]

        # create xarray dataset
        xr_dataset = time_series_df.to_xarray()

        # assign datetime data to coordinate
        xr_dataset["datetime"] = time_series_df.index.values

        # add site metadata
        xr_dataset.attrs["site_name"] = site_info.station_nm[0]
        xr_dataset.attrs["site_code"] = site_info.site_no[0]
        xr_dataset.attrs["site_latitude"] = site_info.dec_lat_va[0]
        xr_dataset.attrs["site_longitude"] = site_info.dec_long_va[0]
        xr_dataset.attrs["site_altitude"] = site_info.alt_va[0]
        xr_dataset.attrs["site_coord_datum"] = site_info.dec_coord_datum_cd[0]

        # add variable metadata
        for var_name in time_series_df.columns:
            xr_dataset[var_name].attrs["variable_name"] = variable_info[var_name][0]
            xr_dataset[var_name].attrs["variable_unit"] = variable_info[var_name][1]
            xr_dataset[var_name].attrs["variable_data_type"] = (
                data_type if data_type == "dv" "daily value" else "instantaneous value"
            )

        # save output file as csv file
        if nc_output:
            try:
                xr_dataset.to_netcdf(nc_output)
            except Exception:
                print("Failed to write the data in the NetCDF file.")

        return xr_dataset

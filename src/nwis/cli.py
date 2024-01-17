from __future__ import annotations

import os

import click
from nwis import Nwis

from nwis._version import __version__


@click.command()
@click.version_option(version=__version__)
@click.option(
    "--site",
    required=True,
    help="USGS site number.",
)
@click.option(
    "--start_date",
    required=True,
    help="Start date of the time series as YYYY-MM-DD",
)
@click.option(
    "--end_date",
    required=True,
    help="End date of the time series as YYYY-MM-DD",
)
@click.option(
    "--data_type",
    default="iv",
    help="Data type of the time series. Daily value ('dv') or Instantaneous value ('iv')",
)
@click.argument("output", type=click.Path(exists=False))
def main(site, start_date, end_date, data_type, output):
    Nwis().get_data(
        site=site,
        start_date=start_date,
        end_date=end_date,
        data_type=data_type,
        nc_output=output,
    )
    if os.path.isfile(output):
        print("Done")

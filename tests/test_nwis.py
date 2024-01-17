import pytest
import os

import xarray

from nwis import Nwis


# test user input for get_data
def test_site():
    with pytest.raises(ValueError):
        Nwis().get_data(site='invalid_site', start_date='2020-01-01', end_date='2020-01-01')

    with pytest.raises(ValueError):
        Nwis().get_data(site='033390001', start_date='2020-01-01', end_date='2020-01-01')

    with pytest.raises(ValueError):
        Nwis().get_data(site='13339000', start_date='2020-01-01', end_date='2020-01-01')


def test_start_end_date():
    with pytest.raises(ValueError):  # start date format
        Nwis().get_data(site='03339000', start_date='2020/01/01', end_date='2020-01-01')

    with pytest.raises(ValueError):  # end date format
        Nwis().get_data(site='03339000', start_date='2020-01-01', end_date='2020/01/01')

    with pytest.raises(ValueError):  # test invalid start date value
        Nwis().get_data(site='03339000', start_date='2020-01-02', end_date='2020-01-01')


def test_data_type():
    with pytest.raises(ValueError):
        Nwis().get_data(site='03339000', start_date='2020-01-01', end_date='2020-01-01', data_type='invalid_type')


def test_nc_output_valid_dir(tmpdir):
    dataset = Nwis().get_data(site='03339000', start_date='2020-01-01', end_date='2020-01-01',
                              nc_output=os.path.join(tmpdir, 'test.nc'))

    assert isinstance(dataset, xarray.core.dataset.Dataset)
    assert len(os.listdir(tmpdir)) == 1


def test_nc_output_invalid_dir(tmpdir):
    with pytest.raises(ValueError):
        Nwis().get_data(site='03339000', start_date='2020-01-01', end_date='2020-01-01',
                        nc_output=os.path.join(tmpdir, 'error'))



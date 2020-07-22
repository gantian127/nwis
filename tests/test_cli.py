#!/usr/bin/env python
import os

from click.testing import CliRunner

from nwis.cli import main


def test_command_line_interface():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output

    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output


def test_output_argument(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        result = runner.invoke(main, ["--site=03339000", "--start_date=2020-01-01", "--end_date=2020-01-02", "demo.nc"])
        assert result.exit_code == 0
        assert len(os.listdir(tmpdir)) == 1


def test_site_option(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        result = runner.invoke(main, ["--site=error", "--start_date=2020-01-01", "--end_date=2020-01-02", "demo.nc"])
        assert result.exit_code != 0

        result = runner.invoke(main, ["--site=033390001", "--start_date=2020-01-01", "--end_date=2020-01-02", "demo.nc"])
        assert result.exit_code != 0

        result = runner.invoke(main, ["--site=13339000", "--start_date=2020-01-01", "--end_date=2020-01-02", "demo.nc"])
        assert result.exit_code != 0


def test_date_option(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        result = runner.invoke(main, ["--site=03339000", "--start_date=2020/01/01", "--end_date=2020-01-02", "demo.nc"])
        assert result.exit_code != 0

        result = runner.invoke(main, ["--site=03339000", "--start_date=2020-01-01", "--end_date=2020/01/02", "demo.nc"])
        assert result.exit_code != 0

        result = runner.invoke(main, ["--site=03339000", "--start_date=2020-01-02", "--end_date=2020-01-01", "demo.nc"])
        assert result.exit_code != 0


def test_data_type_option(tmpdir):
    runner = CliRunner()
    with tmpdir.as_cwd():
        result = runner.invoke(main, ["--site=3339000", "--start_date=2020-01-01", "--end_date=2020-01-02",
                                      "--data_type=error", "demo.nc"])
        assert result.exit_code != 0

        result = runner.invoke(main, ["--site=3339000", "--start_date=2020-01-01", "--end_date=2020-01-02",
                                      "--data_type=iv", "demo.nc"])
        assert result.exit_code == 0
        


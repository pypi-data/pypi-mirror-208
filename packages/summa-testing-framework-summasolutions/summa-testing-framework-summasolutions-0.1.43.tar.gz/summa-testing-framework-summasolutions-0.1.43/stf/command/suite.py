import click
from click_help_colors import HelpColorsCommand

import unittest
from HtmlTestRunner import HTMLTestRunner
from stf.report.result import HtmlResult
import stf.common.config as common_config
import stf.common.filesystem as common_filesystem
import importlib
import os
import sys

sys.path.insert(1, os.getcwd())


@click.command(
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
)
@click.argument('suite')
@click.option('-e', '--environment', 'environment')
@click.option('-b', '--browser', 'browser', required=False, default="chrome",
              type=click.Choice(['chrome', 'firefox', 'android']))
@click.option('-c', '--test-case', 'test_case', required=False, default=None)
def run(suite, environment, browser, test_case):
    click.secho("Suite: %s" % (suite), fg='blue')
    click.secho("Environment: %s" % (environment), fg='blue')
    click.secho("Browser: %s" % (browser), fg='blue')
    if test_case is not None:
        click.secho("Test Case: %s" % (test_case), fg='blue')

    module = importlib.import_module(common_filesystem.tests_folder + '.' + suite)
    class_ = getattr(module, 'TestCase')

    tests = unittest.TestLoader().getTestCaseNames(class_)
    test_suite = unittest.TestSuite()

    test_config = common_config.get_config(os.getcwd())

    for test_name in tests:
        if test_case is None or test_case == test_name:
            click.secho("Test: %s" % (test_name), fg='red')
            test_suite.addTest(class_(test_name, test_config, environment, browser))

    try:
        HTMLTestRunner(
            output="./reports/" + suite,
            report_name='report_' + browser,
            report_title='Acceptance Test Report',
            combine_reports = True,
            add_timestamp = False,
            template = common_config.get_report_template_path(),
            resultclass = HtmlResult
        ).run(test_suite)
    except:
        print("Unexpected error:", sys.exc_info()[0])
    #     print(sys.exc_info()[2])
    #     raise


@click.command(
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
)
@click.argument('name')
@click.option('-t', '--type', 'type', required=False, default="simple", type=click.Choice(common_config.suite_types))
def create(name, type):
    if common_filesystem.create_test_folder():
        click.secho('Test folder created successfully', fg='green')
    else:
        click.secho('Test folder already exists. Skipping creation...')

    new_suite_file = common_filesystem.copy_sample_test(name, type)
    click.secho("Test suite created successfully", fg='green')
    click.secho("Please check new file: %s" % new_suite_file, fg='blue')

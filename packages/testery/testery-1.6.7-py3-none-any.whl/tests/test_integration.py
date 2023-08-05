from os import getenv
from unittest.mock import patch, mock_open
from click.testing import CliRunner

from testery import cancel_test_run, create_test_run, report_test_run_cmd


def check_if_dev(params: list):
    use_dev = getenv('USE_TESTERY_DEV', 'False') == 'True'
    if use_dev:
        params.append('--testery-dev')


class TestCreateTestRun:
    def test_create_test_run_defaults(self, token: str, environment, project, cli_runner: CliRunner):
        params = [
                f'--token={token}',
                f'--project-key={project}',
                f'--environment-key={environment}',
        ]
        check_if_dev(params)

        result = cli_runner.invoke(create_test_run, params)

        assert result.exit_code == 0
        assert 'test_run_id: ' in result.output


class TestCancelTestRun:
    def test_cancel_test_run(self, token: str, cli_runner: CliRunner, start_test_run):
        params = [
                f'--token={token}',
                f'--test-run-id={start_test_run["id"]}'
        ]
        check_if_dev(params)

        result = cli_runner.invoke(cancel_test_run, params)

        assert result.exit_code == 0
        assert result.output == f'Cancelled test run {start_test_run["id"]}\n'

    def test_cancel_test_run_done_pass(self, token: str, test_runs: str, cli_runner: CliRunner):
        params = [f'--token={token}', f'--test-run-id={test_runs["pass"]}']
        check_if_dev(params)

        result = cli_runner.invoke(cancel_test_run, params)

        assert result.exit_code == 0
        assert result.output == 'Test run already done. Status: PASS\n'

    def test_cancel_test_run_done_fail(self, token: str, test_runs: str, cli_runner: CliRunner):
        params = [f'--token={token}', f'--test-run-id={test_runs["fail"]}']
        check_if_dev(params)

        result = cli_runner.invoke(cancel_test_run, params)

        assert result.exit_code == 0
        assert result.output == 'Test run already done. Status: FAIL\n'

    def test_cancel_test_run_done_cancel(self, token: str, test_runs: str, cli_runner: CliRunner):
        params = [f'--token={token}', f'--test-run-id={test_runs["canceled"]}']
        check_if_dev(params)

        result = cli_runner.invoke(cancel_test_run, params)

        assert result.exit_code == 0
        assert result.output == 'Test run already done. Status: CANCELED\n'


class TestReportTestRun:

    USE_TESTERY_DEV = getenv('USE_TESTERY_DEV', 'False') == 'True'

    def test_report_test_run_cmd_passed_sonarqube_no_ignored(self, token: str, test_runs: str, cli_runner: CliRunner):
        if self.USE_TESTERY_DEV:
            with open('./tests/testdata/dev_test_report_expected.txt') as file:
                expected = file.read().encode('ascii').strip()
        else:
            with open('./tests/testdata/prod_test_report_expected.txt') as file:
                expected = file.read().encode('ascii').strip()
        params = [f'--token={token}', f'--test-run-id={test_runs["pass"]}']
        check_if_dev(params)

        with patch('builtins.open', mock_open()) as mock_write:
            result = cli_runner.invoke(report_test_run_cmd, params)

        assert result.exit_code == 0
        mock_write.assert_called_once_with('results.xml', 'wb')
        mock_write().write.assert_called_once_with(expected)

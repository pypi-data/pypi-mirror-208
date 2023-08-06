from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import click
from humanfriendly.tables import format_pretty_table
from tinybird.client import TinyB
import yaml

from tinybird.feedback_manager import FeedbackManager
from tinybird.tb_cli_modules.common import CLIException


@ dataclass
class TestCase:
    name: str
    sql: str
    max_time: Optional[float]
    max_bytes_read: Optional[int]

    def __init__(self, name, sql, max_time: Optional[float] = None, max_bytes_read: Optional[int] = None):
        self.name = name
        self.sql = sql
        self.max_time = max_time
        self.max_bytes_read = max_bytes_read

    def __iter__(self):
        yield (self.name, {'sql': self.sql, 'max_time': self.max_time, 'max_bytes_read': self.max_bytes_read})


@ dataclass(frozen=True)
class Status():
    name: str
    abbreviation: str
    color: str
    description: str


PASS = Status(name='PASS', abbreviation='P', description='Pass', color='green')
PASS_OVER_TIME = Status(name='PASS_OVER_TIME', abbreviation='P*OT', description='Pass Over Time', color='cyan')
PASS_OVER_READ_BYTES = Status(name='PASS_OVER_READ_BYTES', abbreviation='P*OB', description='Pass Over Read Bytes', color='cyan')
PASS_OVER_TIME_AND_READ_BYTES = Status(name='PASS_OVER_TIME_AND_OVER_BYTES', abbreviation='P*OT*OB', description='Pass Over Time and Over Read Bytes', color='cyan')
FAILED = Status(name='FAIL', abbreviation='F', description='Fail', color='red')
ERROR = Status(name='ERROR', abbreviation='E', description='Error', color='bright_yellow')


@ dataclass()
class TestResult:
    name: str
    data: List[Dict]
    elapsed_time: float
    read_bytes: int
    max_elapsed_time: Optional[float]
    max_bytes_read: Optional[int]
    error: Optional[str]

    @ property
    def status(self) -> Status:
        if len(self.data) > 0:
            return FAILED
        elif self.max_bytes_read is not None and self.max_elapsed_time is not None and self.read_bytes > self.max_bytes_read and self.elapsed_time > self.max_elapsed_time:
            return PASS_OVER_TIME_AND_READ_BYTES
        elif self.max_bytes_read is not None and self.read_bytes > self.max_bytes_read:
            return PASS_OVER_READ_BYTES
        elif self.max_elapsed_time is not None and self.elapsed_time > self.max_elapsed_time:
            return PASS_OVER_TIME
        elif self.error:
            return ERROR
        return PASS

    def __dict__(self):
        return {
            'name': self.name,
            'data': self.data,
            'elapsed_time': self.elapsed_time,
            'read_bytes': self.read_bytes,
            'max_elapsed_time': self.max_elapsed_time,
            'max_bytes_read': self.max_bytes_read,
            'error': self.error,
            'status': self.status.name
        }


@dataclass()
class TestSummaryResults:
    filename: str
    results: List[TestResult]


def parse_file(file: str) -> Iterable[TestCase]:
    with Path(file).open('r') as f:
        definitions: List[Dict[str, Any]] = yaml.safe_load(f)

    for definition in definitions:
        try:
            for name, properties in definition.items():
                yield TestCase(
                    name,
                    properties.get('sql'),
                    properties.get('max_time'),
                    properties.get('max_bytes_read'))
        except Exception as e:
            click.echo(f"""Error: {FeedbackManager.error_exception(error=e)} reading file, check "{file}"->"{definition.get('name')}" """)


def generate_file(file: str, overwrite: bool = False) -> None:
    definitions = [
        dict(TestCase('this_test_should_pass', sql='SELECT * FROM numbers(5) WHERE 0')),
        dict(TestCase('this_test_should_fail', 'SELECT * FROM numbers(5) WHERE 1')),
        dict(TestCase('this_test_should_pass_over_time', 'SELECT * FROM numbers(5) WHERE 0', max_time=0.0000001)),
        dict(TestCase('this_test_should_pass_over_bytes', 'SELECT sum(number) AS total FROM numbers(5) HAVING total>1000', max_bytes_read=5)),
        dict(TestCase('this_test_should_pass_over_time_and_bytes', 'SELECT sum(number) AS total FROM numbers(5) HAVING total>1000', max_time=0.0000001, max_bytes_read=5)),
    ]

    p = Path(file)
    if ((not p.exists()) or overwrite):
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('w') as f:
            yaml.safe_dump(definitions, f)
        click.echo(FeedbackManager.success_generated_local_file(file=p))
    else:
        click.echo(FeedbackManager.error_file_already_exists(file=p))

    return


async def run_test_file(tb_client: TinyB, file: str) -> List[TestResult]:
    results: List[TestResult] = []
    for test_case in parse_file(file):
        if not test_case.sql:
            results.append(TestResult(
                name=test_case.name,
                data=[],
                elapsed_time=0,
                read_bytes=0,
                max_elapsed_time=test_case.max_time,
                max_bytes_read=test_case.max_bytes_read,
                error="Not sql"
            ))
            continue

        q = f"SELECT * FROM ({test_case.sql}) LIMIT 20 FORMAT JSON"
        try:
            test_response = await tb_client.query(q)
            results.append(TestResult(
                name=test_case.name,
                data=test_response['data'],
                elapsed_time=test_response.get('statistics', {}).get('elapsed', 0),
                read_bytes=test_response.get('statistics', {}).get('bytes_read', 0),
                max_elapsed_time=test_case.max_time,
                max_bytes_read=test_case.max_bytes_read,
                error=None
            ))

        except Exception as e:
            results.append(TestResult(
                name=test_case.name,
                data=[],
                elapsed_time=0,
                read_bytes=0,
                max_elapsed_time=test_case.max_time,
                max_bytes_read=test_case.max_bytes_read,
                error=str(e)
            ))

    return results


def test_run_summary(results: List[TestSummaryResults], only_fail: bool = False, verbose_level: int = 0):
    total_counts: Dict[Status, int] = {}
    for result in results:

        summary: List[Dict] = []
        for test in result.results:
            total_counts[test.status] = total_counts.get(test.status, 0) + 1

            # Skip the PASS tests if we only want the failed ones
            if only_fail and test.status in [PASS]:
                continue

            summary.append({
                'file': result.filename,
                'test': test.name,
                'status': test.status.description,
                'elapsed': f"{test.elapsed_time} ms",
            })

        click.echo(format_pretty_table(
            data=[d.values() for d in summary],
            column_names=list(summary[0].keys()) if len(summary) > 0 else []
        ))
        click.echo('\n')

        # Only display the data for debugging when wanting verbose
        if verbose_level == 0:
            continue

        failed_tests = [test for test in result.results if test.status is not PASS]
        for test in failed_tests:
            click.secho(f'{result.filename}::{test.name}', fg=test.status.color, bold=True, nl=True)

            if test.data:
                click.echo(format_pretty_table(
                    data=[d.values() for d in test.data],
                    column_names=list(test.data[0].keys()) if len(test.data) else []
                ))
                click.echo('\n')

            if test.error:
                click.secho(test.error, fg=test.status.color, bold=True, nl=True, err=True)

    if (len(total_counts)):
        click.echo("\nTotals:")
        for key_status, value_total in total_counts.items():
            code_summary = f"Total {key_status.description}: {value_total}"
            click.secho(code_summary, fg=key_status.color, bold=True, nl=True)

    if total_counts.get(FAILED, 0) > 0:
        raise CLIException(FeedbackManager.error_some_data_validation_have_failed())


def get_bare_url(url: str) -> str:
    if url.startswith("http://"):
        return url[7:]
    elif url.startswith("https://"):
        return url[8:]
    else:
        return url

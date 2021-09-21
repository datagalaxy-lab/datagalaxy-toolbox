import io
import re

from toolbox.__main__ import run


def test_run_with_valid_copy_attributes_args(mocker):
    copy_attributes_mock = mocker.patch('toolbox.__main__.copy_attributes')
    exit_mock = mocker.patch('sys.exit')
    code = run([
        'copy-attributes',
        '--url-source', 'https://source',
        '--url-target', 'https://target',
        '--token-source', 'token_source',
        '--token-target', 'token_target',
    ])

    assert code == 0
    assert exit_mock.call_count == 0
    assert copy_attributes_mock.call_count == 1


def test_run_with_missing_copy_attributes_args(mocker):
    mocker.patch('toolbox.__main__.copy_attributes')
    exit_mock = mocker.patch('sys.exit')
    mock_stderr = mocker.patch('sys.stderr', new_callable=io.StringIO)
    # missing --token-source, should call sys.exit(1)
    run([
        'copy-attributes',
        '--url-source', 'https://source',
        '--url-target', 'https://target',
        '--token-target', 'token_target',
    ])

    assert exit_mock.call_count == 1
    # should output the CLI usage to stderr
    assert re.compile('^usage:.*copy-attributes.*').match(mock_stderr.getvalue())


def test_run_with_valid_copy_glossary_args(mocker):
    copy_glossary_mock = mocker.patch('toolbox.__main__.copy_glossary')
    exit_mock = mocker.patch('sys.exit')
    code = run([
        'copy-glossary',
        '--url-source', 'https://source',
        '--url-target', 'https://target',
        '--token-source', 'token_source',
        '--token-target', 'token_target',
        '--workspace-source', 'workspace_source_name',
        '--workspace-target', 'workspace_target_name',
    ])

    assert code == 0
    assert exit_mock.call_count == 0
    assert copy_glossary_mock.call_count == 1


def test_run_with_valid_copy_glossary_args_without_optionnal_args(mocker):
    copy_glossary_mock = mocker.patch('toolbox.__main__.copy_glossary')
    exit_mock = mocker.patch('sys.exit')
    code = run([
        'copy-glossary',
        '--url-source', 'https://source',
        '--token-source', 'token_source',
        '--workspace-source', 'workspace_source_name',
        '--workspace-target', 'workspace_target_name',
    ])

    assert code == 0
    assert exit_mock.call_count == 0
    assert copy_glossary_mock.call_count == 1


def test_run_with_missing_copy_glossary_args(mocker):
    mocker.patch('toolbox.__main__.copy_glossary')
    exit_mock = mocker.patch('sys.exit')
    mock_stderr = mocker.patch('sys.stderr', new_callable=io.StringIO)
    # missing --url-source, should call sys.exit(1)
    run([
        'copy-glossary',
        '--url-target', 'https://target',
        '--token-source', 'token_source',
        '--token-target', 'token_target',
        '--workspace-source', 'workspace_source_name',
        '--workspace-target', 'workspace_target_name',
    ])

    assert exit_mock.call_count == 1
    # should output the CLI usage to stderr
    assert re.compile('^usage:.*copy-glossary.*').match(mock_stderr.getvalue())

from capm.config import load_config


def test_load_config_one_package():
    config = ''
    config += 'packages:\n'
    config += '  - id: codelimit\n'

    result = load_config(config)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].id == 'codelimit'


def test_load_config_two_packages():
    config = ''
    config += 'packages:\n'
    config += '  - id: codelimit\n'
    config += '  - id: ruff\n'

    result = load_config(config)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].id == 'codelimit'
    assert result[1].id == 'ruff'


def test_load_config_no_packages():
    config = ''

    result = load_config(config)

    assert isinstance(result, list)
    assert len(result) == 0

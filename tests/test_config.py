from capm.config import load_config


def test_load_config():
    config = ''
    config += '- id: codelimit\n'

    result = load_config(config)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].id == 'codelimit'

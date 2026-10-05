from capm.entities.PackageConfig import PackageConfig
from capm.entities.PackageDefinition import PackageDefinition
from capm.package.package import load_packages, _merge


def test_load_packages():
    packages = load_packages()

    assert len(packages) > 0
    assert 'xenon' in packages
    assert packages['xenon'].install_command == 'pip install xenon=={version}'
    assert packages['xenon'].entrypoint == 'xenon'


def test_merge_package_config():
    package_definition = PackageDefinition(
        image='test-image',
        version='1.0.0',
        type='test-type',
        args='--default-args',
        workspace_mode='rw',
        output_format='json'
    )

    package_config = PackageConfig(
        id='test-package',
        version=None,
        args=None,
        extra_args='--extra-args',
        output_format='markdown'
    )

    merged_config = _merge(package_definition, package_config)

    assert merged_config.id == 'test-package'
    assert merged_config.version == '1.0.0'
    assert merged_config.args == '--default-args'
    assert merged_config.extra_args == '--extra-args'
    assert merged_config.workspace_mode == 'rw'
    assert merged_config.output_format == 'markdown'

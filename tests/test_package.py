from capm.entities.PackageConfig import PackageConfig
from capm.entities.PackageDefinition import PackageDefinition
from capm.output.BufferStream import BufferStream
from capm.output.OutputFormat import OutputFormat
from capm.package.package import load_packages, _merge, run_package


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
        output_format=OutputFormat.text
    )

    package_config = PackageConfig(
        id='test-package',
        version=None,
        args=None,
        extra_args='--extra-args',
        output_format=OutputFormat.markdown
    )

    merged_config = _merge(package_definition, package_config)

    assert merged_config.id == 'test-package'
    assert merged_config.version == '1.0.0'
    assert merged_config.args == '--default-args'
    assert merged_config.extra_args == '--extra-args'
    assert merged_config.workspace_mode == 'rw'
    assert merged_config.output_format == OutputFormat.markdown


def test_run_package():
    package_definition = PackageDefinition(
        image='ubuntu:24.04',
        version='24.04',
        type='other',
        args='echo "Hello, World!"'
    )
    package_config = PackageConfig(id='test-package')
    output_stream = BufferStream(True)

    run_package(package_definition, package_config, output_stream)

    assert len(output_stream.buffer) == 2
    assert output_stream.buffer[0] == '[test-package] Package executed successfully'
    assert output_stream.buffer[1].startswith('Hello, World!')

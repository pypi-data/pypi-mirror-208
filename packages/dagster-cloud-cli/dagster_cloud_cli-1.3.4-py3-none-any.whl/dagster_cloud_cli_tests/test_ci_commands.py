import json
import os
import tempfile
from contextlib import contextmanager

import pytest
from dagster_cloud_cli.entrypoint import app
from typer.testing import CliRunner

DAGSTER_CLOUD_YAML = """
locations:
    - location_name: a
      code_source:
          package_name: a
    - location_name: b
      code_source:
          module_name: b
    - location_name: c
      build:
          directory: subdir
          registry: example.com/some-image-name
      code_source:
          module_name: c
      image: docker/c
      working_directory: c
"""


@contextmanager
def with_dagster_yaml(text):
    pwd = os.curdir
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.mkdir(os.path.join(tmpdir, "subdir"))
            yaml_path = os.path.join(tmpdir, "dagster_cloud.yaml")
            with open(yaml_path, "w") as f:
                f.write(text)
            os.chdir(tmpdir)
            yield tmpdir
    finally:
        os.chdir(pwd)


def test_ci_init(monkeypatch, mocker, empty_config) -> None:
    monkeypatch.setenv("DAGSTER_CLOUD_ORGANIZATION", "some-org")
    monkeypatch.setenv("DAGSTER_CLOUD_API_TOKEN", "some-org:fake-token")

    with tempfile.TemporaryDirectory() as statedir:
        with with_dagster_yaml(DAGSTER_CLOUD_YAML) as project_dir:
            runner = CliRunner()
            result = runner.invoke(app, ["ci", "init", f"--project-dir={project_dir}"])
            # statedir not specified
            assert result.exit_code
            monkeypatch.setenv("DAGSTER_BUILD_STATEDIR", statedir)
            result = runner.invoke(app, ["ci", "init", f"--project-dir={project_dir}"])
            assert result.exit_code, result.output
            assert "deployment" in result.output

            result = runner.invoke(
                app,
                [
                    "ci",
                    "init",
                    f"--project-dir={project_dir}",
                    "--deployment=prod",
                    "--commit-hash=hash-1234",
                    "--git-url=http://some-git-url",
                ],
            )
            assert not result.exit_code

            # 'status' should return a list of code locations
            result = runner.invoke(app, ["ci", "status"])
            assert not result.exit_code
            locations = [json.loads(line) for line in result.output.splitlines()]
            assert ["a", "b", "c"] == [loc["location_name"] for loc in locations]
            location_a = locations[0]
            assert location_a == {
                "build": {
                    "build_config": None,
                    "commit_hash": "hash-1234",
                    "git_url": "http://some-git-url",
                },
                "build_output": None,
                "location_name": "a",
                "deployment_name": "prod",
                "location_file": f"{project_dir}/dagster_cloud.yaml",
                "selected": True,
                "url": "https://some-org.dagster.cloud",
            }

        with with_dagster_yaml(DAGSTER_CLOUD_YAML) as project_dir:
            runner = CliRunner()
            monkeypatch.setenv("DAGSTER_BUILD_STATEDIR", statedir)
            result = runner.invoke(
                app,
                [
                    "ci",
                    "init",
                    f"--project-dir={project_dir}",
                    "--location-name=a",
                    "--location-name=c",
                    "--deployment=prod-1",
                ],
            )
            assert not result.exit_code, result.output
            result = runner.invoke(app, ["ci", "status"])
            print(result.output)
            locations = [json.loads(line) for line in result.output.splitlines()]
            assert ["a", "c"] == [loc["location_name"] for loc in locations]
            assert ["prod-1", "prod-1"] == [loc["deployment_name"] for loc in locations]

            # ensure branch deployment is used if available
            mocker.patch(
                "dagster_cloud_cli.commands.ci.get_deployment_from_context",
                return_value="branch-deployment",
            )
            result = runner.invoke(
                app,
                [
                    "ci",
                    "init",
                    f"--project-dir={project_dir}",
                    "--location-name=a",
                    "--deployment=prod-2",
                ],
            )
            assert not result.exit_code, result.output
            result = runner.invoke(app, ["ci", "status"])
            locations = [json.loads(line) for line in result.output.splitlines()]
            assert ["branch-deployment"] == [loc["deployment_name"] for loc in locations]


@pytest.fixture(params=["prod", "branch-deployment-1234"])
def deployment_name(request):
    return request.param


@pytest.fixture
def initialized_runner(deployment_name, monkeypatch):
    monkeypatch.setenv("DAGSTER_CLOUD_ORGANIZATION", "some-org")
    monkeypatch.setenv("DAGSTER_CLOUD_API_TOKEN", "some-org:some-token")
    with tempfile.TemporaryDirectory():
        with with_dagster_yaml(DAGSTER_CLOUD_YAML) as project_dir:
            statedir = os.path.join(project_dir, "tmp")
            monkeypatch.setenv("DAGSTER_BUILD_STATEDIR", statedir)

            runner = CliRunner()

            result = runner.invoke(
                app,
                [
                    "ci",
                    "init",
                    f"--project-dir={project_dir}",
                    f"--deployment={deployment_name}",
                    "--commit-hash=hash-4354",
                ],
            )
            assert not result.exit_code, result.output
            yield runner


def get_locations(runner):
    result = runner.invoke(app, ["ci", "status"])
    assert not result.exit_code
    return [json.loads(line) for line in result.output.splitlines()]


def test_ci_selection(initialized_runner: CliRunner) -> None:
    assert len(get_locations(initialized_runner)) == 3

    initialized_runner.invoke(app, ["ci", "locations-deselect", "a", "c"])
    selected = [
        location["location_name"]
        for location in get_locations(initialized_runner)
        if location["selected"]
    ]
    assert ["b"] == selected

    initialized_runner.invoke(app, ["ci", "locations-select", "c"])
    selected = [
        location["location_name"]
        for location in get_locations(initialized_runner)
        if location["selected"]
    ]
    assert ["b", "c"] == selected


def test_ci_build_docker(
    mocker, monkeypatch, deployment_name: str, initialized_runner: CliRunner
) -> None:
    assert len(get_locations(initialized_runner)) == 3

    monkeypatch.setenv("DAGSTER_CLOUD_API_TOKEN", "fake-token")
    mocker.patch(
        "dagster_cloud_cli.commands.ci.utils.get_registry_info",
        return_value={"registry_url": "example.com/image-registry"},
    )
    build_image = mocker.patch("dagster_cloud_cli.docker_utils.build_image", return_value=0)
    upload_image = mocker.patch("dagster_cloud_cli.docker_utils.upload_image", return_value=0)

    initialized_runner.invoke(app, ["ci", "locations-deselect", "a"])
    result = initialized_runner.invoke(app, ["ci", "build"])
    assert not result.exit_code, result.output

    assert len(build_image.call_args_list) == 2
    assert len(upload_image.call_args_list) == 2

    (b_build_dir, b_tag, b_registry_info), b_kwargs = build_image.call_args_list[0]
    (b_upload_tag, b_upload_registry_info), _ = upload_image.call_args_list[0]
    assert b_build_dir == "."
    assert b_tag.startswith(f"{deployment_name}-b")
    assert b_registry_info["registry_url"] == "example.com/image-registry"
    assert b_kwargs["base_image"] == "python:3.8-slim"
    assert b_kwargs["env_vars"] == []
    assert b_upload_tag == b_tag
    assert b_upload_registry_info == b_registry_info

    (c_build_dir, c_tag, c_registry_info), b_kwargs = build_image.call_args_list[1]
    assert c_tag.startswith(f"{deployment_name}-c")
    assert c_build_dir == "subdir"

    # test overriding some defaults
    build_image.reset_mock()
    upload_image.reset_mock()
    result = initialized_runner.invoke(
        app,
        [
            "ci",
            "build",
            "--docker-base-image=custom-base-image",
            "--docker-env=A=1",
            "--docker-env=B=2",
        ],
    )
    assert not result.exit_code, result.output

    (b_build_dir, b_tag, b_registry_info), b_kwargs = build_image.call_args_list[0]
    assert b_build_dir == "."
    assert b_registry_info["registry_url"] == "example.com/image-registry"
    assert b_kwargs["base_image"] == "custom-base-image"
    assert b_kwargs["env_vars"] == ["A=1", "B=2"]


def test_ci_deploy_docker(
    mocker, monkeypatch, deployment_name: str, initialized_runner: CliRunner
) -> None:
    monkeypatch.setenv("DAGSTER_CLOUD_API_TOKEN", "fake-token")
    mocker.patch(
        "dagster_cloud_cli.commands.ci.utils.get_registry_info",
        return_value={"registry_url": "example.com/image-registry"},
    )
    mocker.patch("dagster_cloud_cli.docker_utils.build_image", return_value=0)
    mocker.patch("dagster_cloud_cli.docker_utils.upload_image", return_value=0)
    update_code_location = mocker.patch("dagster_cloud_cli.gql.add_or_update_code_location")
    wait_for_load = mocker.patch("dagster_cloud_cli.commands.ci.wait_for_load")

    initialized_runner.invoke(app, ["ci", "locations-deselect", "a"])
    result = initialized_runner.invoke(app, ["ci", "build"])
    assert not result.exit_code, result.output
    print(result.output)
    result = initialized_runner.invoke(app, ["ci", "deploy"])
    assert not result.exit_code, result.output
    print(result.output)

    assert len(update_code_location.call_args_list) == 2
    assert len(wait_for_load.call_args_list) == 1

    (gql_shim, b_update_args), _ = update_code_location.call_args_list[0]
    (_, c_update_args), _ = update_code_location.call_args_list[1]
    assert b_update_args == {
        "code_source": {"module_name": "b"},
        "git": {"commit_hash": "hash-4354"},
        "image": f"example.com/image-registry:{deployment_name}-b-hash-4354",
        "location_name": "b",
    }
    assert gql_shim.url == f"https://some-org.dagster.cloud/{deployment_name}/graphql"
    assert c_update_args == {
        "code_source": {"module_name": "c"},
        "git": {"commit_hash": "hash-4354"},
        "image": f"example.com/image-registry:{deployment_name}-c-hash-4354",
        "location_name": "c",
        "working_directory": "c",
    }
    (_, wait_location_args), wait_kwargs = wait_for_load.call_args_list[0]
    assert wait_location_args == ["b", "c"]
    assert wait_kwargs["url"] == f"https://some-org.dagster.cloud/{deployment_name}"


def test_ci_set_build_output(initialized_runner: CliRunner):
    result = initialized_runner.invoke(app, ["ci", "set-build-output", "--image-tag=1234"])
    assert result.exit_code
    assert "Error: No build:registry:" in result.output

    initialized_runner.invoke(app, ["ci", "locations-deselect", "a", "b"])
    result = initialized_runner.invoke(app, ["ci", "set-build-output", "--image-tag=1234"])
    assert not result.exit_code, result.output
    print(result.output)
    c_location = [
        location
        for location in get_locations(initialized_runner)
        if location["location_name"] == "c"
    ][0]
    assert c_location["build_output"]["image"] == "example.com/some-image-name:1234"


def test_ci_deploy_pex(
    mocker, monkeypatch, deployment_name: str, initialized_runner: CliRunner
) -> None:
    monkeypatch.setenv("DAGSTER_CLOUD_API_TOKEN", "fake-token")
    build_upload_pex = mocker.patch(
        "dagster_cloud_cli.pex_utils.build_upload_pex",
        return_value={"image": "pex-base-image", "pex_tag": "deps-123.pex:source-456.pex"},
    )
    update_code_location = mocker.patch("dagster_cloud_cli.gql.add_or_update_code_location")
    wait_for_load = mocker.patch("dagster_cloud_cli.commands.ci.wait_for_load")

    initialized_runner.invoke(app, ["ci", "locations-deselect", "a"])
    result = initialized_runner.invoke(
        app,
        [
            "ci",
            "build",
            "--build-strategy=python-executable",
            "--pex-deps-cache-from=from-cache",
            "--pex-deps-cache-to=to-cache",
        ],
    )
    assert not result.exit_code, result.output
    print(result.output)
    _, b_build_upload_pex_kwargs = build_upload_pex.call_args_list[0]
    assert b_build_upload_pex_kwargs["kwargs"]["deps_cache_from"] == "from-cache"
    assert b_build_upload_pex_kwargs["kwargs"]["deps_cache_to"] == "to-cache"

    result = initialized_runner.invoke(app, ["ci", "deploy"])
    assert not result.exit_code, result.output
    print(result.output)

    assert len(update_code_location.call_args_list) == 2
    assert len(wait_for_load.call_args_list) == 1

    (gql_shim, b_update_args), _ = update_code_location.call_args_list[0]
    (_, c_update_args), _ = update_code_location.call_args_list[1]
    assert b_update_args == {
        "location_name": "b",
        "code_source": {"module_name": "b"},
        "git": {"commit_hash": "hash-4354"},
        "image": "pex-base-image",
        "pex_metadata": {"pex_tag": "deps-123.pex:source-456.pex"},
    }
    assert gql_shim.url == f"https://some-org.dagster.cloud/{deployment_name}/graphql"
    assert c_update_args == {
        "location_name": "c",
        "code_source": {"module_name": "c"},
        "git": {"commit_hash": "hash-4354"},
        "image": "pex-base-image",
        "pex_metadata": {"pex_tag": "deps-123.pex:source-456.pex"},
        "working_directory": "c",
    }
    (_, wait_location_args), wait_kwargs = wait_for_load.call_args_list[0]
    assert wait_location_args == ["b", "c"]
    assert wait_kwargs["url"] == f"https://some-org.dagster.cloud/{deployment_name}"


def test_ci_branch_deployment(
    mocker,
    monkeypatch,
    empty_config,
) -> None:
    monkeypatch.setenv("DAGSTER_CLOUD_API_TOKEN", "fake-token")
    mocker.patch(
        "dagster_cloud_cli.commands.ci.get_deployment_from_context", return_value="branch-dep-name"
    )
    with with_dagster_yaml(DAGSTER_CLOUD_YAML) as project_dir:
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "ci",
                "branch-deployment",
                project_dir,
            ],
        )
        assert result.exit_code

        monkeypatch.setenv("DAGSTER_CLOUD_ORGANIZATION", "someorg")
        result = runner.invoke(
            app,
            [
                "ci",
                "branch-deployment",
                project_dir,
            ],
        )
        assert not result.exit_code
        assert result.output.strip() == "branch-dep-name"

        monkeypatch.delenv("DAGSTER_CLOUD_ORGANIZATION")
        monkeypatch.setenv("DAGSTER_CLOUD_URL", "https://someurl")
        assert not result.exit_code
        assert result.output.strip() == "branch-dep-name"

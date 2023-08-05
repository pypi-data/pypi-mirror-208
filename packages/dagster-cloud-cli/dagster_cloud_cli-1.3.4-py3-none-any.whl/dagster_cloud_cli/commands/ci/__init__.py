# CI/CD agnostic commands that work with the current CI/CD system

import json
import logging
import os
import pathlib
import shutil
import sys
from collections import Counter
from enum import Enum
from typing import Any, Dict, List, Optional

import typer
from typer import Typer

from dagster_cloud_cli import docker_utils, gql, pex_utils, ui
from dagster_cloud_cli.commands.ci import utils
from dagster_cloud_cli.commands.workspace import wait_for_load
from dagster_cloud_cli.config_utils import (
    AGENT_HEARTBEAT_TIMEOUT_OPTION,
    DAGSTER_ENV_OPTION,
    LOCATION_LOAD_TIMEOUT_OPTION,
    ORGANIZATION_OPTION,
    TOKEN_ENV_VAR_NAME,
    URL_ENV_VAR_NAME,
    dagster_cloud_options,
    get_location_document,
    get_org_url,
)
from dagster_cloud_cli.core import pex_builder, pydantic_yaml

from .. import metrics
from . import checks, state

app = Typer(hidden=True, help="CI/CD agnostic commands")
from dagster_cloud_cli.core.pex_builder import code_location, deps, github_context, parse_workspace
from dagster_cloud_cli.types import CliEventTags


@app.command(help="Print json information about current CI/CD environment")
def inspect(project_dir: str):
    project_dir = os.path.abspath(project_dir)
    source = metrics.get_source()
    info = {"source": str(source), "project-dir": project_dir}
    if source == CliEventTags.source.github:
        info.update(load_github_info(project_dir))
    print(json.dumps(info))


def load_github_info(project_dir: str) -> Dict[str, Any]:
    event = github_context.get_github_event(project_dir)
    return {
        "git-url": event.commit_url,
        "commit-hash": event.github_sha,
    }


@app.command(
    help=(
        "Print the branch deployment name (or nothing) for the current context. Creates a new"
        " branch deployment if necessary. Requires DAGSTER_CLOUD_ORGANIZATION and"
        " DAGSTER_CLOUD_API_TOKEN environment variables."
    )
)
def branch_deployment(
    project_dir: str,
    organization: Optional[str] = ORGANIZATION_OPTION,
    dagster_env: Optional[str] = DAGSTER_ENV_OPTION,
):
    try:
        if organization:
            url = get_org_url(organization, dagster_env)
        else:
            url = os.environ[URL_ENV_VAR_NAME]
        print(get_deployment_from_context(url, project_dir))
    except ValueError as err:
        logging.error(
            f"cannot determine branch deployment: {err}",
        )
        sys.exit(1)


def get_deployment_from_context(url, project_dir: str) -> str:
    source = metrics.get_source()
    if source == CliEventTags.source.github:
        event = github_context.get_github_event(project_dir)
        api_token = os.environ[TOKEN_ENV_VAR_NAME]
        deployment_name = code_location.create_or_update_branch_deployment_from_github_context(
            url, api_token, event
        )
        if not deployment_name:
            raise ValueError(
                f"could not determine branch deployment for PR {event.pull_request_id}"
            )

        return deployment_name
    else:
        raise ValueError(f"unsupported for {source}")


@app.command(help="Validate configuration")
def check(
    organization: Optional[str] = ORGANIZATION_OPTION,
    dagster_env: Optional[str] = DAGSTER_ENV_OPTION,
    project_dir: str = typer.Option("."),
    dagster_cloud_yaml_path: str = "dagster_cloud.yaml",
    dagster_cloud_yaml_check: checks.Check = typer.Option("error"),
    dagster_cloud_connect_check: checks.Check = typer.Option("error"),
):
    project_path = pathlib.Path(project_dir)

    verdicts = []
    if dagster_cloud_yaml_check != checks.Check.skip:
        yaml_path = project_path / dagster_cloud_yaml_path
        result = checks.check_dagster_cloud_yaml(yaml_path)
        verdicts.append(
            checks.handle_result(
                result,
                dagster_cloud_yaml_check,
                prefix_message="[dagster_cloud.yaml] ",
                success_message="Checked OK",
                failure_message=(
                    "Invalid dagster_cloud.yaml, please see"
                    " https://docs.dagster.io/dagster-cloud/managing-deployments/dagster-cloud-yaml"
                ),
            )
        )

    if dagster_cloud_connect_check != checks.Check.skip:
        if not organization:
            raise ui.error(
                "DAGSTER_CLOUD_ORGANIZATION or --organization required for connection check."
            )
        url = get_org_url(organization, dagster_env)
        result = checks.check_connect_dagster_cloud(url)
        verdicts.append(
            checks.handle_result(
                result,
                dagster_cloud_connect_check,
                prefix_message="[dagster.cloud connection] ",
                success_message="Able to connect to dagster.cloud",
                failure_message="Unable to connect to dagster.cloud",
            )
        )

    verdict_counts = Counter(verdicts)
    ui.print(f"Passed: {verdict_counts[checks.Verdict.passed]}")
    if verdict_counts[checks.Verdict.warning]:
        ui.print(f"Warnings: {verdict_counts[checks.Verdict.warning]}")
    if verdict_counts[checks.Verdict.failed]:
        ui.print(ui.red(f"Failed: {verdict_counts[checks.Verdict.failed]}"))
        sys.exit(1)


STATEDIR_OPTION = typer.Option(..., envvar="DAGSTER_BUILD_STATEDIR")


@app.command(help="Initialize a build session")
@dagster_cloud_options(allow_empty=False, allow_empty_deployment=True, requires_url=False)
def init(
    organization: str,
    deployment: Optional[str],
    dagster_env: Optional[str] = DAGSTER_ENV_OPTION,
    project_dir: str = typer.Option("."),
    dagster_cloud_yaml_path: str = "dagster_cloud.yaml",
    statedir: str = STATEDIR_OPTION,
    clean_statedir: bool = typer.Option(True, help="Delete any existing files in statedir"),
    location_name: List[str] = typer.Option([]),
    git_url: Optional[str] = None,
    commit_hash: Optional[str] = None,
):
    yaml_path = pathlib.Path(project_dir) / dagster_cloud_yaml_path
    locations_def = pydantic_yaml.load_dagster_cloud_yaml(yaml_path.read_text())
    locations = locations_def.locations
    if location_name:
        selected_locations = set(location_name)
        unknown = selected_locations - set(location.location_name for location in locations)
        if unknown:
            raise ui.error(f"Locations not found in {dagster_cloud_yaml_path}: {unknown}")
        locations = [
            location for location in locations if location.location_name in selected_locations
        ]
    url = get_org_url(organization, dagster_env)
    # Deploy to the branch deployment for the current context. If there is no branch deployment
    # available (eg. if not in a PR) then we fallback to the --deployment flag.
    try:
        branch_deployment = get_deployment_from_context(url, project_dir)
        if deployment:
            ui.print(
                f"Deploying to branch deployment {branch_deployment}, ignoring"
                f" --deployment={deployment}"
            )
        deployment = branch_deployment
    except ValueError as err:
        if deployment:
            ui.print(f"Deploying to {deployment}. No branch deployment ({err}).")
        else:
            raise ui.error(
                f"Cannot determine deployment name in current context ({err}). Please specify"
                " --deployment."
            )

    if clean_statedir and os.path.exists(statedir):
        shutil.rmtree(statedir, ignore_errors=True)
    state_store = state.FileStore(statedir=statedir)

    ui.print(f"Initializing {statedir}")
    for location in locations:
        location_state = state.LocationState(
            url=url,
            deployment_name=deployment,
            location_file=str(yaml_path.absolute()),
            location_name=location.location_name,
            build=state.BuildMetadata(
                git_url=git_url, commit_hash=commit_hash, build_config=location.build
            ),
            build_output=None,
        )
        state_store.save(location_state)

    ui.print(
        f"Initialized {statedir} to build and deploying following locations for directory"
        f" {project_dir}:"
    )
    for location in state_store.list_locations():
        ui.print(f"- {location.location_name}")


@app.command(help="Show status of the current build session")
def status(
    statedir: str = STATEDIR_OPTION,
):
    state_store = state.FileStore(statedir=statedir)
    for location in state_store.list_locations():
        ui.print(location.json())


@app.command(help="List locations in the current build session")
def locations_list(
    statedir: str = STATEDIR_OPTION,
):
    state_store = state.FileStore(statedir=statedir)
    for location in state_store.list_locations():
        if location.selected:
            ui.print(f"{location.location_name}")
        else:
            ui.print(f"{location.location_name} DESELECTED")


@app.command(help="Mark the specified locations as excluded from the current build session")
def locations_deselect(
    location_names: List[str],
    statedir: str = typer.Option(None, envvar="DAGSTER_BUILD_STATEDIR"),
):
    state_store = state.FileStore(statedir=statedir)
    state_store.deselect(location_names)
    ui.print("Deselected locations: {locations_names}")


@app.command(help="Mark the specified locations as included in the current build session")
def locations_select(
    location_names: List[str],
    statedir: str = typer.Option(None, envvar="DAGSTER_BUILD_STATEDIR"),
):
    state_store = state.FileStore(statedir=statedir)
    state_store.select(location_names)
    ui.print("Deselected locations: {locations_names}")


def _get_selected_locations(
    state_store: state.Store, location_name: List[str]
) -> Dict[str, state.LocationState]:
    requested_locations = set(location_name)
    selected = {
        location.location_name: location
        for location in state_store.list_selected_locations()
        if not requested_locations or location.location_name in requested_locations
    }
    unknown_locations = requested_locations - set(selected)
    if unknown_locations:
        raise ui.error(f"Unknown or deselected location names requested: {unknown_locations}")
    return selected


class BuildStrategy(Enum):
    pex = "python-executable"
    docker = "docker"


@app.command(help="Build selected or requested locations")
def build(
    statedir: str = typer.Option(None, envvar="DAGSTER_BUILD_STATEDIR"),
    location_name: List[str] = typer.Option([]),
    build_directory: Optional[str] = typer.Option(
        None,
        help=(
            "Directory root for building this code location. Read from dagster_cloud.yaml by"
            " default."
        ),
    ),
    build_strategy: BuildStrategy = typer.Option(
        "docker",
        help=(
            "Build strategy used to build code locations. 'docker' builds a docker image."
            " 'python-executable' builds a set of pex files."
        ),
    ),
    docker_image_tag: Optional[str] = typer.Option(
        None, help="Tag for built docker image. Auto-generated by default."
    ),
    docker_base_image: Optional[str] = typer.Option(
        None,
        help="Base image used to build the docker image for --build-strategy=docker.",
    ),
    docker_env: List[str] = typer.Option([], help="Env vars for docker builds."),
    python_version: str = typer.Option(
        "3.8",
        help=(
            "Python version used to build the python-executable; or to determine the default base"
            " image for docker."
        ),
    ),
    pex_build_method: deps.BuildMethod = typer.Option("local"),
    pex_deps_cache_from: Optional[str] = None,
    pex_deps_cache_to: Optional[str] = None,
    pex_base_image_tag: Optional[str] = typer.Option(
        None,
        help="Base image used to run python executable for --build-strategy=python-executable.",
    ),
) -> None:
    if python_version:
        # ensure version is parseable
        pex_builder.util.parse_python_version(python_version)

    if build_strategy == BuildStrategy.pex:
        if docker_base_image or docker_image_tag:
            raise ui.error(
                "--base-image or --image-tag not supported for --build-strategy=python-executable."
            )

    state_store = state.FileStore(statedir=statedir)
    locations = _get_selected_locations(state_store, location_name)
    ui.print("Going to build the following locations:")
    for name in locations:
        ui.print(f"- {name}")

    for name, location_state in locations.items():
        configured_build_directory = (
            location_state.build.build_config.directory
            if (location_state.build.build_config and location_state.build.build_config.directory)
            else None
        )
        if build_directory and configured_build_directory:
            ui.warn(
                f"Overriding configured build:directory:{configured_build_directory!r} with"
                f" cmdline provided --build-directory={build_directory!r}"
            )
            location_build_dir = build_directory
        elif (not build_directory) and configured_build_directory:
            location_build_dir = configured_build_directory
        elif build_directory and (not configured_build_directory):
            location_build_dir = build_directory
        else:
            location_build_dir = "."

        if build_strategy == BuildStrategy.docker:
            if not docker_base_image:
                docker_base_image = f"python:{python_version}-slim"

            ui.print(
                f"Building docker image for location {name} using base image {docker_base_image}"
            )
            docker_utils.verify_docker()
            registry_info = utils.get_registry_info(location_state.url)

            docker_image_tag = docker_utils.default_image_tag(
                location_state.deployment_name, name, location_state.build.commit_hash
            )

            retval = docker_utils.build_image(
                location_build_dir,
                docker_image_tag,
                registry_info,
                env_vars=docker_env,
                base_image=docker_base_image,
            )
            if retval != 0:
                raise ui.error(f"Failed to build docker image for location {name}")

            retval = docker_utils.upload_image(docker_image_tag, registry_info)
            if retval != 0:
                raise ui.error(f"Failed to upload docker image for location {name}")

            image = f'{registry_info["registry_url"]}:{docker_image_tag}'

            # Update and save build state
            location_state.build_output = state.DockerBuildOutput(image=image)
            state_store.save(location_state)
            ui.print(f"Built and uploaded image {image} for location {name}")
        elif build_strategy == BuildStrategy.pex:
            pex_location = parse_workspace.Location(
                name,
                directory=location_build_dir,
                build_folder=location_build_dir,
                location_file=location_state.location_file,
            )
            location_kwargs = pex_utils.build_upload_pex(
                url=location_state.url,
                api_token=os.environ[TOKEN_ENV_VAR_NAME],
                location=pex_location,
                build_method=pex_build_method,
                kwargs={
                    "python_version": python_version,
                    "base_image_tag": pex_base_image_tag,
                    "deps_cache_from": pex_deps_cache_from,
                    "deps_cache_to": pex_deps_cache_to,
                },
            )
            location_state.build_output = state.PexBuildOutput(
                python_version=python_version,
                image=location_kwargs["image"],
                pex_tag=location_kwargs["pex_tag"],
            )
            state_store.save(location_state)
            ui.print(
                f"Build and uploaded python executable {location_state.build_output.pex_tag} for"
                f" location {name}"
            )


@app.command(help="Update the current build session for an externally built docker image.")
def set_build_output(
    statedir: str = typer.Option(None, envvar="DAGSTER_BUILD_STATEDIR"),
    location_name: List[str] = typer.Option([]),
    image_tag: str = typer.Option(
        ...,
        help=(
            "Tag for the built docker image. Note the registry must be specified in"
            " dagster_cloud.yaml."
        ),
    ),
) -> None:
    state_store = state.FileStore(statedir=statedir)
    locations = _get_selected_locations(state_store, location_name)
    ui.print("Going to update the following locations:")
    for name in locations:
        ui.print(f"- {name}")

    # validation pass - computes the full image name for all locations
    images = {}
    for name, location_state in locations.items():
        configured_defs = pydantic_yaml.load_dagster_cloud_yaml(
            open(location_state.location_file, encoding="utf-8").read()
        )
        location_defs = [loc for loc in configured_defs.locations if loc.location_name == name]
        if not location_defs:
            raise ui.error(f"Location {name} not found in {location_state.location_file}")
        location_def = location_defs[0]
        registry = location_def.build.registry if location_def.build else None
        if not registry:
            raise ui.error(
                f"No build:registry: defined for location {name} in {location_state.location_file}"
            )

        images[name] = f"{registry}:{image_tag}"

    # save pass - save full image name computed in the previous pass for all locations
    for name, location_state in locations.items():
        # Update and save build state
        location_state.build_output = state.DockerBuildOutput(image=images[name])
        state_store.save(location_state)
        ui.print(f"Recorded image {images[name]} for location {name}")
    ui.print("Use 'ci deploy' to update dagster-cloud.")


@app.command(help="Deploy built code locations to dagster cloud.")
def deploy(
    statedir: str = typer.Option(None, envvar="DAGSTER_BUILD_STATEDIR"),
    location_name: List[str] = typer.Option([]),
    location_load_timeout: int = LOCATION_LOAD_TIMEOUT_OPTION,
    agent_heartbeat_timeout: int = AGENT_HEARTBEAT_TIMEOUT_OPTION,
):
    state_store = state.FileStore(statedir=statedir)
    locations = _get_selected_locations(state_store, location_name)
    ui.print("Going deploy the following locations:")

    built_locations = []
    for name, location_state in locations.items():
        if location_state.build_output:
            status = "Ready to deploy"
            built_locations.append(location_state)
        else:
            status = "Not ready to deploy"
        ui.print(f"- {name} [{status}]")

    if len(built_locations) < len(locations):
        raise ui.error(
            "Cannot deploy because locations have not been built. Use 'ci build' to build"
            " locations."
        )

    if not built_locations:
        ui.print("No locations to deploy")
        return

    for location_state in built_locations:
        location_args = {
            "image": location_state.build_output.image,
            "location_file": location_state.location_file,
            "git_url": location_state.build.git_url,
            "commit_hash": location_state.build.commit_hash,
        }
        if location_state.build_output.strategy == "python-executable":
            location_args["pex_tag"] = location_state.build_output.pex_tag
        with utils.client_from_env(location_state.url, location_state.deployment_name) as client:
            location_document = get_location_document(location_state.location_name, location_args)
            gql.add_or_update_code_location(client, location_document)
            ui.print(f"Updated code location {location_state.location_name} in dagster-cloud")

    url = built_locations[0].url + "/" + built_locations[0].deployment_name
    with utils.client_from_env(
        built_locations[0].url, deployment=built_locations[0].deployment_name
    ) as client:
        wait_for_load(
            client,
            [location.location_name for location in built_locations],
            location_load_timeout=location_load_timeout,
            agent_heartbeat_timeout=agent_heartbeat_timeout,
            url=url,
        )

    ui.print(f"View the status of your locations at {url}/locations.")

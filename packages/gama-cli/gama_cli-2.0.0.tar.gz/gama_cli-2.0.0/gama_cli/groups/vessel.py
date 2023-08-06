import os
from typing import List
import click

from gama_config.gama_vessel import (
    Variant,
    Network,
    Mode,
    read_vessel_config,
    get_vessel_config_path,
    LogLevel,
    write_vessel_config,
    GamaVesselConfig,
)
from gama_cli.helpers import (
    call,
    docker_compose_path,
    get_project_root,
    docker_bake,
    get_gama_version,
    maybe_ignore_build,
    maybe_ignore_prod,
)
from python_on_whales.docker_client import DockerClient
from python_on_whales.utils import ValidPath


DOCKER_VESSEL = docker_compose_path("vessel/docker-compose.yaml")
DOCKER_VESSEL_GPU = docker_compose_path("vessel/docker-compose.gpu.yaml")
DOCKER_VESSEL_VARIANT_EDUCAT = docker_compose_path("vessel/docker-compose.variant-educat.yaml")
DOCKER_VESSEL_VARIANT_BRAVO = docker_compose_path("vessel/docker-compose.variant-bravo.yaml")
DOCKER_VESSEL_PROD = docker_compose_path("vessel/docker-compose.prod.yaml")
DOCKER_VESSEL_DEV = docker_compose_path("vessel/docker-compose.dev.yaml")
DOCKER_VESSEL_NETWORK_SHARED = docker_compose_path("vessel/docker-compose.network-shared.yaml")
DOCKER_VESSEL_NETWORK_VPN = docker_compose_path("vessel/docker-compose.network-vpn.yaml")
DOCKER_VESSEL_NETWORK_HOST = docker_compose_path("vessel/docker-compose.network-host.yaml")

SERVICES = [
    "gama_ui",
    "gama_chart_tiler",
    "gama_chart_api",
    "gama_vessel",
    "gama_greenstream",
    "gama_docs",
    "lookout",
    "groot",
]


def _get_compose_files(
    network: Network = Network.SHARED,
    gpu: bool = False,
    variant: Variant = Variant.WHISKEY_BRAVO,
    prod: bool = False,
) -> List[ValidPath]:
    compose_files: List[ValidPath] = [DOCKER_VESSEL]

    if not prod:
        compose_files.append(DOCKER_VESSEL_DEV)
    if variant == variant.EDUCAT:
        compose_files.append(DOCKER_VESSEL_VARIANT_EDUCAT)
    if variant == variant.WHISKEY_BRAVO:
        compose_files.append(DOCKER_VESSEL_VARIANT_BRAVO)
    if gpu:
        compose_files.append(DOCKER_VESSEL_GPU)
    if network == Network.SHARED:
        compose_files.append(DOCKER_VESSEL_NETWORK_SHARED)
    if network == Network.VPN:
        compose_files.append(DOCKER_VESSEL_NETWORK_VPN)
    if network == Network.HOST:
        compose_files.append(DOCKER_VESSEL_NETWORK_HOST)
    if prod:
        compose_files.append(DOCKER_VESSEL_PROD)

    return compose_files


@click.group(help="Commands for the vessel")
def vessel():
    pass


@click.command(name="build")
@click.argument(
    "service",
    required=False,
    type=click.Choice(SERVICES),
)
@click.argument("args", nargs=-1)
def build(service: str, args: List[str]):  # type: ignore
    """Build the vessel"""
    config = read_vessel_config()

    docker = DockerClient(
        compose_files=_get_compose_files(),
        compose_project_directory=get_project_root(),
    )

    os.environ["GAMA_VARIANT"] = config.variant.value

    if service:
        docker.compose.build([service])
        return

    docker.compose.build(["gama_ui", "gama_chart_tiler", "gama_chart_api", "gama_vessel"])

    if config.extensions.lookout:
        docker.compose.build(["lookout"])

    if config.extensions.groot:
        docker.compose.build(["groot"])


@click.command(name="bake")
@click.option(
    "--variant",
    type=click.Choice(Variant),  # type: ignore
    required=True,
    help="The variant to bake",
)
@click.option(
    "--version",
    type=str,
    required=True,
    help="The version to bake. Default: latest",
)
@click.option(
    "--push",
    type=bool,
    default=False,
    is_flag=True,
    help="Should we push the images to the registry? Default: False",
)
@click.argument("services", nargs=-1)
def bake(variant: Variant, version: str, push: bool, services: List[str]):  # type: ignore
    """Bakes the vessel docker containers"""
    compose_files = _get_compose_files(variant=variant)
    docker_bake(
        version=version,
        services=services,
        push=push,
        compose_files=compose_files,
    )


@click.command(name="test-ui")
def test_ui():  # type: ignore
    """Runs test for the ui"""
    docker = DockerClient(
        compose_files=_get_compose_files(),
        compose_project_directory=get_project_root(),
    )
    docker.compose.run("gama_ui", ["yarn", "test"])


@click.command(name="test-ros")
def test_ros():  # type: ignore
    """Runs test for the ros nodes"""
    docker = DockerClient(
        compose_files=_get_compose_files(),
        compose_project_directory=get_project_root(),
    )
    docker.compose.run(
        "gama_vessel",
        ["/bin/bash", "-c", "source /home/ros/.profile && platform ros test"],
    )


@click.command(name="test-e2e")
def test_e2e():  # type: ignore
    """Runs UI e2e tests (assuming all the containers are up)"""
    call("cd ./projects/gama_ui && yarn test:e2e")


@click.command(name="test")
def test():  # type: ignore
    """Runs test for the all vessel code"""
    call("gama_cli vessel test-ui")
    call("gama_cli vessel test-ros")


@click.command(name="lint-ui")
@click.argument("args", nargs=-1)
def lint_ui(args: List[str]):  # type: ignore
    """Runs lints for the ui"""
    docker = DockerClient(
        compose_files=_get_compose_files(),
        compose_project_directory=get_project_root(),
    )
    docker.compose.run("gama_ui", ["yarn", "lint", *args])


@click.command(name="type-generate")
def type_generate():  # type: ignore
    """Generates typescript types for all ros messages"""
    docker = DockerClient(
        compose_files=_get_compose_files(),
        compose_project_directory=get_project_root(),
    )
    docker.compose.run("gama_vessel", ["npx", "ros-typescript-generator"])


@click.command(name="up")
@click.option(
    "--build",
    type=bool,
    default=False,
    is_flag=True,
    help="Should we rebuild the docker containers? Default: False",
)
@click.argument(
    "service",
    required=False,
    type=click.Choice(SERVICES),
)
@click.argument("args", nargs=-1)
def up(
    build: bool,
    service: str,
    args: List[str],
):
    """Starts the vessel"""
    dev_mode = os.environ["GAMA_CLI_DEV_MODE"] == "true"

    config = read_vessel_config()
    build = maybe_ignore_build(dev_mode, build)
    prod = maybe_ignore_prod(dev_mode, config.prod)

    docker = DockerClient(
        compose_files=_get_compose_files(
            gpu=config.extensions.lookout,
            network=config.network,
            variant=config.variant,
            prod=prod,
        ),
        compose_project_directory=get_project_root(),
    )

    vessel_launch_command_args = f"mode:='{config.mode.value}' rviz:='{config.extensions.rviz}'"
    if config.ubiquity_user:
        vessel_launch_command_args += f" ubiquity_user:='{config.ubiquity_user}'"
    if config.ubiquity_pass:
        vessel_launch_command_args += f" ubiquity_pass:='{config.ubiquity_pass}'"
    if config.ubiquity_ip:
        vessel_launch_command_args += f" ubiquity_ip:='{config.ubiquity_ip}'"
    if config.log_level:
        vessel_launch_command_args += f" log_level:='{config.log_level.value}'"

    # TODO - use config.__dataclass_fields__ and iterate through the Dict[str, Field]
    fields = [
        "ddsrouter_groundstation_ip",
        "ddsrouter_groundstation_port",
        "ddsrouter_vessel_ip",
        "ddsrouter_vessel_port",
    ]
    for field in fields:
        if getattr(config, field):
            vessel_launch_command_args += f" {field}:='{getattr(config, field)}'"

    os.environ["GAMA_VERSION"] = get_gama_version()
    os.environ["GAMA_VARIANT"] = config.variant.value
    os.environ["GAMA_VESSEL_COMMAND_ARGS"] = vessel_launch_command_args
    os.environ["LOOKOUT_COMMAND_ARGS"] = f"mode:='{config.mode.value}'"

    services = (
        [service]
        if service
        else [
            "gama_ui",
            "gama_chart_tiler",
            "gama_chart_api",
            "gama_vessel",
            "gama_greenstream",
            "gama_docs",
        ]
    )

    docker.compose.up(
        services,
        detach=True,
        build=build,
    )

    if config.extensions.lookout:
        docker.compose.up(
            ["lookout"],
            detach=True,
            build=build,
        )

    if config.extensions.groot:
        docker.compose.up(["groot"], detach=True, build=build)


@click.command(name="down")
@click.argument("args", nargs=-1)
def down(args: List[str]):  # type: ignore
    """Stops the vessel"""
    docker = DockerClient(
        compose_files=_get_compose_files(),
        compose_project_directory=get_project_root(),
    )
    # set timeout to 20 secs (default 10) to allow for graceful shutdown of rosbag et al
    docker.compose.down(timeout=20)


@click.command(name="install")
@click.option(
    "--variant",
    type=click.Choice(Variant),  # type: ignore
    help="Which variant of GAMA to install?",
)
def install(variant: Variant):  # type: ignore
    """Install GAMA on a vessel"""
    config = read_vessel_config()
    variant = variant or config.variant
    docker = DockerClient(
        compose_files=_get_compose_files(variant=variant),
        compose_project_directory=get_project_root(),
    )
    try:
        docker.compose.pull(
            [
                "gama_ui",
                "gama_chart_tiler",
                "gama_chart_api",
                "gama_vessel",
                "gama_greenstream",
                "gama_docs",
            ]
        )
    except Exception:
        click.echo(
            click.style(
                "Failed to pull GAMA files. Have you ran `gama_cli authenticate` ?",
                fg="yellow",
            )
        )


@click.command(name="configure")
@click.option("--default", is_flag=True, help="Use default values")
def configure(default: bool):  # type: ignore
    """Configure GAMA Vessel"""

    if default:
        config = GamaVesselConfig()
        write_vessel_config(config)
    else:
        # Check if the file exists
        if os.path.exists(get_vessel_config_path()):
            click.echo(
                click.style(
                    f"GAMA Vessel config already exists: {get_vessel_config_path()}",
                    fg="yellow",
                )
            )
            result = click.prompt(
                "Do you want to overwrite it?", default="y", type=click.Choice(["y", "n"])
            )
            if result == "n":
                return

        config = GamaVesselConfig(
            variant=click.prompt(
                "Variant",
                default=Variant.WHISKEY_BRAVO,
                type=click.Choice([item.value for item in Variant]),
            ),
            ubiquity_user=click.prompt("Ubiquity username", default=""),
            ubiquity_pass=click.prompt("Ubiquity password", default=""),
            ubiquity_ip=click.prompt("Ubiquity ip", default=""),
            mode=click.prompt(
                "Mode", default=Mode.HARDWARE, type=click.Choice([item.value for item in Mode])
            ),
            prod=click.prompt("Prod", default=True, type=bool),
            network=click.prompt(
                "Network",
                default=Network.HOST,
                type=click.Choice([item.value for item in Network]),
            ),
            log_level=click.prompt(
                "Log level",
                default=LogLevel.INFO,
                type=click.Choice([item.value for item in LogLevel]),
            ),
        )
        write_vessel_config(config)

import logging

import click

from classy_imaginary.cli.colorize import colorize_cmd
from classy_imaginary.cli.describe import describe_cmd
from classy_imaginary.cli.edit import edit_cmd
from classy_imaginary.cli.edit_demo import edit_demo_cmd
from classy_imaginary.cli.imagine import imagine_cmd
from classy_imaginary.cli.shared import ColorShell, ImagineColorsCommand
from classy_imaginary.cli.train import prep_images_cmd, prune_ckpt_cmd, train_concept_cmd
from classy_imaginary.cli.upscale import upscale_cmd

logger = logging.getLogger(__name__)


@click.command(
    prompt="🤖🧠> ",
    intro="Starting imaginAIry shell...",
    help_headers_color="yellow",
    help_options_color="green",
    context_settings={"max_content_width": 140},
    cls=ColorShell,
)
@click.pass_context
def aimg(ctx):
    """
    🤖🧠 ImaginAIry.

    Pythonic generation of images via AI
    """
    import sys

    is_shell = len(sys.argv) == 1
    if is_shell:
        print(ctx.get_help())


aimg.command_class = ImagineColorsCommand


aimg.add_command(colorize_cmd, name="colorize")
aimg.add_command(describe_cmd, name="describe")
aimg.add_command(edit_cmd, name="edit")
aimg.add_command(edit_demo_cmd, name="edit-demo")
aimg.add_command(imagine_cmd, name="imagine")
aimg.add_command(prep_images_cmd, name="prep-images")
aimg.add_command(prune_ckpt_cmd, name="prune-ckpt")
aimg.add_command(train_concept_cmd, name="train-concept")
aimg.add_command(upscale_cmd, name="upscale")


@aimg.command()
def version():
    """Print the version."""
    from classy_imaginary.version import get_version

    print(get_version())


@aimg.command("system-info")
def system_info():
    """
    Display system information. Submit this when reporting bugs.
    """
    from classy_imaginary.debug_info import get_debug_info

    for k, v in get_debug_info().items():
        k += ":"
        click.secho(f"{k: <30} {v}")


@aimg.command("model-list")
def model_list_cmd():
    """Print list of available models."""
    from classy_imaginary import config

    print(f"{'ALIAS': <10} {'NAME': <18} {'DESCRIPTION'}")
    for model_config in config.MODEL_CONFIGS:
        print(
            f"{model_config.alias: <10} {model_config.short_name: <18} {model_config.description}"
        )

    print("\nCONTROL MODES:")
    print(f"{'ALIAS': <10} {'NAME': <18} {'CONTROL TYPE'}")
    for control_mode in config.CONTROLNET_CONFIGS:
        print(
            f"{control_mode.alias: <10} {control_mode.short_name: <18} {control_mode.control_type}"
        )


if __name__ == "__main__":
    aimg()  # noqa

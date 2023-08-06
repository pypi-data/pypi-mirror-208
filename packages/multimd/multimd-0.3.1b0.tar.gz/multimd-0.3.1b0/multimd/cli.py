#!/usr/bin/env python3

###
# This module implements the [C]-ommand [L]-ine [I]-nterface of ¨multimd.
###


from typing import Tuple

import                        typer
from typing_extensions import Annotated

from .build import Builder


# --------- #
# -- CLI -- #
# --------- #

CLI = typer.Typer()

###
# prototype::
#     src_dest : a couple of paths giving the source directory with
#                the MD chunks to be merged, and the final MD file
#                to build.
#     erase    : set to ``True``, this argument allows to erase
#                an existing final file before building the new one.
#
#     :action: :see: mmdbuild.MMDBuilder
###
@CLI.command(
    context_settings = dict(
        help_option_names = ['--help', '-h']
    ),
    help = "Merging MD chunks into a single MD file."
)
def _CLI(
    src_dest: Annotated[
        Tuple[Path,Path],
        typer.Argument(
            help = "Path of the source directory with "
                   "the MD chunks to be merged, followed "
                   "by the path of the final MD file to build."
    )],
    erase: Annotated[
        bool,
        typer.Option(
            '--erase', '-e',
            help = "Erase an existing final MD file before "
                   "building the new one."
    )] = False,
) -> None:
# Relative to absolute?
    cwd = Path.cwd()

    src_dest     = list(src_dest)
    dest_message = src_dest[1]

    for i, p in enumerate(src_dest):
        if not p.is_absolute():
            src_dest[i] = cwd / p

# Let's call our worker.
    Builder(
        erase = erase,
        *src_dest
    ).build()

# Let's talk to the user.
    if Path(dest_message).is_absolute():
        message = f"""
Successfully built file.
  + Full path given:
    {dest_message}
        """

    else:
        message = f"""
Successfully built file.
  + Path given:
    {dest_message}
  + Full path used:
    {src_dest[1]}
        """

    print(message.strip())

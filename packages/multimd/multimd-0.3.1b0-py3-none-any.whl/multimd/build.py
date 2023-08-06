#!/usr/bin/env python3

###
# This module allows to make a single path::``MD`` file from several single
# ones (using or not an "automatic" merging).
###


from pathlib import Path

from .toc import *


# ------------------------------------ #
# -- SINGLE MD FROM MULTI SINGLE MD -- #
# ------------------------------------ #

###
# This class finds all the single path::``MD`` files and then builds a final
# single one with all the chunks found.
###
class Builder():

###
# prototype::
#     src   : the path of the directory containing the path::``MD`` chunks.
#     dest  : the path of the single final path::``MD`` file to build.
#     erase : set to ``True``, this argument allows to erase an existing
#             final file to build a new one.
###
    def __init__(
        self,
        src  : Path,
        dest : Path,
        erase: bool = False
    ) -> None:
        self.src   = src
        self.dest  = dest
        self.erase = erase


###
# prototype::
#     :action: this method finds the single path::``MD`` files, and then merges
#              all the ¨md codes found to build the final path::``MD`` file.
###
    def build(self) -> None:
# All the MD codes.
        mdcode = []

        for onefile in TOC(self.src).extract():
            mdcode.append(
                onefile.read_text(encoding = 'utf-8')
                       .strip()
            )

        mdcode = ('\n'*3).join(mdcode)

# Can we erase an existing final file?
        if self.dest.is_file() and not self.erase:
            raise IOError(
                f"the class {type(self).__name__} is not allowed "
                 "to erase the final file:"
                 "\n"
                f"{self.dest}"
            )

# We can build the file, so let's do it.
        self.dest.write_text(
            data     = mdcode,
            encoding = 'utf-8'
        )

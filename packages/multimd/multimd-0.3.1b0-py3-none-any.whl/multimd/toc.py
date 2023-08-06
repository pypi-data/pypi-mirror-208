#!/usr/bin/env python3

###
# This module finds paths to path::``MD'' files either by following
# the specification in a path::``about.yaml'' file, or by looking
# directly in a directory (without going further recursively).
###


from typing import List

from pathlib import Path
from yaml    import safe_load as yaml_load

from natsort import natsorted


# --------------- #
# -- CONSTANTS -- #
# --------------- #

ABOUT_FILE_NAME = "about.yaml"
TAG_TOC         = "toc"

UNIX_SEP = "/"

MD_FILE_EXT    = "md"
MD_FILE_SUFFIX = f'.{MD_FILE_EXT}'


# ------------------------ #
# -- LOOK FOR MD CHUNKS -- #
# ------------------------ #

###
# This class produces a list of file paths from a path::``maindir`` folder.
# There are two possible ways of doing this.
#
#     1) If there is a path::``about.yaml`` file in path::``maindir``,
#        the yaml::``toc`` block specifications are followed.
#
#     2) If there is no path::``about.yaml`` file, a search is made only
#        in path::``maindir``.
#
#
# warning::
#     Unlike the 1st mode, the 2nd one doesn't do searches in subfolders.
###
class TOC():

###
# prototype::
#     maindir : the path of the directory to analyze.
###
    def __init__(
        self,
        maindir: Path,
    ) -> None:
        self.maindir = maindir


###
# prototype::
#     :return: the paths of the files found inside path::``self.maindir``
#              by using or not an path::``about.yaml`` file.
#
#     :see: self._extract_recu
###
    def extract(self) -> List[Path]:
        return self._extract_recu(curdir = self.maindir)


###
# prototype::
#     curdir : the path of a directory to analyze.
#
#     :return: the list of absolute paths found inside path::``curdir``
#              by using or not an path::``about.yaml`` file.
###
    def _extract_recu(
        self,
        curdir: Path,
    ) -> List[Path]:
# There is an ``about.yaml`` file.
        if (curdir / ABOUT_FILE_NAME).is_file():
# ``strpaths == []`` can be ``True`` if no ``toc`` block has been used.
            strpaths = self.yaml2paths(curdir)

        else:
            strpaths = []

# No files found at this moment.
        if strpaths == []:
            for fileordir in curdir.iterdir():
                if not fileordir.is_file():
                    continue

                if fileordir.suffix == MD_FILE_SUFFIX:
                    strpaths.append(str(fileordir))

            strpaths = natsorted(strpaths)

# No files found.
        if strpaths == []:
            raise IOError(
                f'no file found inside ``{curdir}``.'
            )

# Let's build the ``Path`` paths.
        pathsfound = []

        for one_strpath in strpaths:
# One folder: let's do a recursive search.
            if one_strpath[-1] == UNIX_SEP:
                pathsfound +=  self._extract_recu(
                    curdir = curdir / one_strpath
                )

# Just a file.
            else:
# Complete short names.
                if not '.' in one_strpath:
                    one_strpath = f'{one_strpath}{MD_FILE_SUFFIX}'

# A new path found.
                pathsfound.append(curdir / one_strpath)

# Everything seems ok.
        return pathsfound


###
# prototype::
#     curdir : the path of the directory analyzed.
#
#     :return: the list of candidate paths found inside path::``curdir``
#              by using or not an path::``about.yaml`` file.
###
    def yaml2paths(
        self,
        curdir: Path,
    ) -> List[str]:
        try:
            with (curdir / ABOUT_FILE_NAME).open(
                encoding = 'utf-8',
                mode     = "r",
            ) as f:
                datasfound = yaml_load(f)

            if not TAG_TOC in datasfound:
                return []

            datasfound = datasfound[TAG_TOC]

            if not type(datasfound) == list:
                self._raise_this(
                    'the block `toc` must contains a list of paths.'
                )

            for d in datasfound:
                if not type(d) == str:
                    self._raise_this(
                        'the block `toc` must contains a list of paths.'
                    )

                if not d:
                    raise self._raise_this(
                        'an empty path has been found.'
                    )

            return datasfound

        except Exception as e:
            raise self._raise_this(
                 'Exception from the package ``yaml``:'
                 '\n'
                f'{e}'
            )


###
# prototype::
#     extra : an additional message to specify the error encountered.
#
#     :action: raise a ``ValueError`` to indicate a problem met with
#              the path::``about.yaml`` file.
###
    def _raise_this(
        self,
        extra: str = "",
    ) -> List[str]:
        message = (
            f'invalid ``{ABOUT_FILE_NAME}`` found in the following dir:'
             '\n'
            f'{self.maindir}'
        )

        if extra:
            message += f'\n\n{extra}'

        raise ValueError(message)

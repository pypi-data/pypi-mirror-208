# Box, file versioning.
# Copyright (C) 2023  Firlast
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from os import path as os_path, walk as os_walk


def _filter_filelist(path: str) -> str:
    if path.startswith('/'):
        path = path[1:]

    return os_path.abspath(path)


def _path_has_ignored(ignored: list, path: str) -> bool:
    for i in ignored:
        if i in os_path.abspath(path):
            return True


def _load_ignore() -> list:
    try:
        with open('.ignore', 'r') as ignore_file:
            filelist = ignore_file.readlines()
    except FileNotFoundError:
        ignored = []
    else:
        filelist = [file.replace('\n', '') for file in filelist]
        ignored = list(map(_filter_filelist, filelist))

    ignored.append('.box')
    return ignored


def get_non_ignored() -> list:
    ignored = _load_ignore()
    non_ignored = []

    for root, dirs, files in os_walk('.'):
        if not _path_has_ignored(ignored, root):
            for file in files:
                filepath = os_path.join(root, file)
                if not _path_has_ignored(ignored, filepath):
                    non_ignored.append(filepath.replace('./', ''))

    return non_ignored

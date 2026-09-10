# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

"""
Uranus Utilities
================

General-purpose utility functions and helpers used throughout
the entire Uranus codebase.
"""

from datetime import date
import os, gzip, shutil, tarfile, zipfile, bz2
import utils.shared as shr
import time


# ===========================================================
#           COMPRESSIONS AND ARCHIVES FOR BACKUPS
# ===========================================================


def add_date_suffix(filename: str):
    """add the suffixe date : eg: req.txt-2005-8-6"""
    return filename + "-" + shr.PROGRAM_NAME + str(date.today())


def make_gzip_backup(file: str) -> str:
    """Make a backup of an existing file and compress it using gzip.

    Args:
        file: Path to the original file to back up.

    Returns:
        The path of the created gzip backup file.

    Raises: FileNotFoundError, IsADirectoryError.
    """

    if not os.path.isfile(file):
        raise FileNotFoundError(f"Source file not found: {file}")

    gz_file = f"{add_date_suffix(file)}.back.gz"

    if os.path.exists(gz_file):
        if not os.path.isfile(gz_file):
            raise IsADirectoryError(
                f"Cannot overwrite directory with backup file: {gz_file}"
            )
        os.remove(gz_file)

    with open(file, "rb") as f_in, gzip.open(gz_file, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    return gz_file


def make_tarball(file: str):
    """Make a backup of an existing file or directory and compress it using tar.gz.

    Args:
        file: Path to the original file or directory to back up.

    Returns:
        The path of the created tar.gz backup file.

    Raises: FileNotFoundError, IsADirectoryError.
    """

    if not os.path.exists(file):
        raise FileNotFoundError(f"Source file or directory not found: {file}")

    tar_file = f"{add_date_suffix(file)}.back.tar.gz"

    if os.path.exists(tar_file):
        if os.path.isdir(tar_file):
            raise IsADirectoryError(
                f"Cannot overwrite directory with backup file: {tar_file}"
            )
        os.remove(tar_file)

    with tarfile.open(tar_file, "w:gz") as tar:
        tar.add(file, arcname=os.path.basename(file))

    return tar_file


def make_bzip2_backup(file: str) -> str:
    """Make a backup of an existing file and compress it using Bzip2 (.bz2).

    Args:
        file: Path to the original file to back up.

    Returns:
        The path of the created bz2 backup file.

    Raises: FileNotFoundError, IsADirectoryError.
    """

    if not os.path.isfile(file):
        raise FileNotFoundError(f"Source file not found: {file}")

    bz2_file = f"{add_date_suffix(file)}.back.bz2"

    if os.path.exists(bz2_file):
        if os.path.isdir(bz2_file):
            raise IsADirectoryError(
                f"Cannot overwrite directory with backup file: {bz2_file}"
            )
        os.remove(bz2_file)

    with open(file, "rb") as f_in, bz2.open(bz2_file, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    return bz2_file


def make_zip_backup(file: str) -> str:
    """Make a backup of an existing file or directory using ZIP (.zip).

    Args:
        file: Path to the original file or directory to back up.

    Returns:
        The path of the created ZIP backup file.

    Raises: FileNotFoundError, IsADirectoryError.
    """

    if not os.path.exists(file):
        raise FileNotFoundError(f"Source file or directory not found: {file}")

    zip_file = f"{add_date_suffix(file)}.back.zip"

    if os.path.exists(zip_file):
        if os.path.isdir(zip_file):
            raise IsADirectoryError(
                f"Cannot overwrite directory with backup file: {zip_file}"
            )
        os.remove(zip_file)

    with zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if os.path.isdir(file):
            for root, _, files in os.walk(file):
                for f in files:
                    full_path = os.path.join(root, f)
                    arcname = os.path.relpath(
                        full_path, start=os.path.dirname(file)
                    )
                    zf.write(full_path, arcname=arcname)
        else:
            zf.write(file, arcname=os.path.basename(file))

    return zip_file


"""
def exec_progression_bar():
    for i in range(21):
        bar = "█" * i + "-" * (20 - i)
        print(f"\r[{bar}] {i * 5}%", end="")
        time.sleep(0.1)
        """

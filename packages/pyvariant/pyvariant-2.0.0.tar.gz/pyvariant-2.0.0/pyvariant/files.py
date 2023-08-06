"""Collection of methods for handling files."""
import gzip
import os.path
import shutil
import sys
from ftplib import FTP
from tempfile import TemporaryDirectory
from typing import Callable, Dict, List, Set

from appdirs import user_data_dir
from Bio.bgzf import BgzfWriter, _bgzf_magic

from .constants import CACHE_DIR_ENV, CACHE_DIR_NAME


def bgzip(path: str) -> str:
    """Compress a file in BGZF format.

    Args:
        path (str): Path to file to compress

    Returns:
        str: Path to compressed file
    """
    chunk_size = 4096  # chunk size is set to balance runtime and memory usage
    openfunc: Callable
    openmode: str
    remove_original: bool

    # if the input is gzip-compressed, recompress it with bgzip using the same file name
    if path.endswith(".gz") or path.endswith(".gzip"):
        openfunc = gzip.open
        openmode = "rb"
        output = path
        remove_original = False
    # if the input is not compressed, compress it with bgzip and append ".gz" to the file name
    else:
        openfunc = open
        openmode = "r"
        output = path + ".gz"
        remove_original = True

    # compress to a temporary file first to avoid overwritting the file as it's being read
    with TemporaryDirectory() as tempdir:
        tempfile = os.path.join(tempdir, os.path.basename(output))
        print(f"Compressing {path} with bgzip (this may take some time)...", file=sys.stderr)
        print(f"Writing compressed output to temporary file '{tempfile}'", file=sys.stderr)
        with openfunc(path, openmode) as inf:
            with BgzfWriter(tempfile, compresslevel=9) as outf:
                chunk = inf.read(chunk_size)
                while chunk:
                    outf.write(chunk)
                    chunk = inf.read(chunk_size)
        # move the temporary file to the same directory as the input
        print(f"Moving compressed output to '{output}'", file=sys.stderr)
        shutil.move(tempfile, output)

    # remove the original to save space
    if remove_original:
        os.remove(path)

    return output


def ftp_download(server: str, subdir: str, remote_file: str, local_file: str):
    """Download a file from an FTP server.

    Args:
        server (str): Server URL
        subdir (str): Remote subdirectory name
        remote_file (str): Remote file name
        local_file (str): Local file name

    Raises:
        RuntimeError: Download failed
    """
    try:
        ftp = FTP(server)
        print(f"Connecting to {server}", file=sys.stderr)
        ftp.login()
        url = "ftp://" + server + "/" + subdir + "/" + remote_file
        print(f"Downloading {url} to {local_file}", file=sys.stderr)
        ftp.cwd(subdir)
        with open(local_file, "wb") as fh:
            ftp.retrbinary(f"RETR {remote_file}", fh.write)
        print("Download successful", file=sys.stderr)
        ftp.quit()
    except Exception as exc:
        raise RuntimeError(f"Download failed: {exc}")


def get_cache_dir() -> str:
    f"""Get the cache root directory. If the environmental variable '{CACHE_DIR_ENV}' is set, this
    package will use that as the directory. Otherwise, this package will use the default appdata
    dir for the user (platform dependant).

    Returns:
        str: Path to user's data directory
    """
    try:
        return os.environ[CACHE_DIR_ENV]
    except KeyError:
        return os.path.join(user_data_dir(), CACHE_DIR_NAME)


def is_bgzipped(path: str) -> bool:
    """Check if a file is compressed in BGZF format.

    Args:
        path (str): Path to the file

    Returns:
        bool: True if the file has been compressed with bgzip else False
    """
    with open(path, "rb") as f:
        file_start = f.read(len(_bgzf_magic))
        return file_start == _bgzf_magic


def tsv_to_dict(path: str) -> Dict[str, List[str]]:
    """Parse a TSV of one-to-one mappings.

    Args:
        path (str): Path to TSV file

    Returns:
        Dict[str, List[str]]: Mapping of alias to annotated name
    """
    result_: Dict[str, Set[str]] = {}

    # load data from the TSV file, keep only unique values
    with open(path, "r") as fh:
        for line in fh:
            if line:
                alias, name = line.strip().split("\t")[:2]
                result_.setdefault(alias, set())
                result_[alias].add(name)

    # convert values to sorted lists
    result = {}
    for alias in result_:
        result[alias] = sorted(result_[alias])

    return result


def txt_to_list(path: str) -> List[str]:
    """Parse a text file into a list of unique strings.

    Args:
        path (str): Path to the text file

    Returns:
        List[str]: Values from the file
    """
    result = set()

    with open(path, "r") as fh:
        for line in fh:
            if line:
                result.add(line.strip())

    return sorted(result)

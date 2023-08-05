"""Decodes PexMetadata to download S3 files locally and setup a runnable PEX environment."""
import hashlib
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional
from uuid import uuid4

from dagster import _check as check
from dagster_cloud_cli.core.workspace import PexMetadata

DEFAULT_PEX_FILES_DIR = "/tmp/pex-files"


def _download_from_s3(filename: str, local_filepath: str):
    # Lazy import boto3 to avoid a hard dependency during module load
    import boto3

    s3 = boto3.client("s3")

    # TODO: move the bucket and prefix to pex_metdata
    s3_bucket_name = os.environ["DAGSTER_CLOUD_SERVERLESS_STORAGE_S3_BUCKET"]
    # prefix is typically org-storage/{org_public_id}
    s3_prefix = os.environ["DAGSTER_CLOUD_SERVERLESS_STORAGE_S3_PREFIX"]

    s3_key = f"{s3_prefix}/pex/{filename}"
    # write to different file and rename for read safety
    local_tmp_filepath = local_filepath + "-" + str(uuid4())
    s3.download_file(
        Bucket=s3_bucket_name,
        Key=s3_key,
        Filename=local_tmp_filepath,
    )
    os.rename(local_tmp_filepath, local_filepath)


class PexExecutable(
    NamedTuple(
        "_PexExecutable",
        [
            ("source_path", str),
            ("all_paths", List[str]),
            ("environ", Dict[str, str]),
            ("working_directory", Optional[str]),
            ("venv_dirs", List[str]),
        ],
    )
):
    def __new__(
        cls,
        source_path: str,
        all_paths: List[str],
        environ: Dict[str, str],
        working_directory: Optional[str],
        venv_dirs: List[str],
    ):
        return super(PexExecutable, cls).__new__(
            cls,
            check.str_param(source_path, "source_path"),
            check.list_param(all_paths, "all_paths", str),
            check.dict_param(environ, "environ", str, str),
            check.opt_str_param(working_directory, "working_directory"),
            check.list_param(venv_dirs, "venv_dirs"),
        )


@dataclass
class PexVenv:
    path: Path
    site_packages: Path
    bin: Path
    entrypoint: Path
    pex_filename: str


class PexInstallationError(Exception):
    pass


class PexS3Registry:
    def __init__(self, local_pex_files_dir: Optional[str] = None):
        self._local_pex_files_dir = (
            local_pex_files_dir if local_pex_files_dir else DEFAULT_PEX_FILES_DIR
        )
        os.makedirs(self._local_pex_files_dir, exist_ok=True)
        self.working_dirs: Dict[
            str, str
        ] = {}  # once unpacked, working dirs dont change so we cache them

    def get_pex_executable(self, pex_metadata: PexMetadata) -> PexExecutable:
        if "=" not in pex_metadata.pex_tag:
            raise ValueError(f"Invalid pex tag, no prefix in {pex_metadata.pex_tag!r}")
        prefix, filenames = pex_metadata.pex_tag.split("=", 1)
        if prefix != "files":
            raise ValueError(
                f'Expected pex_tag prefix "files=" not found in tag {pex_metadata.pex_tag!r}'
            )

        pex_filenames = filenames.split(":")
        deps_pex_filepaths = []
        source_pex_filepath = None

        for filename in pex_filenames:
            local_filepath = os.path.join(self._local_pex_files_dir, filename)

            # no need to download if we already have this file - these
            # files have a content hash suffix so name equality implies content is same
            if not os.path.exists(local_filepath):
                if os.getenv("S3_PEX_DISABLED"):
                    raise ValueError(
                        f"File {local_filepath} not found for pex tag {pex_metadata.pex_tag},"
                        " S3_PEX_DISABLED"
                    )
                _download_from_s3(filename, local_filepath)

            if filename.startswith("source-"):
                source_pex_filepath = local_filepath
                # make it executable
                os.chmod(source_pex_filepath, 0o775)
            else:
                deps_pex_filepaths.append(local_filepath)

        if not source_pex_filepath:
            raise ValueError("Invalid pex_tag has no source pex: %r" % pex_metadata.pex_tag)

        # we unpack each pex file into its own venv
        source_venv = self.venv_for(source_pex_filepath)
        deps_venvs = []
        for deps_filepath in deps_pex_filepaths:
            deps_venvs.append(self.venv_for(deps_filepath))

        entrypoint = str(source_venv.entrypoint)
        pythonpaths = ":".join(
            [str(source_venv.site_packages)]
            + [str(deps_venv.site_packages) for deps_venv in deps_venvs]
        )
        bin_paths = ":".join(
            [str(source_venv.bin)] + [str(deps_venv.bin) for deps_venv in deps_venvs]
        )
        working_dir = self.get_working_dir_for_pex(entrypoint)
        env = {
            "PATH": bin_paths + ":" + os.environ["PATH"],
            "PYTHONPATH": pythonpaths,
        }
        return PexExecutable(
            entrypoint,
            [source_pex_filepath] + deps_pex_filepaths,
            env,
            working_dir,
            venv_dirs=[str(source_venv.path)] + [str(deps_venv.path) for deps_venv in deps_venvs],
        )

    def venv_for(self, pex_filepath) -> PexVenv:
        _, pex_filename = os.path.split(pex_filepath)
        venv_dir = self.venv_dir_for(pex_filepath)
        if os.path.exists(venv_dir):
            logging.info("Reusing existing venv %r for %r", venv_dir, pex_filepath)
        else:
            installed = self.install_venv(venv_dir, pex_filepath)
            if not installed or not os.path.exists(venv_dir):
                raise PexInstallationError("Could not install venv", pex_filepath)
        venv_path = Path(venv_dir).absolute()
        return PexVenv(
            path=venv_path,
            site_packages=self.get_site_packages_dir_for_venv(venv_path),
            bin=venv_path / "bin",
            entrypoint=venv_path / "pex",
            pex_filename=pex_filename,
        )

    def venv_dir_for(self, pex_filepath: str):
        # Use a short name for better stack traces
        short_hash = hashlib.shake_256(pex_filepath.encode("utf-8")).hexdigest(6)
        venv_root = os.getenv("VENVS_ROOT", "/venvs")
        return os.path.join(venv_root, short_hash)

    def install_venv(self, venv_dir: str, pex_filepath: str) -> bool:
        # Unpacks the pex file into a venv at venv_dir
        try:
            subprocess.check_output(
                [
                    "pex-tools",
                    pex_filepath,
                    "venv",
                    # multiple packages sometimes provide the same file, eg dbt/__init__.py is in
                    # both dbt_core and dbt_duckdb
                    "--collisions-ok",
                    # since we combine multiple venvs, we need non hermetic scripts
                    "--non-hermetic-scripts",
                    venv_dir,
                ],
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as err:
            shutil.rmtree(venv_dir, ignore_errors=True)  # don't leave invalid dir behind
            logging.exception(
                "Failure to unpack pex file %r into a venv: %r",
                pex_filepath,
                err.output,
            )
            return False
        logging.info(
            "Unpacked pex file %r into venv at %r",
            pex_filepath,
            venv_dir,
        )
        return True

    def get_site_packages_dir_for_venv(self, venv_path: Path) -> Path:
        python = venv_path / "bin" / "python3"
        proc = subprocess.run(
            [python, "-c", "import site; print(site.getsitepackages()[0])"],
            capture_output=True,
            check=False,
        )
        if not proc.returncode:
            return Path(proc.stdout.decode("utf-8").strip()).absolute()
        else:
            logging.error(
                "Cannot determine site-packages for venv at %r: %s\n%s",
                venv_path,
                proc.stdout.decode("utf-8"),
                proc.stderr.decode("utf-8"),
            )
            raise PexInstallationError("Cannot determine site-packages", venv_path, proc.stderr)

    def get_working_dir_for_pex(self, pex_path: str) -> Optional[str]:
        # A special 'working_directory' package may be included the source package.
        # If so we use site-packages/working_directory/root as the working dir.
        # This allows shipping arbitrary files to the server - also used for python_file support.
        if pex_path in self.working_dirs:
            return self.working_dirs[pex_path]
        try:
            working_dir_file = subprocess.check_output(
                [
                    pex_path,
                    "-c",
                    "import working_directory; print(working_directory.__file__);",
                ],
                encoding="utf-8",
            ).strip()
            if working_dir_file:
                package_dir, _ = working_dir_file.rsplit("/", 1)  # remove trailing __init__.py
                working_dir = os.path.join(package_dir, "root")
                self.working_dirs[pex_path] = working_dir
                return working_dir
            return None

        except subprocess.CalledProcessError:
            # working_directory package is optional, just log a message
            logging.info("Cannot import working_directory package - not setting current directory.")
            return None
        except OSError:
            # some issue with pex not being runnable, log an error but don't fail yet
            # might fail later if we try to run this again
            logging.exception(
                "Ignoring failure to run pex file to determine working_directory %r", pex_path
            )
            return None

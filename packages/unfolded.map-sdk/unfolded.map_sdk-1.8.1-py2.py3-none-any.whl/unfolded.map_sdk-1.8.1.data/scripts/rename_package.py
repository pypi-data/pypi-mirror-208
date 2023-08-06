"""rename_package

This script is designed to rename a wheel archive so that the package has a different name while the
code layout stays the same. This means that it can be installed under a different name, and pip will
show a different name, but imports remain `import unfolded.map_sdk`.

python rename_package.py --input path_to_wheel.whl --name amazon.map-sdk --output output_dir
"""
import re
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import click


def extract_wheel(origin: Path, destination: Path) -> None:
    with ZipFile(origin) as zf:
        zf.extractall(destination)


def get_dist_info_dir(path: Path) -> Path:
    dist_info_dirs = [d for d in Path(path).iterdir() if "dist-info" in d.name]
    assert len(dist_info_dirs) == 1, "Only one dist-info dir should exist"
    return dist_info_dirs[0]


def get_data_dir(path: Path) -> Path:
    data_dirs = [d for d in Path(path).iterdir() if "data" in d.name]
    assert len(data_dirs) == 1, "Only one data dir should exist"
    return data_dirs[0]


def rename_dir(dir_: Path, new_folder_name: str) -> None:
    new_dir_name = dir_.parent / dir_.name.replace("unfolded.map_sdk", new_folder_name)
    dir_.replace(new_dir_name)


def change_lines_in_record_file(record_path: Path, new_folder_name: str) -> None:
    with open(record_path) as f:
        lines = f.readlines()

    fmt = r"^unfolded.map_sdk-[\d\.]+\.(data|dist-info)/"
    lines = [
        l.replace("unfolded.map_sdk", new_folder_name) if re.match(fmt, l) else l
        for l in lines
    ]

    with open(record_path, "w") as f:
        f.write("".join(lines))


def change_name_in_metadata_file(metadata_path: Path, new_name: str) -> None:
    with open(metadata_path) as f:
        text = f.read()

    text = text.replace("Name: unfolded.map-sdk", f"Name: {new_name}")

    with open(metadata_path, "w") as f:
        f.write(text)


def create_wheel(origin: Path, destination: Path) -> Path:
    zipped_path = Path(shutil.make_archive(str(destination), "zip", origin))
    # Need to rename since shutil.make_archive appends .zip
    return zipped_path.rename(zipped_path.parent / zipped_path.name.rstrip(".zip"))


def rename_package(path: Path, new_name: str, output_dir: Path) -> None:
    new_folder_name = new_name.replace("-", "_")
    output_dir.mkdir(parents=True, exist_ok=True)
    new_wheel_path = output_dir / path.name.replace("unfolded.map_sdk", new_folder_name)

    with TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        extract_wheel(path, tmp_dir)

        dist_info_dir = get_dist_info_dir(tmp_dir)
        data_dir = get_data_dir(tmp_dir)

        change_name_in_metadata_file(dist_info_dir / "METADATA", new_name)
        change_lines_in_record_file(dist_info_dir / "RECORD", new_folder_name)
        rename_dir(dist_info_dir, new_folder_name)
        rename_dir(data_dir, new_folder_name)

        create_wheel(tmp_dir, new_wheel_path)


@click.command()
@click.option(
    "-i",
    "--input",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Path to input wheel.",
    required=True,
)
@click.option(
    "-n",
    "--name",
    type=str,
    help="New package name.",
    default="amzn.map-sdk",
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=True, file_okay=False, writable=True),
    required=True,
    help="Path to output directory.",
)
def main(input: str, name: str, output: str):  # pylint:disable=redefined-builtin
    rename_package(Path(input), name, Path(output))


if __name__ == "__main__":
    main()

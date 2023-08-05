import argparse
import hashlib
import logging
import os
import pathlib
import sys
from typing import List

import requests
import tqdm

logging.basicConfig(level=logging.INFO)
logging.root.name = "wfetch"


def die(msg: str):
    logging.critical(msg)
    sys.exit(1)


def file_sha256(file: pathlib.Path) -> str:
    assert file.exists(), file
    h = hashlib.sha256()
    with open(file, "rb") as r:
        while True:
            data = r.read(4096)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def run(_args: List[str]):
    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str, help="Target file URL")
    parser.add_argument(
        "-q",
        "--quiet",
        dest="quiet",
        action="store_true",
        default=False,
        help="If true, the tool will not output anything",
    )
    parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        default=False,
        help="If true, and output file/folder exists, it will be overwritten",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        required=False,
        default=pathlib.Path.cwd(),
        help="Output path",
    )
    parser.add_argument(
        "--sha256",
        type=str,
        required=False,
        default=None,
        help="Expected sha256 of a file",
    )

    args: argparse.Namespace = parser.parse_args(_args)
    assert isinstance(args.output, pathlib.Path)

    if args.quiet:
        logging.root.level = logging.ERROR

    name = os.path.basename(args.url)
    target = pathlib.Path(name)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        target = args.output

    if target.exists():
        if target.is_dir():
            target = target.joinpath(name)

        if target.is_file():
            got = file_sha256(target)
            if args.sha256 and got == args.sha256:
                logging.info(
                    f"""\
Not downloading file {target}, because it exists and
has expected hash sha256={got}"""
                )
                return

            if not args.force:
                die(f"File {target} exists. Pass -f to overwrite it.")

    response = requests.get(args.url, stream=True, allow_redirects=True)
    total_size_in_bytes = int(response.headers.get("content-length", 0))

    BLOCK_SIZE = 2**16
    sha256 = hashlib.sha256()
    with tqdm.tqdm(
        desc=name,
        disable=args.quiet,
        total=total_size_in_bytes,
        unit="B",
        unit_scale=True,
        ascii=True,
    ) as progress_bar:
        assert (
            target.exists() and target.is_file() and args.force
        ) or not target.exists()
        with open(target, "wb") as file:
            for data in response.iter_content(BLOCK_SIZE):
                progress_bar.update(len(data))
                sha256.update(data)
                file.write(data)

    got = sha256.hexdigest()
    logging.info(f"Fetched {target} with sha256={got}")

    if args.sha256 and got != args.sha256:
        die(
            f"""\
BAD CHECKSUM:
Expected sha256 : {args.sha256}
Actual   sha256 : {got}
"""
        )

        logging.info("sha256 checksum matched")


def main(args=sys.argv[1:]):
    try:
        run(args)
    except KeyboardInterrupt:
        die("[CTRL+C] Interrupted...")


if __name__ == "__main__":
    main()

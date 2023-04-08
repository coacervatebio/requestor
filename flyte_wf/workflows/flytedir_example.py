import csv
import os
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import List

import flytekit
from flytekit import task, workflow
from flytekit.types.directory import FlyteDirectory

@task
def download_files(csv_urls: List[str]) -> FlyteDirectory:
    working_dir = flytekit.current_context().working_directory
    local_dir = Path(os.path.join(working_dir, "csv_files"))
    local_dir.mkdir(exist_ok=True)

    # get the number of digits needed to preserve the order of files in the local directory
    zfill_len = len(str(len(csv_urls)))
    for idx, remote_location in enumerate(csv_urls):
        local_image = os.path.join(
            # prefix the file name with the index location of the file in the original csv_urls list
            local_dir,
            f"{str(idx).zfill(zfill_len)}_{os.path.basename(remote_location)}",
        )
        urllib.request.urlretrieve(remote_location, local_image)
    return FlyteDirectory(path=str(local_dir))


@task
def normalize_all_files(
    csv_files_dir: FlyteDirectory,
) -> FlyteDirectory:
    for local_csv_file, column_names, columns_to_normalize in zip(
        # make sure we sort the files in the directory to preserve the original order of the csv urls
        [os.path.join(csv_files_dir, x) for x in sorted(os.listdir(csv_files_dir))],
        columns_metadata,
        columns_to_normalize_metadata,
    ):
        print("hello")
    return FlyteDirectory(path=csv_files_dir.path)

@workflow
def download_and_normalize_csv_files(
    csv_urls: List[str],
    columns_metadata: List[List[str]],
    columns_to_normalize_metadata: List[List[str]],
) -> FlyteDirectory:
    directory = download_files(csv_urls=csv_urls)
    return normalize_all_files(
        csv_files_dir=directory,
        columns_metadata=columns_metadata,
        columns_to_normalize_metadata=columns_to_normalize_metadata,
    )

if __name__ == "__main__":
    csv_urls = [
        "https://people.sc.fsu.edu/~jburkardt/data/csv/biostats.csv",
        "https://people.sc.fsu.edu/~jburkardt/data/csv/faithful.csv",
    ]
    columns_metadata = [
        ["Name", "Sex", "Age", "Heights (in)", "Weight (lbs)"],
        ["Index", "Eruption length (mins)", "Eruption wait (mins)"],
    ]
    columns_to_normalize_metadata = [
        ["Age"],
        ["Eruption length (mins)"],
    ]

    print(f"Running {__file__} main...")
    directory = download_and_normalize_csv_files(
        csv_urls=csv_urls,
        columns_metadata=columns_metadata,
        columns_to_normalize_metadata=columns_to_normalize_metadata,
    )
    print(f"Running download_and_normalize_csv_files on {csv_urls}: " f"{directory}")
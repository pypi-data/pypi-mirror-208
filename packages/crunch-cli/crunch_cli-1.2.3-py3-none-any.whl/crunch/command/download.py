import os
import typing
import datetime

import click
import requests
import tqdm

from .. import constants, utils


def cut_url(url: str):
    try:
        return url[:url.index("?")]
    except ValueError:
        return url


def get_extension(url: str):
    url = cut_url(url)

    if url.endswith(".parquet"):
        return "parquet"

    if url.endswith(".csv"):
        return "csv"

    print(f"unknown file extension: {url}")
    raise click.Abort()


def get_data_urls(
    session: utils.CustomSession,
    data_directory: str,
    push_token: str,
) -> typing.Tuple[typing.Dict[str, str], str, str, str]:
    current_crunch = session.get("/v1/crunches/@current").json()
    data_release = session.get(f"/v1/crunches/{current_crunch['number']}/data-release", params={
        "pushToken": push_token
    }).json()

    embargo = data_release["embargo"]
    moon_column_name = data_release["moonColumnName"]
    urls = data_release["dataUrls"]

    x_train_url = urls["xTrain"]
    x_train_path = os.path.join(
        data_directory,
        f"X_train.{get_extension(x_train_url)}"
    )

    y_train_url = urls["yTrain"]
    y_train_path = os.path.join(
        data_directory,
        f"y_train.{get_extension(y_train_url)}"
    )

    x_test_url = urls["xTest"]
    x_test_path = os.path.join(
        data_directory,
        f"X_test.{get_extension(x_test_url)}"
    )

    data_urls = {
        x_train_path: x_train_url,
        y_train_path: y_train_url,
        x_test_path: x_test_url,
    }

    return (
        embargo,
        moon_column_name,
        data_urls,
        x_train_path,
        y_train_path,
        x_test_path
    )


def _download(url: str, path: str, force: bool):
    print(f"download {path} from {cut_url(url)}")

    with requests.get(url, stream=True) as response:
        response.raise_for_status()

        file_length = response.headers.get("Content-Length", None)
        file_length = int(file_length) if not None else None

        exists = os.path.exists(path)
        if not force and exists:
            if file_length is None:
                print(f"already exists: skip since unknown size")
                return

            stat = os.stat(path)
            if stat.st_size == file_length:
                print(f"already exists: file length match")
                return

        with open(path, 'wb') as fd, tqdm.tqdm(total=file_length, unit='iB', unit_scale=True, leave=False) as progress:
            for chunk in response.iter_content(chunk_size=8192):
                progress.update(len(chunk))
                fd.write(chunk)


def download(
    session: utils.CustomSession,
    force=False,
):
    push_token = utils.read_token()

    os.makedirs(constants.DOT_DATA_DIRECTORY, exist_ok=True)

    (
        embargo,
        moon_column_name,
        data_urls,
        x_train_path,
        y_train_path,
        x_test_path
    ) = get_data_urls(session, constants.DOT_DATA_DIRECTORY, push_token)

    for path, url in data_urls.items():
        _download(url, path, force)

    return (
        embargo,
        moon_column_name,
        x_train_path,
        y_train_path,
        x_test_path
    )

def download_no_data_available():
    today = datetime.date.today()
    
    print("\n---")

    # competition lunch
    if today <= datetime.date(2023, 5, 16):
        print("The data will be released on May 16th, 2023, 05.00 PM CET")
    else:
        print("No data is available yet")

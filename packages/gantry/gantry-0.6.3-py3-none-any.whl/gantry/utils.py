import base64
import collections
import collections.abc
import datetime
import hashlib
import json
import logging
import os
import pprint
import re
import sys
from pathlib import Path
from typing import IO, Any, Dict, List, Optional, Set, Tuple

import click
import requests
from dateutil import parser

from gantry.serializers import EventEncoder

logger = logging.getLogger(__name__)


def to_datetime(s: str) -> datetime.datetime:
    """
    Converts a string to a naive UTC datetime object
    """
    try:
        # fromisoformat is present starting in python3.7
        if s.endswith("Z"):
            dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        else:
            dt = datetime.datetime.fromisoformat(s)
    except (AttributeError, ValueError, TypeError):
        try:
            dt = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")
        except Exception:
            dt = parser.parse(s)
    if _is_offset_naive(dt):
        return dt

    naive_dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    return naive_dt


def to_isoformat_duration(relative_interval: datetime.timedelta) -> str:
    days = relative_interval.days
    seconds = relative_interval.seconds

    minutes, seconds = seconds // 60, seconds % 60
    hours, minutes = minutes // 60, minutes % 60
    weeks, days = days // 7, days % 7

    timedelta_str = "P"
    if weeks > 0:
        timedelta_str += str(weeks) + "W"
    if days > 0:
        timedelta_str += str(days) + "D"
    timedelta_str += "T"
    if hours > 0:
        timedelta_str += str(hours) + "H"
    if minutes > 0:
        timedelta_str += str(minutes) + "M"
    if seconds > 0:
        timedelta_str += str(seconds) + "S"

    if timedelta_str[-1] == "T":
        timedelta_str = timedelta_str[:-1]

    if len(timedelta_str) == 1:
        return "P0D"

    return timedelta_str


def _is_offset_naive(d: datetime.datetime) -> bool:
    # https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive
    aware = d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None
    return not aware


def check_event_time_in_future(event_timestamp: datetime.datetime) -> bool:
    """
    Raises an error if the event timestamp is in the future.
    Note, `event_timestamp` is assumed to be in UTC. This
    method will handle both offset-naive and offset-aware event_timestamp
    """
    current_time = (
        datetime.datetime.utcnow()
        if _is_offset_naive(event_timestamp)
        else datetime.datetime.now(datetime.timezone.utc)
    )
    return event_timestamp > current_time


def compute_feedback_id(inputs: Dict[str, Any], feedback_keys: Optional[List[str]] = None) -> str:
    assert isinstance(inputs, collections.abc.Mapping)
    if not feedback_keys:
        # When not specified, default to feedback_keys are all the
        # fields of inputs
        feedback_keys = list(inputs.keys())

    values = []
    for key in sorted(feedback_keys):
        input_value = inputs[key]
        # TODO change to hashable type if input_value isn't
        # hashable
        values.append(input_value)

    return hashlib.md5(
        json.dumps(values, sort_keys=True, cls=EventEncoder).encode("utf-8")
    ).hexdigest()


def clean_name(name: str) -> str:
    """Replace any non-alphanumeric characters, except '-' and '.', with '-'"""
    return re.sub(r"[^a-zA-Z0-9\-.]+", "-", name)


def generate_gantry_name(name: str, max_len: int = 64) -> str:
    prefix = "gantry-"
    suffix = "-" + hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]

    remaining_len = max_len - len(prefix) - len(suffix)
    trunc_name = clean_name(name)[:remaining_len].lower().strip("-")

    return prefix + trunc_name + suffix


def parse_s3_path(path: str) -> Tuple[str, str]:
    """Parses an S3 path of the form s3://bucket/path/to/obj and returns (key, path/to/obj)"""
    prefix_len = len("s3://")
    s3_path = path[prefix_len:]
    bucket, _, key = s3_path.partition("/")

    return (bucket, key)


def format_msg_with_color(msg: str, color: str, logger: logging.Logger) -> str:
    """Given a message and a colorama color, conditionally returns a formatted message if the only
    handlers of the gantry package logger are NullHandlers or StreamHandlers with sys.stderr
    or sys.stdout
    """
    # loop to short-circuit and return original message if a potential file handler is found
    for handler in logging.getLogger("gantry").handlers:
        if isinstance(handler, logging.NullHandler):
            # It is okay if handler is NullHandler
            continue
        elif isinstance(handler, logging.StreamHandler):
            # If handler is a StreamHandler make sure stream is sys.stderr or sys.stdout
            if handler.stream in (
                sys.stderr,
                sys.stdout,
            ):
                continue
        else:
            # In all other cases, we might be logging to a file so just return the original msg
            return msg
    # If we haven't short-circuited and returned original message, return the colored message
    return color + msg


def obj_by_id(els):
    obj = {}
    for el in els:
        obj[el.id] = el

    return obj


def download_file_from_url(presigned_url: str, local_path: Path):
    """
    Args:
        presigned_url (str): presigned url
        local_path (Path): local file path
    """
    os.makedirs(local_path.parent, exist_ok=True)
    with local_path.open("wb") as f:
        _download_file_to_IO(presigned_url, f)
    return local_path


def _download_file_to_IO(presigned_url: str, file: IO):
    """
    Args:
        presigned_url (str): presigned url
        file (IO): file object
    """
    with requests.get(presigned_url, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=8192):
            file.write(chunk)


def upload_file_to_url(presigned_url: str, local_path: Path):
    """
    Args:
        presigned_url (str): presigned url
        local_path (Path): local file path

    Returns:
        s3 object version id
    """
    with local_path.open("rb") as f:
        return _upload_file_from_IO(presigned_url, f)


def _upload_file_from_IO(presigned_url: str, file: IO):
    """
    Args:
        presigned_url (str): presigned url
        file (IO): file object

    Returns:
        s3 object version id
    """
    res = requests.put(presigned_url, data=file.read())
    res.raise_for_status()
    return res.headers["x-amz-version-id"]


def is_hidden(path):
    return str(path.name).startswith(".")


def list_all_files(dirpath, include_hidden_file=False):
    """
    List all files in a folder

    Args:
        dirpath (Path): target directory
        include_hidden_file (bool): whether include hidden file or not
    Returns:
        List[Path]
    """
    assert dirpath.is_dir()
    file_list = []

    if not include_hidden_file and is_hidden(dirpath):
        return file_list

    for x in dirpath.iterdir():
        if x.is_file():
            if include_hidden_file or not is_hidden(x):
                file_list.append(x)
        elif x.is_dir():
            file_list.extend(list_all_files(x, include_hidden_file))

    return file_list


def get_s3_sha256_checksum(data_bytes):
    """
    Generate local file base64 encoded sha256 checksum

    Args:
        data_bytes : byte data which need to be hashed

    Returns:
        sha256: base64 encoded sha256 value
    """
    return base64.b64encode(hashlib.sha256(data_bytes).digest()).decode("utf-8")


def get_files_checksum(path):
    """_summary_

    Args:
        path (_type_): directory path

    Returns:
        {file name: sha256 checksum}
    """
    # Do not include hidden files to avoid adding .DS_Store or other system files by accident
    file_list = list_all_files(path)
    return dict(
        [(str(f.relative_to(path)), get_s3_sha256_checksum(f.read_bytes())) for f in file_list]
    )


def pprint_records(records: List[Dict[str, str]], include_keys: Optional[Set[str]] = None):
    """
    Args:
        records (List[Dict[str, str]]): _description_
        include_keys (Optional[Set[str]], optional): _description_. Defaults to None.
    """
    pp = pprint.PrettyPrinter(depth=4)
    if not include_keys:
        pp.pprint(records)
    else:
        pp.pprint(
            [dict([(k, v) for k, v in record.items() if k in include_keys]) for record in records]
        )


def check_response_status(resp, error_prefix: str):
    if resp.get("response") != "ok":
        click.secho("FAILED.", fg="red")
        err_msg = resp.get("error", "unknown error")
        raise click.ClickException(f"{error_prefix}: {err_msg}.")
    click.secho("SUCCESS", fg="cyan")


def read_lines_from_url(url):
    response = requests.get(url, stream=True)
    for line in response.iter_lines():
        yield line.decode("utf-8")


def from_isoformat_duration(duration_string: str) -> datetime.timedelta:
    # Parse the duration string using regular expressions
    match = re.match(r"^P((\d+)W)?((\d+)D)?T?((\d+)H)?((\d+)M)?((\d+)S)?$", duration_string)
    if not match:
        raise ValueError(f"Invalid duration string: {duration_string}")

    # Extract the component values from the match object
    weeks = int(match.group(2) or 0)
    days = int(match.group(4) or 0)
    hours = int(match.group(6) or 0)
    minutes = int(match.group(8) or 0)
    seconds = int(match.group(10) or 0)

    # Calculate the total duration in seconds
    total_seconds = (weeks * 7 + days) * 86400 + hours * 3600 + minutes * 60 + seconds

    # Return a timedelta object representing the duration
    return datetime.timedelta(seconds=total_seconds)

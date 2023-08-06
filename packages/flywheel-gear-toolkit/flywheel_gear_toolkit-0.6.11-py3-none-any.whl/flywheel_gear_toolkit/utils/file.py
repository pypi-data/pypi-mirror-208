"""Checks if files do/don't exist, and handles exceptions.

This module is to remove the redundant "if os.path.exists...else" statements for
checking file existence. It allows you to check for a file, specify if it should or
should not exist, provide a desired extension, and determine if this file should result
in a code-stopping exception if it's not in the expected state.

Examples:
    >>> # Check to see if a file exists and has the extension '.mat'.  If it doesn't
    >>> # exist, do not raise an exception, as it's not critical to the code.
    >>> output_files = []
    >>> file_name = '/home/user/myFile.mat'
    >>> if file_state(file=file_name, ext='.mat', is_expected=True, exception_on_error=False):
    ...    output_files.append(file_name)

    >>> # Ensure that a file does not exist.  If it does, raise an exception. which will
    >>> # stop execution of the script
    >>> file_name = '/home/user/FinalOutput.csv'
    >>> file_state(file=file_name, is_expected=False, exception_on_error=True)

"""

import logging
import pathlib
import re
import typing as t
from dataclasses import dataclass, field
from pathlib import Path

from fw_meta.imports import load_file_name

log = logging.getLogger(__name__)


@dataclass
class File:
    """Class representing metadata of a Flywheel file.

    The SDK and config.json represent files differently. This object
    holds all the metadata associated with a file in a predictable manner
    and allows for converting from SDK or config.json file representations.

    Attributes:
        name (str): File name.
        parent_type (str): Container type of file's parent.
        modality (str): File modality.
        fw_type (str): Flywheel file type.
        mimetype (str): File mimetype.
        classification (Dict[str, List[str]]): Classification dictionary.
        tags (List[str]): List of tags.
        info (dict): Custom information dict.
        local_path (Optional[Path]): Local path to file
        parents (Dict[str, str]): File parents.
        zip_member_count (Optional[int]): File zip member count.
        version (Optional[int]): File version.
        file_id (Optional[str]): File id.
        size (Optional[int]): File size in bytes.
    """

    name: str
    parent_type: str
    modality: str = ""
    fw_type: str = ""
    mimetype: str = ""
    classification: t.Dict[str, t.List[str]] = field(default_factory=dict)
    tags: t.List[str] = field(default_factory=list)
    info: dict = field(default_factory=dict)
    local_path: t.Optional[Path] = None
    parents: t.Dict[str, str] = field(default_factory=dict)
    zip_member_count: t.Optional[int] = None
    version: t.Optional[int] = None
    file_id: t.Optional[str] = None
    size: t.Optional[int] = None

    @classmethod
    def from_config(cls, file_: dict) -> "File":
        """Create a File object from a config.json input dictionary.

        Args:
            file_ (dict): Config.json dictionary representing the file.
        """
        # file_ passed in from config.json
        obj = file_.get("object", {})
        return cls(
            file_.get("location", {}).get("name", ""),
            file_.get("hierarchy", {}).get("type", ""),
            modality=obj.get("modality", ""),
            fw_type=obj.get("type", ""),
            mimetype=obj.get("mimetype", ""),
            classification=obj.get("classification", {}),
            tags=obj.get("tags", []),
            info=obj.get("info", {}),
            local_path=file_.get("location", {}).get("path", None),
            zip_member_count=obj.get("zip_member_count", None),
            version=obj.get("version", None),
            file_id=obj.get("file_id", None),
            size=obj.get("size", None),
        )

    @classmethod
    def from_sdk(cls, file_: dict) -> "File":
        """Create a File from an SDK "file".

        Args:
            file_ (dict): SDK "file" object
        """
        return cls(
            file_.get("name", ""),
            file_.get("parent_ref", {}).get("type", ""),
            modality=file_.get("modality", ""),
            fw_type=file_.get("type", ""),
            mimetype=file_.get("mimetype", ""),
            classification=file_.get("classification", {}),
            tags=file_.get("tags", []),
            info=file_.get("info", {}),
            parents=file_.get("parents", {}),
            zip_member_count=file_.get("zip_member_count", None),
            version=file_.get("version", None),
            file_id=file_.get("file_id", None),
            size=file_.get("size", None),
        )


def is_valid(file_path, ext=None, is_expected=True, exception_on_error=True):
    """
    Checks if a file exists as expected

    Slightly more functional 'if exists' algorithm that checks for files and takes care
    of logging.  The input options specify if the file is expected to exist or not, and
    whether an exception should be thrown if it does not match the expectation.
    Input is often from a glob or pattern match, where the extension may vary or is
    unknown, so extension matching is optional.

    Args:
        file (str, pathlib.PosixPath): The file to look for.
        ext (str): An extension that "file" must match.
        is_expected (bool): Indicate if the file should exist (True) or should not exist
            (False).
        exception_on_error (bool): Raise an exception if the file does not match the
            expectations indicated by the other input arguments.

    Returns:
        bool: Indicator of whether the file exists in the specified state
            (does or does not exist, with the specified extension).  I.E, if "file.txt"
            does not exist, and is not expected to exist, file_state returns "True".
    """

    file_path = pathlib.Path(file_path)
    path_exists_as_intended = file_path.exists()

    # If the file exists and it is expected to exist
    if path_exists_as_intended and is_expected:
        log.info("located %s", file_path)

    # If the file doesn't exist and it is expected to exist
    elif not path_exists_as_intended and is_expected:
        # If the file doesn't exist but it is expected to exist and if it is critical
        # for the file to exist
        if exception_on_error:
            # throw an exception
            log.warning("Unable to locate %s", file_path)
            raise FileNotFoundError("Unable to locate %s" % file_path)

        # If the file doesn't exist but it is expected to exist and it is not critical
        # for the file to exist, keep going
        log.warning("Unable to locate %s", file_path)

    # If the file does not exist and is expected to not exist
    elif not path_exists_as_intended and not is_expected:
        # Then that's good
        log.info("%s is not present (in a good way) ", file_path)
        path_exists_as_intended = True

    # If the file does exist but is expected to not exist
    elif path_exists_as_intended and not is_expected:
        # If the file does exist but is expected to not exist and it is critical for the
        # file to not exist
        if exception_on_error:
            # Throw an exception.
            log.warning("%s is present, but should not be", file_path)
            raise FileExistsError("%s is present, but should not be" % file_path)

        # If the file does exist but is expected to not exist and it is not critical for
        # the file to not exist
        log.warning("%s is present, but unexpected", file_path)
        path_exists_as_intended = False

    # Now we'll check the file extension (if desired)
    if isinstance(ext, str):
        ext_period = ext.count(".")
        file_name = file_path.name
        extensions = file_path.suffixes

        if len(extensions) < ext_period:
            log.error("Extension %s too long for file %s", ext, file_name)
            raise TypeError("Extension %s too long for file %s" % (ext, file_name))

        file_ext = extensions[-ext_period:]
        file_ext = "".join(file_ext)

        if file_ext != ext:
            if exception_on_error:
                log.warning(
                    "Incorrect file type for input %s, expected %s, got %s",
                    file_path,
                    ext,
                    file_ext,
                )

                raise TypeError(
                    "Incorrect file type for input %s, expected %s, got %s"
                    % (file_path, ext, file_ext)
                )

            log.warning(
                "Incorrect file type for input %s, expected %s, got %s",
                file_path,
                ext,
                file_ext,
            )
        else:
            log.info("file %s has expected extension %s", file_path, ext)

    return path_exists_as_intended


def sanitize_filename(filename: str) -> t.Union[None, str]:
    """Sanitize filename to be valid on all platforms (Linux/Windows/macOS/Posix)
    Replace special characters with `_`. "*" character replaced with "star".
    """

    return load_file_name(filename)


def sanitize_name_general(
    input_basename: str, replace_str: str = "", keep_whitespace: bool = False
) -> t.Union[None, str]:
    """Remove non-safe characters from any label or name and return a name without
        special characters.

    Args:
        input_basename(str): the input basename to be checked and replaced
        replace_str(str): the string with which to replace the unsafe characters
        keep_whitespace(boolean): whether to retain spaces

    Returns:
        output_basename(str): a safe label
    """
    # Keep standard, expected behavior like sanitize_filename
    input_basename = load_file_name(input_basename)
    # Add the extra refinement of output
    if keep_whitespace:
        safe_patt = re.compile(r"[^A-Za-z0-9_\-.\s\s+]+")
    else:
        safe_patt = re.compile(r"[^A-Za-z0-9_\-.]+")
    # if the replacement is not a string or not safe, set replace_str to x
    forbidden_rplcmnt = safe_patt.match(replace_str)
    if not isinstance(replace_str, str) or forbidden_rplcmnt:
        log.warning(
            "{} is not a safe replacement string, removing instead".format(replace_str)
        )
        replace_str = ""

    # Replace non-alphanumeric (or underscore) characters with replace_str
    safe_output_basename = re.sub(safe_patt, replace_str, input_basename)

    if safe_output_basename.startswith("."):
        safe_output_basename = safe_output_basename[1:]

    log.debug('"' + input_basename + '" -> "' + safe_output_basename + '"')

    return safe_output_basename

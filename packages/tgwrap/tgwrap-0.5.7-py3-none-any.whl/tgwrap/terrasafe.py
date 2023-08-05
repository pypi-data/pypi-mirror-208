"""
This is a slightly modified copy of [terrasafe](https://github.com/PrismeaOpsTeam/Terrasafe)
and the only reason to copy it is that we wanted more control and invoke it programmatically
rather than via the command line.
"""

import os
import fnmatch
import re
from argparse import ArgumentParser
import json
import sys

from .printer import Printer

def run_terrasafe(config, data, verbose=False):
    """ Run the terrasafe validation and return the unauthorized deletions """

    printer = Printer(verbose)

    ignored_from_env_var = parse_ignored_from_env_var()

    all_deletion = get_resource_deletion(data)

    # List of all deletion which is not whitelisted or commented. Fail if not empty
    unauthorized_deletion = []

    for resource in all_deletion:
        resource_address = resource["address"]
        if is_resource_match_any(resource_address, config["unauthorized_deletion"]):
            printer.verbose(f'Resource {resource_address} can not be destroyed for any reason')
            # exit(1)
        if is_resource_match_any(resource_address, config["ignore_deletion"]):
            continue
        if is_resource_recreate(resource) and is_resource_match_any(
            resource_address,
            config["ignore_deletion_if_recreation"]
            ):
            continue
        if is_resource_match_any(resource_address, ignored_from_env_var):
            printer.verbose(f"deletion of {resource_address} authorized by env var.")
            continue
        if is_deletion_commented(resource["type"], resource["name"]):
            printer.verbose(f"deletion of {resource_address} authorized by comment")
            continue
        if is_deletion_in_disabled_file(resource["type"], resource["name"]):
            printer.verbose(f"deletion of {resource_address} authorized by disabled file feature")
            continue
        unauthorized_deletion.append(resource_address)

    if unauthorized_deletion:
        printer.verbose("Unauthorized deletion detected for those resources:")
        for deletion in unauthorized_deletion:
            printer.verbose(f" - {deletion}")
        printer.verbose("If you really want to delete those resources: comment it or export this environment variable:")
        printer.verbose(f"export TERRASAFE_ALLOW_DELETION=\"{';'.join(unauthorized_deletion)}\"")

    return unauthorized_deletion


def parse_ignored_from_env_var():
    ignored = os.environ.get("TERRASAFE_ALLOW_DELETION")
    if ignored:
        return ignored.split(";")
    return []


def get_resource_deletion(data):
    # check format version
    if data["format_version"].split(".")[0] != "0" and data["format_version"].split(".")[0] != "1":
        raise Exception("Only format major version 0 or 1 is supported")

    if "resource_changes" in data:
        resource_changes = data["resource_changes"]
    else:
        resource_changes = []

    return list(filter(has_delete_action, resource_changes))


def has_delete_action(resource):
    return "delete" in resource["change"]["actions"]


def is_resource_match_any(resource_address, pattern_list):
    for pattern in pattern_list:
        pattern = re.sub(r"\[(.+?)\]", "[[]\g<1>[]]", pattern)
        if fnmatch.fnmatch(resource_address, pattern):
            return True
    return False


def is_resource_recreate(resource):
    actions = resource["change"]["actions"]
    return "create" in actions and "delete" in actions


def is_deletion_commented(resource_type, resource_name):
    regex = re.compile(rf'(#|//)\s*resource\s*\"{resource_type}\"\s*\"{resource_name}\"')
    tf_files = get_all_files(".tf")
    for filepath in tf_files:
        with open(filepath, 'r') as file:
            for line in file:
                if regex.match(line):
                    return True
    return False


def is_deletion_in_disabled_file(resource_type, resource_name):
    regex = re.compile(rf'\s*resource\s*\"{resource_type}\"\s*\"{resource_name}\"')
    tf_files = get_all_files(".tf.disabled")
    for filepath in tf_files:
        with open(filepath, 'r') as file:
            for line in file:
                if regex.match(line):
                    return True


def get_all_files(extension):
    res = []
    for root, dirs, file_names in os.walk("."):
        for file_name in file_names:
            if fnmatch.fnmatch(file_name, "*" + extension):
                res.append(os.path.join(root, file_name))
    return res

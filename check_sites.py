# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import difflib
import getopt
import json
import os
import pathlib
import sys

from publicsuffixlist import PublicSuffixList
from RwsCheck import RwsCheck


def find_format_diff(rws_json_string, rws_sites):
    """Returns the diff of the rws_json_string and the formatted string
    generated from rws_sites.

    Args:
        rws_json_string: string
        rws_sites: JSON Object
    Returns:
        String
    """
    # Add final newline by convention
    formatted_file = json.dumps(rws_sites, indent=2, ensure_ascii=False) + "\n"
    if rws_json_string == formatted_file:
        return ""
    diff = difflib.unified_diff(
        rws_json_string.splitlines(keepends=True),
        formatted_file.splitlines(keepends=True),
        fromfile="PR file",
        tofile="expected",
    )
    joined_diff = "".join(diff)
    return f"Formatting for JSON is incorrect;\nerror was:\n```diff\n{joined_diff}\n```"


def find_diff_sets(old_sets, new_sets):
    """Finds changes made between two dictionaries of Related Website Sets

    Finds Related Website Sets that have been added or modified in old_sets
    to create new_sets and returns them as the dictionary diff_sets.
    Additionally, finds Related Website Sets that have been removed from
    old_sets to create new_sets and returns them as subtracted_sets.

    Args:
        old_sets: Dict[string, RwsSet]
        new_sets: Dict[string, RwsSet]
    Returns:
        Tuple[Dict[string, RwsSet], Dict[string, RwsSet]]
    """
    diff_sets = {
        primary: rws
        for primary, rws in new_sets.items()
        if rws != old_sets.get(primary)
    }
    subtracted_sets = {
        primary: old_sets[primary]
        for primary in set(old_sets) - set(new_sets)
        if not any(rws.includes(primary) for rws in new_sets.values())
    }
    return diff_sets, subtracted_sets


def run_nonbreaking_checks(rws_checker, rws_json_string, strict_formatting, check_sets):
    """Runs all checks from check_sites and RWSCheck whose exceptions should
    not cause the program to immediately exit.

    Returns a list of `error_texts` that result from running `find_format_diff`
    as well as a number of RWSCheck functions. The RWSCheck function calls may
    also result in changes to `rws_checker.error_list`.

    Args:
        rws_checker: RWSCheck object
        rws_json_string: string
        strict_formatting: boolean
        check_sets: Dict[string, RwsSet]
    Returns:
        [String]
    """
    error_texts = []
    if strict_formatting and (
        format_diff := find_format_diff(rws_json_string, rws_checker.rws_sites)
    ):
        error_texts.append(format_diff)

    try:
        rws_checker.check_exclusivity(rws_checker.load_sets())
    except Exception as inst:
        error_texts.append(inst)

    # These are RWSCheck functions that may append to the
    # rws_checker's error_list.
    check_list = [
        rws_checker.has_all_rationales,
        rws_checker.find_non_https_urls,
        rws_checker.find_invalid_eTLD_Plus1,
        rws_checker.find_invalid_well_known,
        rws_checker.find_invalid_alias_eSLDs,
        rws_checker.find_robots_tag,
        rws_checker.find_ads_txt,
        rws_checker.check_for_service_redirect,
    ]

    for check in check_list:
        try:
            check(check_sets)
        except Exception as inst:
            error_texts.append(inst)

    return error_texts


def main():
    args = sys.argv[1:]
    input_filepath = "related_website_sets.JSON"
    cli_primaries = []
    with_diff = False
    strict_formatting = False
    opts, _ = getopt.getopt(
        args, "i:p:", ["with_diff", "strict_formatting", "primaries="]
    )
    for opt, arg in opts:
        if opt == "-i":
            input_filepath = arg
        if opt == "--with_diff":
            with_diff = True
        if opt == "--strict_formatting":
            strict_formatting = True
        if opt == "--primaries" or opt == "-p":
            cli_primaries.extend(arg.split(","))

    rws_json_string = pathlib.Path(input_filepath).read_text()
    try:
        rws_sites = json.loads(rws_json_string)
    except Exception as inst:
        # If the file cannot be loaded, we will not run any other checks
        print(f"There was an error when parsing the JSON;\nerror was:  {inst}")
        return

    # Load the etlds from the public suffix list
    with open("effective_tld_names.dat", "rb") as f:
        etlds = PublicSuffixList(f)
    # Get all the ICANN domains
    icanns = set()
    with open("ICANN_domains") as f:
        for line in f:
            l = line.strip()
            icanns.add(l)

    rws_checker = RwsCheck(rws_sites, etlds, icanns)

    try:
        rws_checker.validate_schema("SCHEMA.json")
    except Exception as inst:
        # If the schema is invalid, we will not run any other checks
        print(inst)
        return

    error_texts = []
    check_sets = {}
    subtracted_sets = {}
    # If called with with_diff, we must determine the sets that are different
    # to properly construct our check_sets
    if with_diff:
        with open("related_website_sets.JSON") as f:
            try:
                old_sites = json.load(f)
            except Exception as inst:
                # If the file cannot be loaded, we will not run any other
                # checks
                print(
                    "There was an error when loading "
                    + "related_website_sets.JSON"
                    + "\nerror was: "
                    + inst
                )
                return
        old_checker = RwsCheck(old_sites, etlds, icanns)
        check_sets, subtracted_sets = find_diff_sets(
            old_checker.load_sets(), rws_checker.load_sets()
        )
    else:
        check_sets = rws_checker.load_sets()
        if cli_primaries:
            absent_primaries = [p for p in cli_primaries if p not in check_sets]
            for p in absent_primaries:
                error_texts.append(
                    "There was an error loading the set:\n"
                    + f'could not find set with primary site "{p}"'
                )
            check_sets = {p: check_sets[p] for p in cli_primaries if p in check_sets}

    # Run check on subtracted sets
    rws_checker.find_invalid_removal(subtracted_sets)
    # Run remaining technical checks
    error_texts += run_nonbreaking_checks(
        rws_checker, rws_json_string, strict_formatting, check_sets
    )
    # This message allows us to check the succes of our action
    if rws_checker.error_list or error_texts:
        for checker_error in rws_checker.error_list:
            print(checker_error)
        for error_text in error_texts:
            print(error_text)
    else:
        print("success", end="")


if __name__ == "__main__":
    main()

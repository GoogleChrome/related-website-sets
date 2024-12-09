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
import pathlib
import os
import sys
from publicsuffix2 import PublicSuffixList
from RwsCheck import RwsCheck

def parse_rws_json(rws_json_string, strict_formatting):
    """Attempts to parse `rws_json_string` as JSON and validate formatting if `strict_formatting` is true.

        Returns a tuple of the JSON dict and None if there were no errors,
        or None and the error message if there was an error.

        Args:
            rws_json_string: string
            strict_formatting: bool
        Returns:
            Tuple[Dict|None, string|None]
    """
    try:
        rws_sites = json.loads(rws_json_string)
    except Exception as inst:
        # If the file cannot be loaded, we will not run any other checks
        return (None, f"There was an error when parsing the JSON;\nerror was:  {inst}")
    # Notify of any formatting errors in the JSON
    if strict_formatting:
        # Add final newline by convention
        formatted_file = json.dumps(rws_sites, indent=2, ensure_ascii=False) + "\n"
        if rws_json_string != formatted_file:
            diff = difflib.ndiff(rws_json_string.splitlines(keepends=True), formatted_file.splitlines(keepends=True))
            # Only show lines with differences
            filtered_diff = (line for line in diff if len(line) > 0 and line[0] != ' ')
            joined_diff = ''.join(filtered_diff)
            return (None, f"Formatting for JSON is incorrect;\nerror was:\n```diff\n{joined_diff}\n```")
    return (rws_sites, None)

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
    diff_sets = {primary: rws
             for primary, rws in new_sets.items()
             if rws != old_sets.get(primary)
            }
    subtracted_sets = {
        primary: old_sets[primary]
        for primary in set(old_sets) - set(new_sets)
        if not any(rws.includes(primary) for rws in new_sets.values())
    }
    return diff_sets, subtracted_sets


def main():
    args = sys.argv[1:]
    input_filepath = 'related_website_sets.JSON'
    cli_primaries = []
    input_prefix = ''
    with_diff = False
    strict_formatting = False
    opts, _ = getopt.getopt(args, "i:p:", ["data_directory=", "with_diff",
                                         "strict_formatting", "primaries="])
    for opt, arg in opts:
        if opt == '-i':
            input_filepath = arg
        if opt == '--data_directory':
            input_prefix = arg
        if opt == '--with_diff':
            with_diff = True
        if opt == '--strict_formatting':
            strict_formatting = True
        if opt == '--primaries' or opt == '-p':
            cli_primaries.extend(arg.split(','))

    rws_json_string = pathlib.Path(input_filepath).read_text()
    (rws_sites, error) = parse_rws_json(rws_json_string, strict_formatting)
    if rws_sites == None or error != None:
        print(error)
        return

    # Load the etlds from the public suffix list
    etlds = PublicSuffixList(psl_file = os.path.join(input_prefix,'effective_tld_names.dat'))
    # Get all the ICANN domains
    icanns = set()
    with open(os.path.join(input_prefix,'ICANN_domains')) as f:
        for line in f:
            l = line.strip()
            icanns.add(l)

    rws_checker = RwsCheck(rws_sites, etlds, icanns)
    error_texts = []

    try:
        rws_checker.validate_schema(os.path.join(input_prefix,'SCHEMA.json'))
    except Exception as inst:
        # If the schema is invalid, we will not run any other checks
        print(inst)
        return
    
    # Check for exclusivity among all sets in the updated version
    try:
        rws_checker.check_exclusivity(rws_checker.load_sets())
    except Exception as inst:
            error_texts.append(inst)


    check_sets = {}
    subtracted_sets = {}
    # If called with with_diff, we must determine the sets that are different 
    # to properly construct our check_sets
    if with_diff:   
        with open(os.path.join(input_prefix,'related_website_sets.JSON')) as f:
            try:
                old_sites = json.load(f)
            except Exception as inst:
            # If the file cannot be loaded, we will not run any other checks
                print("There was an error when loading " +
                    os.path.join(input_prefix,'related_website_sets.JSON') + 
                    "\nerror was: " + inst)
                return
        old_checker = RwsCheck(old_sites, etlds, icanns)
        check_sets, subtracted_sets = find_diff_sets(old_checker.load_sets(), rws_checker.load_sets())
    else:
        check_sets = rws_checker.load_sets()
        if cli_primaries:
            absent_primaries = [p for p in cli_primaries if p not in check_sets]
            for p in absent_primaries:
                error_texts.append("There was an error loading the set:\n" + 
                    f"could not find set with primary site \"{p}\"")  
            check_sets = {p: check_sets[p] for p in cli_primaries if p in check_sets}

    # Run check on subtracted sets
    rws_checker.find_invalid_removal(subtracted_sets)

    # Run rest of checks
    check_list = [
        rws_checker.has_all_rationales,
        rws_checker.find_non_https_urls, 
        rws_checker.find_invalid_eTLD_Plus1,
        rws_checker.find_invalid_well_known, 
        rws_checker.find_invalid_alias_eSLDs, 
        rws_checker.find_robots_tag, 
        rws_checker.find_ads_txt, 
        rws_checker.check_for_service_redirect
        ]

    for check in check_list:
        try:
            check(check_sets)
        except Exception as inst:
            error_texts.append(inst)
    # This message allows us to check the succes of our action
    if rws_checker.error_list or error_texts:
        for checker_error in rws_checker.error_list:
            print(checker_error)
        for error_text in error_texts:
            print(error_text)
    else:
        print("success", end='')


if __name__ == '__main__':
    main() 

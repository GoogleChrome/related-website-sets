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
from RwsCheck import RwsCheck
import difflib
import json
import getopt
import sys
import os
from publicsuffix2 import PublicSuffixList

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
    input_file = 'related_website_sets.JSON'
    cli_primaries = []
    input_prefix = ''
    with_diff = False
    with_format = True
    opts, _ = getopt.getopt(args, "i:p:", ["data_directory=", "with_diff",
                                         "with_format", "primaries="])
    for opt, arg in opts:
        if opt == '-i':
            input_file = arg
        if opt == '--data_directory':
            input_prefix = arg
        if opt == '--with_diff':
            with_diff = True
        if opt == '--with_format':
            with_format = True
        if opt == '--primaries' or opt == '-p':
            cli_primaries.extend(arg.split(','))

    # Open and load the json of the new list
    with open(input_file) as f:
        try:
            rws_sites = json.load(f)
        except Exception as inst:
        # If the file cannot be loaded, we will not run any other checks
            print(f"There was an error when loading {input_file};" 
                  f"\nerror was:  {inst}")
            return
        # Notify of any formatting errrors in the JSON
        if with_format:
            f.seek(0)
            loaded_file = f.read()
            # Add final newline by convention
            formatted_file = json.dumps(rws_sites, indent=2, ensure_ascii=False) + "\n"
            if loaded_file != formatted_file:
                diff = difflib.ndiff(loaded_file.splitlines(keepends=True), formatted_file.splitlines(keepends=True))
                # Only show lines with differences
                filtered_diff = filter(lambda line: len(line) > 0 and line[0] != ' ', diff)
                joined_diff = ''.join(filtered_diff)
                print(f"Formatting for {input_file} is incorrect;" 
                      f"\nerror was:\n{joined_diff}")
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

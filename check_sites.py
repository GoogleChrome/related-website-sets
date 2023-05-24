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
from FpsCheck import FpsCheck
import json
import getopt
import sys
import os
from publicsuffix2 import PublicSuffixList

def find_diff_sets(old_sets, new_sets):
    diff_sets = {}
    subtracted_sets = {}
    difference = set(old_sets)^set(new_sets)
    for diff in difference:
        if diff in new_sets:
            diff_sets[diff] = new_sets[diff]
        else:
            subtracted_sets[diff] = old_sets[diff]
    return diff_sets, subtracted_sets


def main():
    args = sys.argv[1:]
    input_file = 'first_party_sets.JSON'
    input_prefix = ''
    with_diff = False
    opts, _ = getopt.getopt(args, "i:", ["data_directory=", "with_diff="])
    for opt, arg in opts:
        if opt == '-i':
            input_file = arg
        if opt == '--data_directory':
            input_prefix = arg
        if opt == '--with_diff':
            with_diff = arg.lower == "true"

    # Open and load the json of the new list
    with open(input_file) as f:
        try:
            fps_sites = json.load(f)
        except Exception as inst:
        # If the file cannot be loaded, we will not run any other checks
            print("There was an error when loading "+ input_file + 
                  "\nerror was: " + inst)
            exit()  
     

    # Load the etlds from the public suffix list
    etlds = PublicSuffixList(psl_file = os.path.join(input_prefix,'effective_tld_names.dat'))
    # Get all the ICANN domains
    icanns = set()
    with open(os.path.join(input_prefix,'ICANN_domains')) as f:
        for line in f:
            l = line.strip()
            icanns.add(l)

    fps_checker = FpsCheck(fps_sites, etlds, icanns)
    error_texts = []

    try:
        fps_checker.validate_schema(os.path.join(input_prefix,'SCHEMA.json'))
    except Exception as inst:
        # If the schema is invalid, we will not run any other checks
        print(inst)
        exit()

    check_sets = {}
    # If called with with_diff, we must determine the sets that are different 
    # to properly construct our check_sets
    if with_diff:   
        with open(os.path.join(input_prefix,'first_party_sets.JSON')) as f:
            try:
                old_sites = json.load(f)
            except Exception as inst:
            # If the file cannot be loaded, we will not run any other checks
                print("There was an error when loading " +
                    os.path.join(input_prefix,'first_party_sets.JSON') + 
                    "\nerror was: " + inst)
                exit()
        old_checker = FpsCheck(old_sites, etlds, icanns)
        check_sets, _ = find_diff_sets(old_checker.load_sets(), fps_checker.load_sets())

    else:
        check_sets = fps_checker.load_sets()
    

    check_list = [
        fps_checker.has_all_rationales, 
        fps_checker.check_exclusivity,
        fps_checker.find_non_https_urls, 
        fps_checker.find_invalid_eTLD_Plus1,
        fps_checker.find_invalid_well_known, 
        fps_checker.find_invalid_alias_eSLDs, 
        fps_checker.find_robots_txt, 
        fps_checker.find_ads_txt, 
        fps_checker.check_for_service_redirect
        ]

    for check in check_list:
        try:
            check(check_sets)
        except Exception as inst:
            error_texts.append(inst)
    # This message allows us to check the succes of our action
    if fps_checker.error_list or error_texts:
        for checker_error in fps_checker.error_list:
            print(checker_error)
        for error_text in error_texts:
            print(error_text)
    else:
        print("success", end='')


if __name__ == '__main__':
    main()

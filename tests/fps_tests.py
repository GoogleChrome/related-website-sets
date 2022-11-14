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
import unittest
import json
import sys
from jsonschema import ValidationError

sys.path.append('../FPS-Technical-Github-Checks')
from FpsSet import FpsSet
from FpsCheck import FpsCheck

class TestValidateSchema(unittest.TestCase):
    """A test suite for the validate_schema function of FpsCheck"""

    def test_no_primary(self):
        json_dict = {
            "sets":
            [
                {
                    "associatedSites": ["https://asociated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {
                        "https://associate1.com": "example rationale",
                        "https://service1.com": "example rationale",
                    },
                    "ccTLDs": {
                        "https://associate1.com": ["https://associate1.ca"]
                    }
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                      etlds='effective_tld_names.dat', icanns=set(['ca']))
        with self.assertRaises(ValidationError):
            fp.validate_schema()

    def test_no_rationaleBySite(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary1.com",
                    "associatedSites": ["https://associate1.com"],
                    "serviceSites": ["https://service1.com"],
                    "ccTLDs": {
                        "https://associate1.com": ["https://associate1.ca"]
                    }
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                      etlds='effective_tld_names.dat', icanns=set(['ca']))
        with self.assertRaises(ValidationError):
            fp.validate_schema()

    def test_invalid_field_type(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "ccTLDs": {
                        "https://primary.com": "https://primary.ca"
                    }
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                      etlds='effective_tld_names.dat', icanns=set(['ca']))
        with self.assertRaises(ValidationError):
            fp.validate_schema()

class TestLoadSets(unittest.TestCase):
    def test_collision_case(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "ccTLDs": {
                        "https://primary.com": "https://primary.ca"
                    }
                },
                {
                    "primary": "https://primary.com",
                    "ccTLDs": {
                        "https://primary.com": "https://primary.co.uk"
                    }
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                      etlds='effective_tld_names.dat',
                       icanns=set(['ca', 'co.uk']))
        loaded_sets = fp.load_sets()
        expected_sets = {
            'https://primary.com': FpsSet(ccTLDs={
                        "https://primary.com": "https://primary.ca"
                    }, 
                    primary="https://primary.com", 
                    associated_sites=None, 
                    service_sites=None)
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, 
        ["https://primary.com is already a primary of another site"])
    
    def test_expected_case(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "ccTLDs": {
                        "https://primary.com": "https://primary.ca"
                    }
                },
                {
                    "primary": "https://primary2.com",
                    "ccTLDs": {
                        "https://primary2.com": "https://primary2.co.uk"
                    }
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                      etlds='effective_tld_names.dat',
                       icanns=set(['ca', 'co.uk']))
        loaded_sets = fp.load_sets()
        expected_sets = {
            'https://primary.com': FpsSet(ccTLDs={
                        "https://primary.com": "https://primary.ca"
                    }, 
                    primary="https://primary.com", 
                    associated_sites=None, 
                    service_sites=None),
            'https://primary2.com': FpsSet(ccTLDs={
                        "https://primary2.com": "https://primary2.co.uk"
                    }, 
                    primary="https://primary2.com", 
                    associated_sites=None, 
                    service_sites=None)
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, [])

if __name__ == '__main__':
    unittest.main()

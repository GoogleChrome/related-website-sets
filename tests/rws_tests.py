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
import sys
import unittest

from jsonschema import ValidationError
from publicsuffix2 import PublicSuffixList
from unittest import mock
from requests import structures

sys.path.append(".")
from check_sites import find_diff_sets, parse_rws_json
from RwsCheck import RwsCheck, WELL_KNOWN
from RwsSet import RwsSet


class TestLoadFile(unittest.TestCase):
    """A test suite for the parse_rws_json function"""

    def test_parse_only(self):
        self.assertEqual(
            parse_rws_json("this is not json", False),
            (
                None,
                "There was an error when parsing the JSON;\nerror was:  Expecting value: line 1 column 1 (char 0)",
            ),
        )
        self.assertEqual(
            parse_rws_json('{\n  "a": "foo", \n    "b": "bar"\n}\n  ', False),
            ({"a": "foo", "b": "bar"}, None),
        )
        self.assertEqual(
            parse_rws_json('{\n  "a": "foo",\n  "b": "bar"\n}\n', False),
            ({"a": "foo", "b": "bar"}, None),
        )

    def test_parse_and_check_format(self):
        self.assertEqual(
            parse_rws_json("this is not json", True),
            (
                None,
                "There was an error when parsing the JSON;\nerror was:  Expecting value: line 1 column 1 (char 0)",
            ),
        )
        self.assertEqual(
            parse_rws_json('{\n  "a": "foo", \n    "b": "bar"\n}\n  ', True),
            (
                None,
                'Formatting for JSON is incorrect;\nerror was:\n```diff\n-   "a": "foo", \n?              -\n+   "a": "foo",\n-     "b": "bar"\n? --\n+   "b": "bar"\n-   \n```',
            ),
        )
        self.assertEqual(
            parse_rws_json('{\n  "a": "foo",\n  "b": "bar"\n}\n', True),
            ({"a": "foo", "b": "bar"}, None),
        )


class TestValidateSchema(unittest.TestCase):
    """A test suite for the validate_schema function of RwsCheck"""

    def test_no_primary(self):
        json_dict = {
            "sets": [
                {
                    "contact": "abc@example.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {
                        "https://associated1.com": "example rationale",
                        "https://service1.com": "example rationale",
                    },
                    "ccTLDs": {"https://associated1.com": ["https://associated1.ca"]},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set(["ca"]))
        with self.assertRaises(ValidationError):
            rws_check.validate_schema("SCHEMA.json")

    def test_no_rationaleBySite(self):
        json_dict = {
            "sets": [
                {
                    "contact": "abc@example.com",
                    "primary": "https://primary1.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "ccTLDs": {"https://associated1.com": ["https://associated1.ca"]},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set(["ca"]))
        with self.assertRaises(ValidationError):
            rws_check.validate_schema("SCHEMA.json")

    def test_invalid_field_type(self):
        json_dict = {
            "sets": [
                {
                    "contact": "abc@example.com",
                    "primary": "https://primary.com",
                    "ccTLDs": {"https://primary.com": "https://primary.ca"},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set(["ca"]))
        with self.assertRaises(ValidationError):
            rws_check.validate_schema("SCHEMA.json")

    def test_no_contact(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {
                        "https://associated1.com": "example rationale",
                        "https://service1.com": "example rationale",
                    },
                    "ccTLDs": {"https://associated1.com": ["https://associated1.ca"]},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set(["ca"]))
        with self.assertRaises(ValidationError):
            rws_check.validate_schema("SCHEMA.json")


class TestRwsSetEqual(unittest.TestCase):
    def test_equal_case(self):
        rws_1 = RwsSet(
            ccTLDs={"https://primary.com": ["https://primary.ca"]},
            primary="https://primary.com",
        )
        rws_2 = RwsSet(
            ccTLDs={"https://primary.com": ["https://primary.ca"]},
            primary="https://primary.com",
        )
        self.assertIsNot(rws_1, rws_2)
        self.assertEqual(rws_1, rws_2)
        self.assertEqual(rws_1, rws_1)

    def test_inequal_cases(self):
        rws_1 = RwsSet(
            ccTLDs={"https://primary.com": ["https://primary.ca"]},
            primary="https://primary.com",
        )
        rws_2 = RwsSet(
            ccTLDs={"https://primary.com": ["https://primary.co.uk"]},
            primary="https://primary.com",
        )
        self.assertNotEqual(rws_1, rws_2)

        rws_2.ccTLDs = {"https://primary.com": ["https://primary.ca"]}
        self.assertEqual(rws_1, rws_2)

        rws_1.associated_sites = ["https://associated1.com"]
        rws_2.associated_sites = ["https://associated2.com"]
        self.assertNotEqual(rws_1, rws_2)

        rws_2.associated_sites = ["https://associated1.com"]
        self.assertEqual(rws_1, rws_2)

        rws_1.service_sites = ["https://service1.com"]
        rws_2.service_sites = ["https://service2.com"]
        self.assertNotEqual(rws_1, rws_2)


class TestRwsIncludes(unittest.TestCase):
    def test_primary_case(self):
        rws = RwsSet(
            ccTLDs={"https://primary.com": ["https://primary.ca"]},
            primary="https://primary.com",
        )
        self.assertTrue(rws.includes("https://primary.com"))
        self.assertFalse(rws.includes("https://primary2.com"))

    def test_associated_case(self):
        rws = RwsSet(
            ccTLDs={},
            primary="https://primary.com",
            associated_sites=["https://associated1.com", "https://associated2.com"],
        )
        self.assertTrue(rws.includes("https://associated1.com"))
        self.assertTrue(rws.includes("https://associated2.com"))
        self.assertFalse(rws.includes("https://associated3.com"))

    def test_cctld_case(self):
        rws = RwsSet(
            ccTLDs={
                "https://primary.com": ["https://primary.ca", "https://primary.co.uk"]
            },
            primary="https://primary.com",
        )

        self.assertTrue(rws.includes("https://primary.ca"))
        self.assertFalse(rws.includes("https://primary.ca", with_ccTLDs=False))


class TestLoadSets(unittest.TestCase):
    def test_collision_case(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "ccTLDs": {"https://primary.com": ["https://primary.ca"]},
                },
                {
                    "primary": "https://primary.com",
                    "ccTLDs": {"https://primary.com": ["https://primary.co.uk"]},
                },
            ]
        }
        rws_check = RwsCheck(
            rws_sites=json_dict, etlds=None, icanns=set(["ca", "co.uk"])
        )
        loaded_sets = rws_check.load_sets()
        expected_sets = {
            "https://primary.com": RwsSet(
                ccTLDs={"https://primary.com": ["https://primary.ca"]},
                primary="https://primary.com",
            )
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(
            rws_check.error_list,
            ["https://primary.com is already a primary of another site"],
        )

    def test_expected_case(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "ccTLDs": {"https://primary.com": ["https://primary.ca"]},
                },
                {
                    "primary": "https://primary2.com",
                    "ccTLDs": {"https://primary2.com": ["https://primary2.co.uk"]},
                },
            ]
        }
        rws_check = RwsCheck(
            rws_sites=json_dict, etlds=None, icanns=set(["ca", "co.uk"])
        )
        loaded_sets = rws_check.load_sets()
        expected_sets = {
            "https://primary.com": RwsSet(
                ccTLDs={"https://primary.com": ["https://primary.ca"]},
                primary="https://primary.com",
            ),
            "https://primary2.com": RwsSet(
                ccTLDs={"https://primary2.com": ["https://primary2.co.uk"]},
                primary="https://primary2.com",
            ),
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(rws_check.error_list, [])


class TestHasRationales(unittest.TestCase):
    def test_no_rationales(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.has_all_rationales(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "There is no provided rationale for https://associated1.com",
                "There is no provided rationale for https://service1.com",
            ],
        )

    def test_expected_rationales_case(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {
                        "https://associated1.com": "example rationale",
                        "https://service1.com": "example rationale",
                    },
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        self.assertEqual(rws_check.error_list, [])


class TestCheckExclusivity(unittest.TestCase):
    def test_servicesets_overlap(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {},
                },
                {
                    "primary": "https://primary2.com",
                    "associatedSites": ["https://associated2.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {},
                },
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.check_exclusivity(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "These service sites are already registered in another"
                + " related website set: {'https://service1.com'}"
            ],
        )

    def test_primary_is_associate(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://primary2.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {},
                },
                {
                    "primary": "https://primary2.com",
                    "associatedSites": ["https://associated2.com"],
                    "serviceSites": ["https://service2.com"],
                    "rationaleBySite": {},
                },
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.check_exclusivity(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "This primary is already registered in another"
                + " related website set: https://primary2.com"
            ],
        )

    def test_primary_overlap(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://primary.com"],
                    "rationaleBySite": {},
                },
                {
                    "primary": "https://primary2.com",
                    "associatedSites": ["https://primary.com"],
                    "serviceSites": ["https://service2.com"],
                    "rationaleBySite": {},
                },
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.check_exclusivity(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "These service sites are already registered in another"
                + " related website set: {'https://primary.com'}",
                "These associated sites are already registered in another"
                + " related website set: {'https://primary.com'}",
            ],
        )

    def test_expected_case(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {},
                },
                {
                    "primary": "https://primary2.com",
                    "associatedSites": ["https://associated2.com"],
                    "serviceSites": ["https://service2.com"],
                    "rationaleBySite": {},
                },
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.check_exclusivity(loaded_sets)
        self.assertEqual(rws_check.error_list, [])


class TestFindNonHttps(unittest.TestCase):
    def test_no_https_in_primary(self):
        json_dict = {
            "sets": [
                {
                    "primary": "primary.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_non_https_urls(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            ["The provided primary site does not begin with https:// " + "primary.com"],
        )

    def test_no_https_in_ccTLD(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "ccTLDs": {"https://primary.com": ["primary.ca"]},
                    "rationaleBySite": {},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_non_https_urls(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            ["The provided alias site does not begin with" + " https:// primary.ca"],
        )

    def test_multi_no_https(self):
        json_dict = {
            "sets": [
                {
                    "primary": "primary.com",
                    "associatedSites": ["associated1.com"],
                    "serviceSites": ["service1.com"],
                    "ccTLDs": {"primary.com": ["primary.ca"]},
                    "rationaleBySite": {},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_non_https_urls(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "The provided primary site does not begin with https:// primary.com",
                "The provided aliased site does not begin with https:// primary.com",
                "The provided alias site does not begin with https:// primary.ca",
                "The provided associated site does not begin with https:// "
                + "associated1.com",
                "The provided service site does not begin with https:// service1.com",
            ],
        )


class TestFindInvalidETLD(unittest.TestCase):
    def test_invalid_etld_primary(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.c2om",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {},
                }
            ]
        }
        rws_check = RwsCheck(
            rws_sites=json_dict,
            etlds=PublicSuffixList(psl_file="effective_tld_names.dat"),
            icanns=set(),
        )
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_eTLD_Plus1(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            ["The provided primary site is not an eTLD+1: https://primary.c2om"],
        )

    def test_invalid_etld_cctld(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "ccTLDs": {"https://primary.com": ["https://primary.c2om"]},
                    "rationaleBySite": {},
                }
            ]
        }
        rws_check = RwsCheck(
            rws_sites=json_dict,
            etlds=PublicSuffixList(psl_file="effective_tld_names.dat"),
            icanns=set(),
        )
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_eTLD_Plus1(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            ["The provided alias site is not an eTLD+1: https://primary.c2om"],
        )

    def test_multi_invalid_etlds(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.c2om",
                    "associatedSites": ["https://associated1.c2om"],
                    "serviceSites": ["https://service1.c2om"],
                    "ccTLDs": {"https://primary.c2om": ["https://primary.c2om"]},
                    "rationaleBySite": {},
                }
            ]
        }
        rws_check = RwsCheck(
            rws_sites=json_dict,
            etlds=PublicSuffixList(psl_file="effective_tld_names.dat"),
            icanns=set(),
        )
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_eTLD_Plus1(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "The provided primary site is not an eTLD+1: https://primary.c2om",
                "The provided aliased site is not an eTLD+1: https://primary.c2om",
                "The provided alias site is not an eTLD+1: https://primary.c2om",
                "The provided associated site is not an eTLD+1: https://associated1.c2om",
                "The provided service site is not an eTLD+1: https://service1.c2om",
            ],
        )

    def test_not_etld_plus1(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://subdomain.primary.com",
                    "ccTLDs": {},
                    "rationaleBySite": {},
                }
            ]
        }
        rws_check = RwsCheck(
            rws_sites=json_dict,
            etlds=PublicSuffixList(psl_file="effective_tld_names.dat"),
            icanns=set(),
        )
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_eTLD_Plus1(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "The provided primary site is not an eTLD+1: https://subdomain.primary.com"
            ],
        )

    def test_valid_etld_plus1(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com.ar",
                    "ccTLDs": {},
                    "rationaleBySite": {},
                }
            ]
        }
        rws_check = RwsCheck(
            rws_sites=json_dict,
            etlds=PublicSuffixList(psl_file="effective_tld_names.dat"),
            icanns=set(),
        )
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_eTLD_Plus1(loaded_sets)
        self.assertEqual(rws_check.error_list, [])

    def test_valid_tld_plus1(self):
        json_dict = {
            "sets": [
                {"primary": "https://primary.com", "ccTLDs": {}, "rationaleBySite": {}}
            ]
        }
        rws_check = RwsCheck(
            rws_sites=json_dict,
            etlds=PublicSuffixList(psl_file="effective_tld_names.dat"),
            icanns=set(),
        )
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_eTLD_Plus1(loaded_sets)
        self.assertEqual(rws_check.error_list, [])

    def test_just_suffix(self):
        json_dict = {"sets": [{"primary": "https://7.bg", "rationaleBySite": {}}]}
        rws_check = RwsCheck(
            rws_sites=json_dict,
            etlds=PublicSuffixList(psl_file="effective_tld_names.dat"),
            icanns=set(),
        )
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_eTLD_Plus1(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            ["The provided primary site is not an eTLD+1: https://7.bg"],
        )


class TestFindInvalidESLDs(unittest.TestCase):
    def test_invalid_alias_name(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "ccTLDs": {"https://primary.com": ["https://primary2.ca"]},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set(["ca"]))
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_alias_eSLDs(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "The following top level domain "
                + "must match: https://primary.com, but is instead: "
                + "https://primary2.ca"
            ],
        )

    def test_invalid_alias_ccTLD(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "ccTLDs": {"https://primary.com": ["https://primary.gov"]},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set(["ca"]))
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_alias_eSLDs(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "The provided country code: gov, "
                + "in: https://primary.gov is not a ICANN registered country code"
            ],
        )

    def test_invalid_com_in_alias(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.edu",
                    "ccTLDs": {"https://primary.edu": ["https://primary.com"]},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set(["ca"]))
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_alias_eSLDs(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "The provided country code: com, "
                + "in: https://primary.com is not a ICANN registered country code"
            ],
        )

    def test_valid_com_in_alias(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.ca",
                    "ccTLDs": {"https://primary.ca": ["https://primary.com"]},
                },
                {
                    "primary": "https://primary2.co.uk",
                    "ccTLDs": {"https://primary2.co.uk": ["https://primary2.com"]},
                },
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set(["ca", "uk"]))
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_alias_eSLDs(loaded_sets)
        self.assertEqual(rws_check.error_list, [])

    def test_invalid_associated_alias(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://associated.com"],
                    "ccTLDs": {"https://associated.com": ["https://associated.gov"]},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set(["ca"]))
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_alias_eSLDs(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "The provided country code: gov, "
                + "in: https://associated.gov is not a ICANN registered country code"
            ],
        )

    def test_valid_associated_alias(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://associated.com"],
                    "ccTLDs": {"https://associated.com": ["https://associated.ca"]},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set(["ca"]))
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_alias_eSLDs(loaded_sets)
        self.assertEqual(rws_check.error_list, [])

    def test_expected_esld(self):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "ccTLDs": {"https://primary.com": ["https://primary.ca"]},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set(["ca"]))
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_alias_eSLDs(loaded_sets)
        self.assertEqual(rws_check.error_list, [])


class TestFindDiff(unittest.TestCase):
    def test_unchanged_sets(self):
        old_sets = {
            "https://primary.com": RwsSet(
                primary="https://primary.com",
                ccTLDs={"https://primary.com": ["https://primary.ca"]},
            )
        }
        new_sets = {
            "https://primary.com": RwsSet(
                primary="https://primary.com",
                ccTLDs={"https://primary.com": ["https://primary.ca"]},
            )
        }
        self.assertEqual(find_diff_sets(old_sets, new_sets), ({}, {}))

    def test_added_set(self):
        old_sets = {
            "https://primary.com": RwsSet(
                primary="https://primary.com",
                ccTLDs={"https://primary.com": ["https://primary.ca"]},
            )
        }
        new_sets = {
            "https://primary.com": RwsSet(
                primary="https://primary.com",
                ccTLDs={"https://primary.com": ["https://primary.ca"]},
            ),
            "https://primary2.com": RwsSet(
                primary="https://primary2.com",
                ccTLDs={"https://primary2.com": ["https://primary2.ca"]},
            ),
        }
        expected_diff_sets = {
            "https://primary2.com": RwsSet(
                primary="https://primary2.com",
                ccTLDs={"https://primary2.com": ["https://primary2.ca"]},
            )
        }
        self.assertEqual(find_diff_sets(old_sets, new_sets), (expected_diff_sets, {}))

    def test_removed_set(self):
        old_sets = {
            "https://primary.com": RwsSet(
                primary="https://primary.com",
                ccTLDs={"https://primary.com": ["https://primary.ca"]},
            ),
            "https://primary2.com": RwsSet(
                primary="https://primary2.com",
                ccTLDs={"https://primary2.com": ["https://primary2.ca"]},
            ),
        }
        new_sets = {
            "https://primary.com": RwsSet(
                primary="https://primary.com",
                ccTLDs={"https://primary.com": ["https://primary.ca"]},
            )
        }
        expected_subtracted_sets = {
            "https://primary2.com": RwsSet(
                primary="https://primary2.com",
                ccTLDs={"https://primary2.com": ["https://primary2.ca"]},
            )
        }
        self.assertEqual(
            find_diff_sets(old_sets, new_sets), ({}, expected_subtracted_sets)
        )

    def test_added_and_removed_set(self):
        old_sets = {
            "https://primary.com": RwsSet(
                primary="https://primary.com",
                ccTLDs={"https://primary.com": ["https://primary.ca"]},
            )
        }
        new_sets = {
            "https://primary2.com": RwsSet(
                primary="https://primary2.com",
                ccTLDs={"https://primary2.com": ["https://primary2.ca"]},
            )
        }
        self.assertEqual(find_diff_sets(old_sets, new_sets), (new_sets, old_sets))

    def test_modified_set(self):
        old_sets = {
            "https://primary.com": RwsSet(
                primary="https://primary.com",
                ccTLDs={"https://primary.com": ["https://primary.ca"]},
            )
        }
        new_sets = {
            "https://primary.com": RwsSet(
                primary="https://primary.com",
                ccTLDs={"https://primary.com": ["https://primary.co.uk"]},
            )
        }
        self.assertEqual(find_diff_sets(old_sets, new_sets), (new_sets, {}))

    def test_primary_to_member(self):
        old_sets = {
            "https://primary.com": RwsSet(
                primary="https://primary.com",
                ccTLDs={"https://primary.com": ["https://primary.ca"]},
            ),
            "https://primary2.com": RwsSet(primary="https://primary2.com", ccTLDs={}),
        }
        new_sets = {
            "https://primary.com": RwsSet(
                primary="https://primary.com",
                associated_sites=["https://primary2.com"],
                ccTLDs={"https://primary.com": ["https://primary.ca"]},
            )
        }
        self.assertEqual(find_diff_sets(old_sets, new_sets), (new_sets, {}))


# This method will be used in tests below to mock get requests
def mock_get(*args, **kwargs):
    class MockedGetResponse:
        def __init__(self, headers, status_code):
            self.headers = structures.CaseInsensitiveDict(headers)
            self.status_code = status_code
            self.url = args[0]

    if args[0] == "https://service1.com":
        return MockedGetResponse({}, 200)
    elif args[0] == "https://service2.com":
        return MockedGetResponse({"X-Robots-Tag": "foo"}, 200)
    elif args[0] == "https://service3.com":
        return MockedGetResponse({"X-Robots-Tag": "noindex"}, 200)
    elif args[0] == "https://service4.com":
        return MockedGetResponse({"X-Robots-Tag": "none"}, 200)
    elif args[0] == "https://service5.com/ads.txt":
        return MockedGetResponse({}, 400)
    elif args[0] == "https://service6.com":
        mgr = MockedGetResponse({}, 200)
        mgr.url = "https://example.com"
        return mgr
    elif args[0] == "https://service7.com":
        if "allow_redirects" in kwargs:
            if kwargs["allow_redirects"] != True:
                return MockedGetResponse({"X-Robots-Tag": "noindex"}, 200)
        return MockedGetResponse({"X-Robots-Tag": "foo"}, 200)
    elif args[0].startswith("https://service"):
        return MockedGetResponse({}, 200)
    elif args[0] == "https://primary1.com" + WELL_KNOWN:
        return MockedGetResponse({}, 200)

    return MockedGetResponse(None, 404)


def mock_open_and_load_json(*args, **kwargs):
    class MockedJsonResponse:
        def __init__(self, json):
            self.json = json

    if args[0] == "https://primary1.com" + WELL_KNOWN:
        return {
            "primary": "https://primary1.com",
            "associatedSites": ["https://not-in-list.com"],
        }
    elif args[0] == "https://expected-associated.com" + WELL_KNOWN:
        return {"primary": "https://primary1.com"}
    elif args[0] == "https://primary2.com" + WELL_KNOWN:
        return {
            "primary": "https://wrong-primary.com",
            "associatedSites": ["https://associated1.com"],
        }
    elif args[0] == "https://associated1.com" + WELL_KNOWN:
        return {"primary": "https://primary2.com"}
    elif args[0] == "https://primary3.com" + WELL_KNOWN:
        return {
            "primary": "https://primary3.com",
            "associatedSites": ["https://associated2.com"],
        }
    elif args[0] == "https://associated2.com" + WELL_KNOWN:
        return {"primary": "https://wrong-primary.com"}
    elif args[0] == "https://primary4.com" + WELL_KNOWN:
        return {
            "primary": "https://primary4.com",
            "associatedSites": ["https://associated3.com"],
        }
    elif args[0] == "https://associated3.com" + WELL_KNOWN:
        return {
            "primary": "https://primary4.com",
            "associatedSites": ["https://associated3.com"],
            "unchecked": "some unchecked field",
        }
    elif args[0] == "https://primary5.com" + WELL_KNOWN:
        return {"primary": "https://primary5.com", "unchecked": "An unchecked field"}
    return {"primary": None}


# Our test case class


class MockTestsClass(unittest.TestCase):

    # We patch requests.get with our mocked method. We'll pass
    # in the relevant urls, and get our responses for robots checks
    @mock.patch("requests.get", side_effect=mock_get)
    def test_robots(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service1.com"],
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_robots_tag(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "The service site "
                + "https://service1.com "
                + "does not have an X-Robots-Tag in its header"
            ],
        )

    @mock.patch("requests.get", side_effect=mock_get)
    def test_robots_wrong_tag(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service2.com"],
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_robots_tag(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "The service site "
                + "https://service2.com "
                + "does not have a 'noindex' or 'none' tag in its header"
            ],
        )

    @mock.patch("requests.get", side_effect=mock_get)
    def test_robots_expected_tag(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service3.com"],
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_robots_tag(loaded_sets)
        self.assertEqual(rws_check.error_list, [])

    @mock.patch("requests.get", side_effect=mock_get)
    def test_robots_none_tag(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service4.com"],
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_robots_tag(loaded_sets)
        self.assertEqual(rws_check.error_list, [])

    @mock.patch("requests.get", side_effect=mock_get)
    def test_robots_redirects(self, mock_get):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service7.com"],
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_robots_tag(loaded_sets)
        self.assertEqual(rws_check.error_list, [])

    # We run a similar set of mock tests for ads.txt
    @mock.patch("requests.get", side_effect=mock_get)
    def test_ads(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service1.com"],
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_ads_txt(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "The service site "
                + "https://service1.com has an ads.txt file, this "
                + "violates the policies for service sites"
            ],
        )

    @mock.patch("requests.get", side_effect=mock_get)
    def test_ads(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service5.com"],
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_ads_txt(loaded_sets)
        self.assertEqual(rws_check.error_list, [])

    # We run a similar set of mock tests for redirect check
    @mock.patch("requests.get", side_effect=mock_get)
    def test_non_redirect(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service1.com"],
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.check_for_service_redirect(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            ["The service site " + "must not be an endpoint: https://service1.com"],
        )

    @mock.patch("requests.get", side_effect=mock_get)
    def test_proper_redirect(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service6.com"],
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.check_for_service_redirect(loaded_sets)
        self.assertEqual(rws_check.error_list, [])

    @mock.patch("requests.get", side_effect=mock_get)
    def test_404_redirect(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://no-such-service.com"],
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.check_for_service_redirect(loaded_sets)
        self.assertEqual(rws_check.error_list, [])

    # Now we test check_invalid_removal by checking for an error 404
    @mock.patch("requests.get", side_effect=mock_get)
    def test_find_invalid_removal(self, mock_get):
        subtracted_sets = {
            "https://primary1.com": RwsSet(primary="https://primary1.com", ccTLDs={})
        }
        rws_check = RwsCheck(rws_sites={}, etlds=None, icanns=set())
        rws_check.find_invalid_removal(subtracted_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "The set associated with "
                + "https://primary1.com was removed from the list, but "
                + "https://primary1.com/.well-known/related-website-set.json does "
                + "not return error 404."
            ],
        )

    @mock.patch("requests.get", side_effect=mock_get)
    def test_find_valid_removal(self, mock_get):
        subtracted_sets = {
            "https://primary2.com": RwsSet(primary="https://primary2.com", ccTLDs={})
        }
        rws_check = RwsCheck(rws_sites={}, etlds=None, icanns=set())
        rws_check.find_invalid_removal(subtracted_sets)
        self.assertEqual(rws_check.error_list, [])

    # Now we test the mocked open_and_load_json to test the well-known checks
    @mock.patch(
        "RwsCheck.RwsCheck.open_and_load_json", side_effect=mock_open_and_load_json
    )
    def test_primary_page_differs(self, mock_open_and_load_json):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary1.com",
                    "associatedSites": ["https://expected-associated.com"],
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_well_known(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "Encountered an inequality between the PR submission and the "
                + "/.well-known/related-website-set.json file:\n\tassociatedSites was "
                + "['https://expected-associated.com'] in the PR, and "
                + "['https://not-in-list.com'] in the well-known.\n\tDiff was: "
                + "['https://expected-associated.com', 'https://not-in-list.com']."
            ],
        )

    @mock.patch(
        "RwsCheck.RwsCheck.open_and_load_json", side_effect=mock_open_and_load_json
    )
    def test_wrong_primary_name(self, mock_open_and_load_json):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary2.com",
                    "associatedSites": ["https://associated1.com"],
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_well_known(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "The /.well-known/related-website-set.json"
                + " set's primary (https://wrong-primary.com) did not equal the PR "
                + "set's primary (https://primary2.com)"
            ],
        )

    @mock.patch(
        "RwsCheck.RwsCheck.open_and_load_json", side_effect=mock_open_and_load_json
    )
    def test_associate_wrong_page(self, mock_open_and_load_json):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary3.com",
                    "associatedSites": ["https://associated2.com"],
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_well_known(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "The listed associated site "
                + "did not have https://primary3.com listed as its primary: "
                + "https://associated2.com"
            ],
        )

    @mock.patch(
        "RwsCheck.RwsCheck.open_and_load_json", side_effect=mock_open_and_load_json
    )
    def test_expected_case(self, mock_open_and_load_json):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary4.com",
                    "associatedSites": ["https://associated3.com"],
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_well_known(loaded_sets)
        self.assertEqual(rws_check.error_list, [])

    @mock.patch(
        "RwsCheck.RwsCheck.open_and_load_json", side_effect=mock_open_and_load_json
    )
    def test_absent_field(self, mock_open_and_load_json):
        json_dict = {"sets": [{"primary": "https://primary1.com"}]}
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_well_known(loaded_sets)
        self.assertEqual(
            rws_check.error_list,
            [
                "Encountered an inequality between the PR submission and the "
                + "/.well-known/related-website-set.json file:\n\tassociatedSites was [] in "
                + "the PR, and ['https://not-in-list.com'] in the well-known.\n\tDiff "
                + "was: ['https://not-in-list.com']."
            ],
        )

    @mock.patch(
        "RwsCheck.RwsCheck.open_and_load_json", side_effect=mock_open_and_load_json
    )
    def test_differing_fields(self, mock_open_and_load_json):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary1.com",
                    "serviceSites": ["https://expected-associated.com"],
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_well_known(loaded_sets)
        self.assertEqual(
            sorted(rws_check.error_list),
            [
                "Encountered an inequality between the PR submission and the "
                + "/.well-known/related-website-set.json file:\n\tassociatedSites was [] in "
                + "the PR, and ['https://not-in-list.com'] in the well-known.\n\tDiff "
                + "was: ['https://not-in-list.com'].",
                "Encountered an inequality between the PR submission and the "
                + "/.well-known/related-website-set.json file:\n\tserviceSites was "
                + "['https://expected-associated.com'] in the PR, and [] in the "
                + "well-known.\n\tDiff was: ['https://expected-associated.com'].",
            ],
        )

    @mock.patch(
        "RwsCheck.RwsCheck.open_and_load_json", side_effect=mock_open_and_load_json
    )
    def test_unchecked_field(self, mock_open_and_load_json):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary4.com",
                    "associatedSites": ["https://associated3.com"],
                    "rationaleBySite": {"https://associated3.com": "A rationale."},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_well_known(loaded_sets)
        self.assertEqual(sorted(rws_check.error_list), [])

    @mock.patch(
        "RwsCheck.RwsCheck.open_and_load_json", side_effect=mock_open_and_load_json
    )
    def test_unchecked_well_known_field(self, mock_open_and_load_json):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary5.com",
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set())
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_well_known(loaded_sets)
        self.assertEqual(sorted(rws_check.error_list), [])

    @mock.patch(
        "RwsCheck.RwsCheck.open_and_load_json", side_effect=mock_open_and_load_json
    )
    def test_unexpteced_cctTLD(self, mock_open_and_load_json):
        json_dict = {
            "sets": [
                {
                    "primary": "https://primary4.com",
                    "associatedSites": ["https://associated3.com"],
                    "ccTLDs": {"https://associated3.com": ["https://associated3.ca"]},
                }
            ]
        }
        rws_check = RwsCheck(rws_sites=json_dict, etlds=None, icanns=set(["ca"]))
        loaded_sets = rws_check.load_sets()
        rws_check.find_invalid_well_known(loaded_sets)
        self.assertEqual(
            sorted(rws_check.error_list),
            [
                "Encountered an inequality between the PR submission and the "
                "/.well-known/related-website-set.json file:\n\t"
                + "https://associated3.com alias list was ['https://associated3.ca']"
                + " in the PR, and [] in the well-known.\n\tDiff was: "
                + "['https://associated3.ca'].",
                "The listed associated site did not have https://primary4.com "
                + "listed as its primary: https://associated3.ca",
            ],
        )


if __name__ == "__main__":
    unittest.main()

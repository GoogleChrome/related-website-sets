import unittest
import sys
from jsonschema import ValidationError
from publicsuffix2 import PublicSuffixList
from unittest import mock

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
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {
                        "https://associated1.com": "example rationale",
                        "https://service1.com": "example rationale",
                    },
                    "ccTLDs": {
                        "https://associated1.com": ["https://associated1.ca"]
                    }
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                      etlds=None, icanns=set(['ca']))
        with self.assertRaises(ValidationError):
            fp.validate_schema()

    def test_no_rationaleBySite(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary1.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "ccTLDs": {
                        "https://associated1.com": ["https://associated1.ca"]
                    }
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                      etlds=None, icanns=set(['ca']))
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
                      etlds=None, icanns=set(['ca']))
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
                      etlds=None,
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
                      etlds=None,
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

class TestHasRationales(unittest.TestCase):
    def test_no_rationales(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {}
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                      etlds=None,
                       icanns=set())
        loaded_sets = fp.load_sets()
        fp.has_all_rationales(loaded_sets)
        expected_sets = {
            'https://primary.com': FpsSet(ccTLDs= None,
                    primary="https://primary.com", 
                    associated_sites=["https://associated1.com"], 
                    service_sites=["https://service1.com"])
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, 
        ["There is no provided rationale for https://associated1.com", 
        "There is no provided rationale for https://service1.com"])
    
    def test_expected_rationales_case(self):
        json_dict = {
            "sets":
            [
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
        fp = FpsCheck(fps_sites=json_dict,
                      etlds=None,
                       icanns=set())
        loaded_sets = fp.load_sets()
        expected_sets = {
            'https://primary.com': FpsSet(ccTLDs=None, 
                    primary="https://primary.com", 
                    associated_sites=["https://associated1.com"], 
                    service_sites=["https://service1.com"])
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, [])  
    def test_no_expected_rationales_case(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com"
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                      etlds=None,
                       icanns=set())
        loaded_sets = fp.load_sets()
        expected_sets = {
            'https://primary.com': FpsSet(ccTLDs=None, 
                    primary="https://primary.com", associated_sites=None, service_sites=None)
        }
        fp.has_all_rationales(loaded_sets)
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, [])  

class TestCheckExclusivity(unittest.TestCase):
    def test_servicesets_overlap(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {}
                },
                {
                    "primary": "https://primary2.com",
                    "associatedSites": ["https://associated2.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {}
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                      etlds=None,
                       icanns=set())
        loaded_sets = fp.load_sets()
        fp.check_exclusivity(loaded_sets)
        expected_sets = {
            'https://primary.com': FpsSet(ccTLDs= None,
                    primary="https://primary.com", 
                    associated_sites=["https://associated1.com"], 
                    service_sites=["https://service1.com"]),
            'https://primary2.com': FpsSet(ccTLDs= None,
                    primary="https://primary2.com", 
                    associated_sites=["https://associated2.com"], 
                    service_sites=["https://service1.com"]),
                    
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, 
         ["These service sites are already registered in another"
                        + " first party set: {'https://service1.com'}"])

    def test_primary_is_associate(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://primary2.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {}
                },
                {
                    "primary": "https://primary2.com",
                    "associatedSites": ["https://associated2.com"],
                    "serviceSites": ["https://service2.com"],
                    "rationaleBySite": {}
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                      etlds=None,
                       icanns=set())
        loaded_sets = fp.load_sets()
        fp.check_exclusivity(loaded_sets)
        expected_sets = {
            'https://primary.com': FpsSet(ccTLDs= None,
                    primary="https://primary.com", 
                    associated_sites=["https://primary2.com"], 
                    service_sites=["https://service1.com"]),
            'https://primary2.com': FpsSet(ccTLDs= None,
                    primary="https://primary2.com", 
                    associated_sites=["https://associated2.com"], 
                    service_sites=["https://service2.com"]),
                    
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, 
         ["This primary is already registered in another"
                        + " first party set: https://primary2.com"])
    def test_expected_case(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {}
                },
                {
                    "primary": "https://primary2.com",
                    "associatedSites": ["https://associated2.com"],
                    "serviceSites": ["https://service2.com"],
                    "rationaleBySite": {}
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                      etlds=None,
                       icanns=set())
        loaded_sets = fp.load_sets()
        fp.check_exclusivity(loaded_sets)
        expected_sets = {
            'https://primary.com': FpsSet(ccTLDs= None,
                    primary="https://primary.com", 
                    associated_sites=["https://associated1.com"], 
                    service_sites=["https://service1.com"]),
            'https://primary2.com': FpsSet(ccTLDs= None,
                    primary="https://primary2.com", 
                    associated_sites=["https://associated2.com"], 
                    service_sites=["https://service2.com"]),
                    
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, [])
    
class TestFindNonHttps(unittest.TestCase):
    def test_no_https_in_primary(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "primary.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {}
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                      etlds=None,
                       icanns=set())
        loaded_sets = fp.load_sets()
        fp.find_non_https_urls(loaded_sets)
        expected_sets = {
            'primary.com': FpsSet(ccTLDs= None,
                    primary="primary.com", 
                    associated_sites=["https://associated1.com"], 
                    service_sites=["https://service1.com"])         
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, 
         ["The provided primary site does not begin with https:// " +
         "primary.com"])
    def test_no_https_in_ccTLD(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "ccTLDs": {
                        "https://primary.com": ["primary.ca"]
                    },
                    "rationaleBySite": {}
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                      etlds=None,
                       icanns=set())
        loaded_sets = fp.load_sets()
        fp.find_non_https_urls(loaded_sets)
        expected_sets = {
            'https://primary.com': FpsSet(
                    primary="https://primary.com", 
                    associated_sites=["https://associated1.com"], 
                    service_sites=["https://service1.com"],
                    ccTLDs={
                        "https://primary.com": ["primary.ca"]
                    })         
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, 
         ["The provided alias site does not begin with" +
                                " https:// primary.ca"])
    def test_multi_no_https(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "primary.com",
                    "associatedSites": ["associated1.com"],
                    "serviceSites": ["service1.com"],
                    "ccTLDs": {
                        "primary.com": ["primary.ca"]
                    },
                    "rationaleBySite": {}
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                      etlds=None,
                       icanns=set())
        loaded_sets = fp.load_sets()
        fp.find_non_https_urls(loaded_sets)
        expected_sets = {
            'primary.com': FpsSet(
                    primary="primary.com", 
                    associated_sites=["associated1.com"], 
                    service_sites=["service1.com"],
                    ccTLDs={
                        "primary.com": ["primary.ca"]
                    })         
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, 
         [
        "The provided primary site does not begin with https:// primary.com", 
        "The provided alias does not begin with https:// primary.com",
        "The provided alias site does not begin with https:// primary.ca",
        "The provided associated site does not begin with https:// " + 
        "associated1.com",
        "The provided service site does not begin with https:// service1.com"
         ])
class TestFindInvalidETLD(unittest.TestCase):
    def test_invalid_etld_primary(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.c2om",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "rationaleBySite": {}
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                     etlds=PublicSuffixList(
                        psl_file = 'effective_tld_names.dat'),
                     icanns=set())
        loaded_sets = fp.load_sets()
        fp.find_invalid_eTLD_Plus1(loaded_sets)
        expected_sets = {
            'https://primary.c2om': FpsSet(ccTLDs= None,
                    primary="https://primary.c2om", 
                    associated_sites=["https://associated1.com"], 
                    service_sites=["https://service1.com"])         
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, 
         ["The provided primary site does not have an eTLD in the" +
                    " Public suffix list: https://primary.c2om"])
    def test_invalid_etld_cctld(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "associatedSites": ["https://associated1.com"],
                    "serviceSites": ["https://service1.com"],
                    "ccTLDs": {
                        "https://primary.com": ["https://primary.c2om"]
                    },
                    "rationaleBySite": {}
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                     etlds=PublicSuffixList(
                        psl_file = 'effective_tld_names.dat'),
                     icanns=set())
        loaded_sets = fp.load_sets()
        fp.find_invalid_eTLD_Plus1(loaded_sets)
        expected_sets = {
            'https://primary.com': FpsSet(
                    primary="https://primary.com", 
                    associated_sites=["https://associated1.com"], 
                    service_sites=["https://service1.com"],
                    ccTLDs={
                        "https://primary.com": ["https://primary.c2om"]
                    })         
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, 
         ["The provided aliased site does not have an eTLD in the" +
                    " Public suffix list: https://primary.c2om"])
    def test_multi_invalid_etlds(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.c2om",
                    "associatedSites": ["https://associated1.c2om"],
                    "serviceSites": ["https://service1.c2om"],
                    "ccTLDs": {
                        "https://primary.c2om": ["https://primary.c2om"]
                    },
                    "rationaleBySite": {}
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                     etlds=PublicSuffixList(
                        psl_file = 'effective_tld_names.dat'),
                     icanns=set())
        loaded_sets = fp.load_sets()
        fp.find_invalid_eTLD_Plus1(loaded_sets)
        expected_sets = {
            'https://primary.c2om': FpsSet(
                    primary="https://primary.c2om", 
                    associated_sites=["https://associated1.c2om"], 
                    service_sites=["https://service1.c2om"],
                    ccTLDs={
                        "https://primary.c2om": ["https://primary.c2om"]
                    })         
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, 
         ["The provided primary site does not have an eTLD in the" +
                    " Public suffix list: https://primary.c2om",
          "The provided alias does not have an eTLD in the" +
                    " Public suffix list: https://primary.c2om",
          "The provided aliased site does not have an eTLD in the" +
                    " Public suffix list: https://primary.c2om",
          "The provided associated site does not have an eTLD in the" +
                    " Public suffix list: https://associated1.c2om",
          "The provided service site does not have an eTLD in the" +
                    " Public suffix list: https://service1.c2om"])
        
class TestFindInvalidESLDs(unittest.TestCase):
    def test_invalid_alias_name(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "ccTLDs": {
                        "https://primary.com": ["https://primary2.ca"]
                    }
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                     etlds=None,
                     icanns=set(["ca"]))
        loaded_sets = fp.load_sets()
        fp.find_invalid_alias_eSLDs(loaded_sets)
        expected_sets = {
            'https://primary.com': 
            FpsSet(
                    primary="https://primary.com", 
                    associated_sites=None,
                    service_sites=None,
                    ccTLDs={
                        "https://primary.com": ["https://primary2.ca"]
                    }
                    )
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, ["The following top level domain " + 
        "must match: https://primary.com, but is instead: "+
        "https://primary2.ca"])
    def test_invalid_alias_ccTLD(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "ccTLDs": {
                        "https://primary.com": ["https://primary.gov"]
                    }
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                     etlds=None,
                     icanns=set(["ca"]))
        loaded_sets = fp.load_sets()
        fp.find_invalid_alias_eSLDs(loaded_sets)
        expected_sets = {
            'https://primary.com': 
            FpsSet(
                    primary="https://primary.com", 
                    associated_sites=None,
                    service_sites=None,
                    ccTLDs={
                        "https://primary.com": ["https://primary.gov"]
                    }
                    )
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, ["The provided country code: gov, "+
            "in: https://primary.gov is not a ICANN registered country code"])
    def test_expected_esld(self):
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "ccTLDs": {
                        "https://primary.com": ["https://primary.ca"]
                    }
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                     etlds=None,
                     icanns=set(["ca"]))
        loaded_sets = fp.load_sets()
        fp.find_invalid_alias_eSLDs(loaded_sets)
        expected_sets = {
            'https://primary.com': 
            FpsSet(
                    primary="https://primary.com", 
                    associated_sites=None,
                    service_sites=None,
                    ccTLDs={
                        "https://primary.com": ["https://primary.ca"]
                    }
                    )
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, [])

# This method will be used in tests below to mock get requests
def mock_get(*args, **kwargs):
    class MockedGetResponse:
        def __init__(self, headers, status_code):
            self.headers = headers
            self.status_code = status_code
            self.url = args[0]

        def json(self):
            return self.json_data

    if args[0] == 'https://service1.com':
        return MockedGetResponse({}, 200)
    elif args[0] == 'https://service2.com':
        return MockedGetResponse({"X-Robots-Tag":"foo"}, 200)
    elif args[0] == 'https://service3.com':
        return MockedGetResponse({"X-Robots-Tag":"noindex"}, 200)
    elif args[0] == 'https://service4.com/robots.txt':
        return MockedGetResponse({}, 400)
    elif args[0] == 'https://service5.com/ads.txt':
        return MockedGetResponse({}, 400)
    elif args[0] == 'https://service6.com':
        mgr = MockedGetResponse({}, 200)
        mgr.url = 'https://example.com'
        return mgr
    elif args[0].startswith('https://service'):
        return MockedGetResponse({},200)
    
    return MockedGetResponse(None, 404)

# Our test case class
class MockTestsClass(unittest.TestCase):

    # We patch requests.get with our mocked method. We'll pass
    # in the relevant urls, and get our responses for robots checks
    @mock.patch('requests.get', side_effect=mock_get)
    def test_robots(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service1.com"]
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                     etlds=None,
                     icanns=set())
        loaded_sets = fp.load_sets()
        fp.find_robots_txt(loaded_sets)
        expected_sets = {
            'https://primary.com': 
            FpsSet(
                    primary="https://primary.com", 
                    associated_sites=None,
                    service_sites=["https://service1.com"],
                    ccTLDs=None
                    )
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, ["The service site " +
        "https://service1.com has a robots.txt file, but " +
        "does not have X-Robots-Tag in its header"])
    @mock.patch('requests.get', side_effect=mock_get)
    def test_robots_wrong_tag(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service2.com"]
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                     etlds=None,
                     icanns=set())
        loaded_sets = fp.load_sets()
        fp.find_robots_txt(loaded_sets)
        expected_sets = {
            'https://primary.com': 
            FpsSet(
                    primary="https://primary.com", 
                    associated_sites=None,
                    service_sites=["https://service2.com"],
                    ccTLDs=None
                    )
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, ["The service site " +
        "https://service2.com has a robots.txt file, but " +
        "does not have a no-index tag in its header"])
    @mock.patch('requests.get', side_effect=mock_get)
    def test_robots_expected_tag(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service3.com"]
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                     etlds=None,
                     icanns=set())
        loaded_sets = fp.load_sets()
        fp.find_robots_txt(loaded_sets)
        expected_sets = {
            'https://primary.com': 
            FpsSet(
                    primary="https://primary.com", 
                    associated_sites=None,
                    service_sites=["https://service3.com"],
                    ccTLDs=None
                    )
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, [])

    @mock.patch('requests.get', side_effect=mock_get)
    def test_robots_wrong_tag(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service4.com"]
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                     etlds=None,
                     icanns=set())
        loaded_sets = fp.load_sets()
        fp.find_robots_txt(loaded_sets)
        expected_sets = {
            'https://primary.com': 
            FpsSet(
                    primary="https://primary.com", 
                    associated_sites=None,
                    service_sites=["https://service4.com"],
                    ccTLDs=None
                    )
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, [])
    # We run a similar set of mock tests for ads.txt
    @mock.patch('requests.get', side_effect=mock_get)
    def test_ads(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service1.com"]
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                     etlds=None,
                     icanns=set())
        loaded_sets = fp.load_sets()
        fp.find_ads_txt(loaded_sets)
        expected_sets = {
            'https://primary.com': 
            FpsSet(
                    primary="https://primary.com", 
                    associated_sites=None,
                    service_sites=["https://service1.com"],
                    ccTLDs=None
                    )
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, ["The service site " +
        "https://service1.com has an ads.txt file, this " +
        "violates the policies for service sites"])
    @mock.patch('requests.get', side_effect=mock_get)
    def test_ads(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service5.com"]
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                     etlds=None,
                     icanns=set())
        loaded_sets = fp.load_sets()
        fp.find_ads_txt(loaded_sets)
        expected_sets = {
            'https://primary.com': 
            FpsSet(
                    primary="https://primary.com", 
                    associated_sites=None,
                    service_sites=["https://service5.com"],
                    ccTLDs=None
                    )
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, [])
    # We run a similar set of mock tests for redirect check
    @mock.patch('requests.get', side_effect=mock_get)
    def test_non_redirect(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service1.com"]
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                     etlds=None,
                     icanns=set())
        loaded_sets = fp.load_sets()
        fp.check_for_service_redirect(loaded_sets)
        expected_sets = {
            'https://primary.com': 
            FpsSet(
                    primary="https://primary.com", 
                    associated_sites=None,
                    service_sites=["https://service1.com"],
                    ccTLDs=None
                    )
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, ["The service site " +
        "must not be an endpoint: https://service1.com"])
    @mock.patch('requests.get', side_effect=mock_get)
    def test_proper_redirect(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://service6.com"]
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                     etlds=None,
                     icanns=set())
        loaded_sets = fp.load_sets()
        fp.check_for_service_redirect(loaded_sets)
        expected_sets = {
            'https://primary.com': 
            FpsSet(
                    primary="https://primary.com", 
                    associated_sites=None,
                    service_sites=["https://service6.com"],
                    ccTLDs=None
                    )
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, [])
    @mock.patch('requests.get', side_effect=mock_get)
    def test_404_redirect(self, mock_get):
        # Assert requests.get calls
        json_dict = {
            "sets":
            [
                {
                    "primary": "https://primary.com",
                    "serviceSites": ["https://no-such-service.com"]
                }
            ]
        }
        fp = FpsCheck(fps_sites=json_dict,
                     etlds=None,
                     icanns=set())
        loaded_sets = fp.load_sets()
        fp.check_for_service_redirect(loaded_sets)
        expected_sets = {
            'https://primary.com': 
            FpsSet(
                    primary="https://primary.com", 
                    associated_sites=None,
                    service_sites=["https://no-such-service.com"],
                    ccTLDs=None
                    )
        }
        self.assertEqual(loaded_sets, expected_sets)
        self.assertEqual(fp.error_list, [])

if __name__ == '__main__':
    unittest.main()

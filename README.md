# **Related Website Sets**
For full instructions and guidance on how to submit a set, please read the [Related Website Sets Submission Guidelines](https://github.com/GoogleChrome/first-party-sets/blob/main/RWS-Submission_Guidelines.md).

For clarity on the Related Website Sets proposal being incubated in WICG, please 
read the [Related Website Sets explainer](https://github.com/WICG/first-party-sets/).

The following is a description of the contents of this repository:


* Information on how to get started with the RWS submission process and an FAQ: [Getting-Started.md](https://github.com/GoogleChrome/related-website-sets/blob/main/Getting-Started.md)
* Guidance on submitting Related Website Sets: [RWS-Submission_Guidelines.md](https://github.com/GoogleChrome/first-party-sets/blob/main/RWS-Submission_Guidelines.md)
* A JSON document of Related Website Sets: [related_website_sets.JSON](https://github.com/GoogleChrome/first-party-sets/blob/main/related_website_sets.JSON)
* Various submission checks visible in [RwsCheck.py](https://github.com/GoogleChrome/first-party-sets/blob/main/RwsCheck.py)
    * [RwsSet.py](https://github.com/GoogleChrome/first-party-sets/blob/main/RwsSet.py) 
    defines an object type used by [RwsCheck.py](https://github.com/GoogleChrome/first-party-sets/blob/main/RwsCheck.py)
    * [Check_sites.py](https://github.com/GoogleChrome/first-party-sets/blob/main/check_sites.py) 
    calls several submission checks visible in 
    [RwsCheck.py](https://github.com/GoogleChrome/first-party-sets/blob/main/RwsCheck.py)
    * [tests/rws_tests.py](https://github.com/GoogleChrome/first-party-sets/blob/main/tests/rws_tests.py) 
    includes examples of failing set submissions and which checks 
    they will fail
* Reference files like 
[effective_tld_names.dat](https://github.com/GoogleChrome/first-party-sets/blob/main/effective_tld_names.dat) 
and [ICANN_domains](https://github.com/GoogleChrome/first-party-sets/blob/main/ICANN_domains)

# **First-Party Sets**
For full instructions and guidance on how to submit a set, please read the [First-Party Sets Submission Guidelines](https://github.com/GoogleChrome/first-party-sets/blob/main/FPS-Submission_Guidelines.md).

For clarity on the First-Party Sets proposal being incubated in WICG, please 
read the [First-Party Sets explainer](https://github.com/WICG/first-party-sets/).

The following is a description of the contents of this repository:



* Guidance on submitting First-Party Sets: [FPS-Submission_Guidelines.md](https://github.com/GoogleChrome/first-party-sets/blob/main/FPS-Submission_Guidelines.md)
* A JSON document of First-Party Sets: [first_party_sets.JSON](https://github.com/GoogleChrome/first-party-sets/blob/main/first_party_sets.JSON)
* Various submission checks visible in [FpsCheck.py](https://github.com/GoogleChrome/first-party-sets/blob/main/FpsCheck.py)
    * [FpsSet.py](https://github.com/GoogleChrome/first-party-sets/blob/main/FpsSet.py) 
    defines an object type used by [FpsCheck.py](https://github.com/GoogleChrome/first-party-sets/blob/main/FpsCheck.py)
    * [Check_sites.py](https://github.com/GoogleChrome/first-party-sets/blob/main/check_sites.py) 
    calls a number of submission checks visible in 
    [FpsCheck.py](https://github.com/GoogleChrome/first-party-sets/blob/main/FpsCheck.py)
    * [tests/fps_tests.py](https://github.com/GoogleChrome/first-party-sets/blob/main/tests/fps_tests.py) 
    includes examples of failing set submissions and which checks 
    they will fail
* Reference files like 
[effective_tld_names.dat](https://github.com/GoogleChrome/first-party-sets/blob/main/effective_tld_names.dat) 
and [ICANN_domains](https://github.com/GoogleChrome/first-party-sets/blob/main/ICANN_domains)
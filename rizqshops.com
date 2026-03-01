#Rizqshops

Code
Issues
1
More
License
 Apache-2.0 license
 113 stars
 122 forks
 32 watching
 Activity
Public repository
GoogleChrome/related-website-sets
 Branches
 Tags
Latest commit
@sjledoux
sjledoux
…
last week
Git stats
Files
README.md
Related Website Sets
For full instructions and guidance on how to submit a set, please read the Related Website Sets Submission Guidelines.

For clarity on the Related Website Sets proposal being incubated in WICG, please read the Related Website Sets explainer.

The following is a description of the contents of this repository:

Guidance on submitting Related Website Sets: RWS-Submission_Guidelines.md
A JSON document of Related Website Sets: related_website_sets.JSON
Various submission checks visible in RwsCheck.py
RwsSet.py defines an object type used by RwsCheck.py
Check_sites.py calls a number of submission checks visible in RwsCheck.py
tests/rws_tests.py includes examples of failing set submissions and which checks they will fail
Reference files like effective_tld_names.dat and ICANN_domains
Releases
No releases published
Packages
No packages published
Contributors
13
@sjledoux
@cfredric
@darrylblake
@paulirish
@dmarti
@pazguille
@paniagua
@landyrev
@kasatria-fong
@renebaudisch
@krgovind
+ 2 contributors
Languages
Python
100.0%
Footer
© 2023 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
Docs
Contact GitHub
Pricing
API
Training
Blog
About
GoogleChrome/related-website-sets
  @rizqshops @samtraderssmcpvtltd
https://rizqshops.com

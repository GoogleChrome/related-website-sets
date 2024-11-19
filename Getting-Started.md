# Related Website Sets (RWS) Submission Quick-Start Guide and FAQs 
The purpose of this document is to provide a companion guide to the [Related Website Sets Submission Guidelines](https://github.com/GoogleChrome/related-website-sets/blob/main/RWS-Submission_Guidelines.md), which details the full requirements for Related Website Sets creation and submission.

Pre-steps
=========

1.  A [GitHub account](https://docs.github.com/en/get-started/learning-about-github/types-of-github-accounts) is required to make a set submission, since sets are submitted by creating a [pull request (PR)](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request).

2.  Submitters must sign a [Contributor's License Agreement (CLA)](https://cla.developers.google.com/about/google-corporate) to contribute to the GoogleChrome repo where the Related Website Sets (RWS) list lives. If you haven't signed it yet, you will be prompted to sign after you submit your PR.

RWS Submission
==============

Step 1: Identifying your RWS
----------------------------

1.  Identify which domains you want to declare in your RWS, and decide on the set primary and set members. Set members have a defined relationship with the set primary. Make sure your set members meet the relationship requirements under "[Set Formation Requirements](https://github.com/GoogleChrome/related-website-sets/blob/main/RWS-Submission_Guidelines.md#set-formation-requirements)."

Step 2: Creating (or updating) your RWS submission
--------------------------------------------------

1.  Create a local copy of the [GitHub repository](https://github.com/GoogleChrome/first-party-sets) on your machine. You may choose to [clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) or [fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) the repository.

2.  Create a new branch by using the command `git checkout -b your-branch-name -t origin/main` or [via the UI](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-and-deleting-branches-within-your-repository).

3.  Create your JSON resources in the correct [format](https://github.com/GoogleChrome/related-website-sets/blob/main/RWS-Submission_Guidelines.md#set-submissions). You can use the [RWS JSON Generator tool](https://goo.gle/rws-json-generator) to easily do this.

4.  Make changes to the [related_website_sets.JSON file](https://github.com/GoogleChrome/related-website-sets/blob/main/related_website_sets.JSON) to reflect your new or modified RWS.

1.  Ensure you add your submission inside the `"sets": []` list (preferably at the end of the list).

Step 3: Ensuring your RWS meets the technical requirements
----------------------------------------------------------

1.  Ensure that all domains in your set meet the [Set-level technical validation checks](https://github.com/GoogleChrome/first-party-sets/blob/main/RWS-Submission_Guidelines.md#set-level-technical-validation). This includes, but is not limited to, checks that look for the https:// scheme and /.well-known metadata requirement.

2.  Ensure that member domains in your set meet the [Subset-level technical validation checks](https://github.com/GoogleChrome/first-party-sets/blob/main/RWS-Submission_Guidelines.md#subset-level-technical-validation). This includes, but is not limited to, the X-Robots-Tag requirement for service domains.

Step 4: Testing your RWS locally
--------------------------------

Once you've made your changes to your local branch, you can open a terminal and run the command 

`python3 check_sites.py --primaries=https://yourprimary.example`

or, equivalently, run

`python3 check_sites.py -p https://yourprimary.example`

You will get the results of any failed tests in the terminal. Otherwise, you will see "success" if your changes are passing all of the checks. Make sure that the text of the primary site you're passing into the command line is identical to the primary site you have listed in the related_website_sets.JSON file, or the tests will fail. If you would like to test multiple Related Website Sets at once, you can run the command above with multiple primaries in a comma separated list. 

For example, to get the results of the checks for a set with `https://foo.example` as its primary, you would run

`python3 check_sites.py --primaries=https://foo.example`

or equivalently

`python3 check_sites.py -p https://foo.example`


To get the results for both the set with `https://foo.example` as its primary, and for the set with `https://bar.example` as its primary, you would run

`python3 check_sites.py --primaries=https://foo.example,https://bar.example`

or

`python3 check_sites.py -p https://foo.example -p https://bar.example`

Step 5: Submitting your RWS
---------------------------

Once you've confirmed that your set is passing checks in your local branch, you can create a pull request (PR).

1.  [Push](https://docs.github.com/en/get-started/using-git/pushing-commits-to-a-remote-repository) your local changes to your remote branch by using the command `git push origin your-branch-name`.

1.  [Create a PR](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) to pull your branch into the master.

1.  You may need to resolve merge conflicts.

1.  Wait for all actions to finish running to confirm whether your PR has passed or failed the checks. 

1.  Sometimes, especially if you had merge conflicts that you had to squash, a checkmark will appear before the action has actually run.

1.  Check the "Actions" tab to confirm the status of the run triggered by your request.

1.  If you want your PR to be merged in a timely manner, please [enable repository maintainer permissions on your pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/allowing-changes-to-a-pull-request-branch-created-from-a-fork#enabling-repository-maintainer-permissions-on-existing-pull-requests).
This allows the maintainers of the RWS repository to resolve merge conflicts on your behalf. Without this permission, the maintainers must wait for **you** to resolve any conflicts before they can merge your PR, even if it is otherwise passing the checks. This will delay your submission; maintainers will not revisit your PR until the next regular review.

Per the Submission Guidelines, approved PRs will be manually merged in batches to the canonical RWS list once per week (Tuesdays at 12pm Eastern Time).

### Debugging failures

-   If your PR fails, an error message will provide additional information on why the submission may have failed. Here is an [example](https://github.com/GoogleChrome/first-party-sets/pull/26#issuecomment-1533661609).

-   You can also investigate the details of the failure by clicking on "PR-Actions" then clicking the drop-down labeled "File contents."

-   If your PR is failing because of changes you made to related_website_sets.JSON, you can fix those issues in your local copy of the repository, push them to your branch as previously described, and the action will run again once you've finished. The comment should update with any changes to the error message or it will change to say that you've passed all of the tests.

-   If your PR is failing validation and has been not updated after 30 days, you will be reminded with a comment to take action. Failing any action taken within 14 days of the reminder, the PR will be closed. Once the PR is closed, you will need to submit a new PR to restart the submission process.

FAQs
====

### Q. How can I sign the CLA?

Answer: 

You can visit [Google's page about the Contributor License Agreement](https://cla.developers.google.com/about/google-individual) to sign the CLA, or check if you already have a CLA on file.

### Q. What is the /.well-known/ file?

Answer: 

The /.well-known/ directory is commonly used by different services to fetch different metadata relating to a domain. In the case of RWS submission checks, we will be checking that your domains are all hosting a file at /.well-known/related-website-sets.json in order to prove ownership of the domain.

### Q. Can I change the set primary domain?

Answer: Yes, technically, you can change the set primary domain. However, when you change the set primary domain, Chrome's implementation will register this change as a set change, and clear site data for all the sites in this set, even if the new primary used to be a member in this set.

### Q. What should I put in the rationale field?

Answer: The rationale field is where you provide an explanation as to why or how the domain you've added meets the use case the subset is designed for. For service domains, you must provide an explanation of how each domain in this subset supports functionality or security needs. For associated domains, you must provide an explanation of how you clearly present the affiliation across domains to users and why users would expect your domains to be affiliated (e.g., an About page, header or footer, shared branding or logo, etc).

### Q. Since anyone can contribute to the RWS list, can someone else modify or delete my RWS?

Answer: A key component to the technical checks that run upon submission is the [/.well-known/ metadata requirement](https://github.com/GoogleChrome/first-party-sets/blob/main/RWS-Submission_Guidelines.md#set-level-technical-validation). This requirement demonstrates that the submitter has administrative access to the domains present in the set, since administrative access is required to modify the /.well-known/ file. This will help prevent unauthorized actors from adding domains to a set.

### Q. What if I would like to modify or delete my RWS?

Answer: 
To modify an RWS that you own, simply submit a Pull Request that makes the changes you wish to make to your set, and ensure that the `/.well-known/related-website-set.json` endpoint for your set's primary reflects these changes, as do the `/.well-known/related-website-set.json` endpoints of any sites changed within your subsets. To remove a set entirely from the [canonical RWS list](https://github.com/googlechrome/first-party-sets/blob/main/related_website_sets.JSON) you must change the `/.well-known/related-website-set.json` endpoint for your set's primary so that it serves a `404 (Not Found)` status code, then submit a pull request that removes your RWS set from the list.

### Q. Can I make pull requests against files other than related_website_sets.JSON (e.g., the Submission Guidelines or the technical checks)?

Answer: Please refrain from making suggestions in the form of pull requests to files in the GitHub repository other than related_website_sets.JSON. We welcome feedback to any of the content, but would prefer feedback to be submitted as issues to the repository instead.The purpose of this document is to provide a companion guide to the [Related Website Sets Submission Guidelines](https://github.com/GoogleChrome/related-website-sets/blob/main/RWS-Submission_Guidelines.md), which details the full requirements for Related Website Sets creation and submission.

### Q. What should I do if my PR fails validation?

Answer: If your PR fails, an error message will provide additional information on why the submission may have failed. Here is an [example](https://github.com/GoogleChrome/related-website-sets/pull/26#issuecomment-1533661609). If the PR that fails validation is not updated after 30 days, you will be reminded with a comment to take action. Failing any action taken within 14 days of the reminder, the PR will be closed. Once the PR is closed, you can either create a new PR to restart the process, or click the button at the bottom of your old PR marked "Reopen pull request."
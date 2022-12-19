# **Getting Started**

Please read the [First-Party Sets Submission Guidelines](https://github.com/GoogleChrome/first-party-sets/blob/main/FPS-Submission_Guidelines.md) 
for full instructions and guidance on how to submit a set. 

The following summary is provided as general guidance:

Changes are made by creating a Pull Request (PR) from your branch to the main 
branch. When this occurs, a Github Action will trigger, visible in 
[.github/workflows/fps-submissions-checks.yml](https://github.com/GoogleChrome/first-party-sets/blob/main/.github/workflows/fps-submissions-checks.yml)
. This action will run [check_sites.py](https://github.com/GoogleChrome/first-party-sets/blob/main/check_sites.py)
, which calls a number of submission checks visible in 
[FpsCheck.py](https://github.com/GoogleChrome/first-party-sets/blob/main/FpsCheck.py)
. Once it has run its action, you can see any errors in the actions tab of the 
repository. Running the command 'python3 check_sites.py' locally will also 
show you if you have any errors in your update before you create the PR. 
Please try to do this first so that it will be easier to update the repository 
and accept PRs. A step by step guide to running the project is provided below 
to avoid confusion.


## **Running this project**

In order to run/test these checks, you will have to:



1. Checkout a new branch.
2. Make changes to the first_party_sets.JSON, these should be in the format 
dictated by the schema in First Party Sets Submissions Guideline.
3. Push your remote.
4. Create a pull request to pull your branch into master, then resolve any 
merge conflicts that may be present.
5. Wait for the action to finish running. This should be visible both on the 
page for your PR, and on the "Actions" tab.
6. If it succeeds, there should be a check mark. On failure, there will be a 
red "x." Make sure you wait for the action to finish! Sometimes, especially if 
you had merge conflicts that you had to squash, a checkmark will appear before 
the action has actually run. To be absolutely certain, always check the 
actions tab to see the status of the run triggered by your request.
7. The details of the failure will be visible by clicking on "PR-Actions'' and 
then clicking the drop down labeled "File contents." The details will also be 
visible in results.txt.
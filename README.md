# first-party-sets
This repo stores a json document of First-Party Sets (FPSes) within the file 
"first_party_sets.JSON". For clarity on the First-Party Sets proposal,
please read the information on 
[this page](https://github.com/WICG/first-party-sets/). For guidance on submitting sets,
please follow the guidelines provided 
here <b>...insert link to submission guideline once it is public...</b> 
In general, changes are made by creating a Pull Request (PR) from your branch 
to the main branch. When this occurs, a Github Action will trigger, visible in 
.github/workflows/fps-submission-checks.yml. This action will run 
check_sites.py, which calls a number of submission checks visible in 
FpsCheck.py. Once it has run its action, you can see any errors in the actions
tab of the repo. Running FpsCheck locally will also show you if you have any 
errors in your update before you create the PR. Please try to do this first
so that it will be easier to update the repo and accept PRs. A step by step 
guide to running the project is provided below to avoid confusion. 

If you have suggestions or any cases that are failing that you
believe should be passing, please feel free to comment on the PR or add issues to the issues tab
of this repo. 

## Running this project
In order to run/test these checks, you will have to:
<ol>
<li> Checkout a new branch.
<li> Make changes to the first_party_sets.JSON, these should be in the format 
dictated by the schema in First Party Sets Submissions Guideline.
<li> Push your remote.
<li> Create a pull request to pull your branch into master, then resolve any 
merge conflicts that may be present.
<li> Wait for the action to finish running. This should be visible both on the 
page for your PR, and on the "Actions" tab.
<li> If it succeeds, there should be a check mark. On failure, there will a red
 "x." <b>Make sure you wait for the action to finish!</b> 
 Sometimes, especially if you had merge conflicts that you had to squash, a 
 checkmark will appear before the action has actually run. To be absolutely 
 certain, always check the actions tab to see the status of the run triggered 
 by your request. 
<li> The details of the failure will be visible by clicking on 
"PR-Actions" and then clicking the drop down labeled "File contents."
The details will also be visibile in results.txt.
</ol>

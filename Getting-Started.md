# **Getting Started**

Please read the [First-Party Sets Submission Guidelines](https://github.com/GoogleChrome/first-party-sets/blob/main/FPS-Submission_Guidelines.md) 
for full instructions and guidance on how to submit a set. This Getting Started guide will provide general guidance on navigating this repo.

Changes are made by creating a Pull Request (PR) from your branch to the main 
branch. When this occurs, a Github Action will trigger, visible in 
[.github/workflows/fps-submissions-checks.yml](https://github.com/GoogleChrome/first-party-sets/blob/main/.github/workflows/fps-submissions-checks.yml)
. This action will run [check_sites.py](https://github.com/GoogleChrome/first-party-sets/blob/main/check_sites.py)
, which calls a number of submission checks visible in 
[FpsCheck.py](https://github.com/GoogleChrome/first-party-sets/blob/main/FpsCheck.py)
. Once it has run its action, you can see any errors in the "Actions" tab of the 
repository.

<b>Note:</b> All contributors to the GoogleChrome repo will need to sign a [Contributor's License Agreement](https://cla.developers.google.com/about/google-corporate).

# Creating your Submission #
To create or revise a submission, you will first need to create a local copy of the repo. To do this, follow [this GitHub guide on cloning a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository). Once you've you cloned the repo, you can create a new branch by using the call "git checkout -b your-branch-name -t origin/main". When making your changes to  first_party_sets.JSON, follow the <a href = "https://github.com/GoogleChrome/first-party-sets/blob/main/FPS-Submission_Guidelines.md#set-submissions">schema in the Submission Guidelines.</a>

# Testing your Submission Locally #

Once you've made your changes to your local branch, you can open a terminal and run the command "python3 check_sites.py". 
When this command has finished you will either see "success" meaning your submission passed all of the checks, or you will see a 
list of failed checks. 


# Creating your Pull Request #
Once you're satisfied with your changes and they are passing the checks locally, you can prepare to create a Pull Request (PR). You can push your local changes to your remote branch, and then create a PR to pull your branch into master. Once you have done this you may need to resolve any merge conflicts. When this is done, wait for the actions to finish running, which will tell you whether your PR has passed or failed the checks.
 
 # Debugging Failures #

If all checks succeed, there should be a check mark. On failure, there will be a 
red "x." Make sure you wait for the action to finish! Sometimes, especially if 
you had merge conflicts that you had to squash, a checkmark will appear before 
the action has actually run. To be absolutely certain, always check the 
"Actions" tab to see the status of the run triggered by your request.
The details of the failure will be visible by clicking on "PR-Actions" and 
then clicking the drop down labeled "File contents." 

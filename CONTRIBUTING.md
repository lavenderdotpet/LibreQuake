# How to Contribute to the LibreQuake Project

## Background

Previously we have had a very much archaic and unstandardized approach to how we accept contributions to the LibreQuake project. This has had quite a few problems as a result, some examples being:

* A "dirty" git log, making tracking regressions or general progress difficult
* Lack of quality control (Does this change actually work? Does the project still build? Are the contribution detais easy to read and understand?)
* Overly or underly verbose commit messages

These problems became more exacerbated as more eyes and contributors have appeared. As a result, this contribution guide has been drafted to hopefully address all of these problems and make for a cleaner and easier to work on project.

## Branches

Please do not generalize branches. Use branches for specific features or concepts.

If you are a Collaborator (meaning, if you are added to the LibreQuake repository and have administrative control) it is required that your branch naming scheme is as follows:

`{username}/{change-subject}`

Shorthand is allowed for `username`. For instance, if your GitHub username is `lavenderdotpet`, using `lav` would be appropriate. However, these must be easily connected to your GitHub username to track who owns a branch.

The `change-subject` field should be a **very** brief issue or feature or similar concept. 

An example branch name that fits this standard would be `cypress/quakec-stringopts` for a branch owned by CypressImplex that makes QuakeC related string optimizations.

External contributors (non-Collaborators) are not expected to follow this name convention, but should still refrain from using generalized branch names.

## Commits

In general, this guide is a must-read when writing good commit messages to begin with: https://cbea.ms/git-commit/

Additionally, as this reporistory contains multiple diverse components, we ask that you prefix your commit message pertaining to the component you are modifying. Here are acceptable prefixes to use:

* `BUILD`: Modification of our build scripts and/or tools.
* `CI`: Modification of the GitHub Actions Pipeline(s).
* `GFX`: Modification of **game** (not map) textures.
* `GH`: Modifiation of any repository-related elements (screenshots, readme, etc.)
* `MAPS`: Modification of `.map` files.
* `MODELS`: Modification of models, both `.blend` and exported `.mdl`
* `QC`: Modification of QuakeC source code.
* `AUDIO`: Modification of game sound effects or music.
* `WADS`: Modification of **map** textures, to be packed into a `.wad` during the build process.

Here is a good example for a commit subject line:

`GFX: Fix colormap having incorrect fullbright count`

**You must always provide more context for your changes via the commit message body.**

If your commit addresses an open issue, be sure to include the issue in the commit message body.

If you are committing on behalf of someone, please use the [Co-Author feature](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors) if they other author has a GitHub profile. If they do not, please credit them in the commit body at the very bottom of the message as to keep the flow of the commit organized. You may use any source platform of their choice to refer to them as long as it complies with GitHub's Terms of Service.

## Pull Requests

Please keep Pull Requests on-topic. The Pull Request title should follow the same naming convention as your commit messages for clarity.

It is required that you provide both a detailed desctription of your changes as well as visualization of your changes being functional in-game. The Pull Request template will guide you through this.

Be mindful that Pull Requests are scrutinized and reviewed carefully to mitigate any potential problems a Collaborator may discover. It is important for us to verify and test your changes independently as well. We will leave reviews and mark appropriately when we request changes and are happy to turn the request into a discussion.

Please do not have discussions about a Pull Request off-platform. We should preserve the history of the conversation in an easily accessible matter so that justifications can be tracked in the event of an overturning discussion.

When having discussions, please be mindful to use proper grammar and full sentences in the English language. We should be accessible to people who are English-Second-Language, and a big part of that is refraining from using acronyms or shorthand/slang.

If you are a Collaborator looking to merge a Pull Request, or are just curious about merge prerequisites, we will merge a Pull Request given the following are true:

* It has received 2 or more approvals.
* The Pull Request template has been followed.
* Commits follow our convention standards.
* If the user is a collaborator, the Branch name convention standards have been followed.
* Our CI passes without failure.
* 48 hours or more have passed since the PR has been marked ready for review.

If the change fixes a critical issue (such as a crash, broken animaton, etc.) an exception should be made for the 48 hour rule, **however all other prerequisites must be met!**
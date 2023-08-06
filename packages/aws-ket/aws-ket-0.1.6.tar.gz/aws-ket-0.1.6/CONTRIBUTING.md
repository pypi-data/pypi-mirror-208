# Contributing Code to AWS KET

Thank you for your interest in contributig to AWS KET. 

## Guidelines

When submitting or commenting on an Issue, please respect the following guidelines. Github Issues are AWS KET project record of bugs and feature development, e.g. for publishing a release's Changelog, and as such it is important to keep them informative and on-topic.

-   Be respectful and civil!
-   Use the provided Issue templates to report a bug or request a feature
-   If you have a question please use [discussion](https://github.com/sayefiqb/aws-ket/discussions)
    instead.

Before starting to contribute make sure you have the following:

-   `Python 3.9` or greater version installed on your machine
-   Install all depedencies using `make develop`
-   Run `make test` to ensure it is working on your local machine from the start

When submitting Pull Request (PR), please respect the following coding
guidelines:

-   Please make sure PRs include:

    -   Tests asserting behavior of any new or modified features.
    -   Docs for any new or modified functionalities.

-   Ensure the application works and functiomns as expected locally

-   Keep PRs clean, simple and to-the-point:
    -   Squash all your commits
    -   No merge commits (`git merge main`), prefer `rebase` to resolve
        conflicts with the `main` branch.
    -   Try to organize commits as functional components (as opposed to
        timeline-of-development)
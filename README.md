# Few notes:


## Code

- I used codefly to create all the boilerplate for python and Next.
- I used Claude Sonnet to do all the indexing definitions and the UI.
- some aspect of the SDK are broken now (current refactor) -- which is why I hardcoded a few values in the code.

What it looks like to run:

https://asciinema.org/a/Q5Hxtn5BHon2rx5QKCYHJpA4R

(I need to publish the recent CLI and agents so won't work for you yet)

## Tech

- I used Opensearch (agent in codefly I wrote for it) to do the search.
- I didn't dig too much into the question: "NSCLC trials -AND- immunotherapy related drugs" because I didn't have time to do so. But I worked a bit with Opensearch and it's incredibly powerful.
- For deployment, using codefly makes it easy to deploy to Kubernetes (having a bit of issues with the current refactor, but it's a work in progress).

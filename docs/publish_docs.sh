#!/bin/bash

# Source script from Hugo: https://gohugo.io/hosting-and-deployment/hosting-on-github/#put-it-into-a-script-1
DOCS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PUBLISH_DIR="${DOCS_DIR}/_build/html"
REPO_DIR=$(git rev-parse --show-toplevel)

if [ "`git status -s`" ]
then
    echo "The working directory is dirty. Please commit any pending changes."
    exit 1;
fi

echo "Deleting old content"
cd ${DOCS_DIR}
poetry run make clean
git worktree prune
cd ${REPO_DIR}
rm -rf .git/worktrees/html/

echo "Checking out gh-pages branch into ${PUBLISH_DIR}l"
git worktree add -B gh-pages ${PUBLISH_DIR} origin/gh-pages

echo "Generating site"
cd ${DOCS_DIR} && poetry run make html && touch ${PUBLISH_DIR}/.nojekyll

echo "Updating gh-pages branch"
cd ${PUBLISH_DIR} && git add --all && git commit -m "docs: updated repo documentation" --no-verify

echo "Pushing to github"
cd ${PUBLISH_DIR} && git push

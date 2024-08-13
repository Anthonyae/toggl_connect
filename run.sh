#!/bin/bash

set -e

# this mkes the directory equal to where the script is located
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)"
TEST_COVERAGE_MIN=80

function install {
    python -m pip install --upgrade pip
    python -m pip install --editable "$THIS_DIR/[dev]"
}

function lint {
    pre-commit run --all-files
}

function lint:ci {
    # We skip no-commit-to-branch since that blocks commits to `main`.
    # All merged PRs are commits to `main` so this must be disabled.
    # shellcheck disable=SC2317
    SKIP=no-commit-to-branch pre-commit run --all-files
}

function tests {
        PYTEST_EXIT_STATUS=0
        python -m pytest ${@:-"$THIS_DIR/tests/"} \
            --cov="${COVERAGE_DIR:-$THIS_DIR/src}" \
            --cov-report html \
            --cov-report term \
            --cov-report xml \
            --junit-xml "$THIS_DIR/test-reports/report.xml" \
            --cov-fail-under=${TEST_COVERAGE_MIN} || ((PYTEST_EXIT_STATUS+=$?))
        mv coverage.xml "$THIS_DIR/test-reports/" || true
        rm -rf "$THIS_DIR/test-reports/htmlcov" || true
        mv -f htmlcov "$THIS_DIR/test-reports/" || true
        mv .coverage "$THIS_DIR/test-reports/" || true
        return $PYTEST_EXIT_STATUS
}

function test:serve {
    python -m http.server -d  ./test-reports/htmlcov
}

function build {
    python -m build --sdist --wheel "$THIS_DIR/"
}

function try-load-dotenv {
    [ -f "${THIS_DIR}/.env" ] || (echo "no .env file found" && return 1)
    while IFS='=' read -r key value; do
        # Ignore empty lines and lines starting with #
        if [[ -n "$key" && "$key" != \#* ]]; then
            export "$key=$value"
        fi
    done < <(grep -v '^#' "$THIS_DIR/.env" | grep -v '^$')
}

function lint:ci {
    SKIP=no-commit-to-branch pre-commit run --all-files
}

function release:test {
    create_env_example
    lint
    clean
    tests
    build
    publish:test
}

function release:prod {
    release:test
    publish:prod
}

function publish:test {
    try-load-dotenv || true
    twine upload dist/* \
    --repository testpypi \
    --username=__token__ \
    --password="$TEST_PYPI_TOKEN"
}

function publish:prod {
    try-load-dotenv || true
    twine upload dist/* \
    --repository pypi \
    --username=__token__ \
    --password="$PROD_PYPI_TOKEN"
}

function clean {
    rm -rf dist build
    find . \
       -type d \
       \( \
       -name "*cache*" \
       -o -name "*.dist-info" \
       -o -name "*.egg-info" \
       -o -name "*htmlcov" \
       -o -name "test-reports" \
       \) \
       -not -path "./venv/*" \
       -not -path "./.venv/*" \
       -not -path "./.env/*" \
       -not -path "./env/*" \
       -exec rm -r {} +
}

function start {
    echo "start not implemented"
}

function default {
    # Default task to execute
    start
}

function help {
    echo "$0 <task> <args>"
    echo "Tasks:"
    compgen -A function | cat -n
}

function create_env_example {
    # Copy the .env file to .env.example
    cp .env .env.example
    # remove sensitive info
    sed -i 's/=.*/=/' .env.example
    # add header note
    sed -i '1s/^/# generated automatically by .git\/hooks\/pre-commit\n/' .env.example
    sed -i '1s/^/# shellcheck disable=all\n/' .env.example

    # Remove lines containing the string "pypi"
    sed -i '/pypi/I d' .env.example

    # Add a line to .gitignore to ignore the real .env file
    if ! grep -q "^\.env$" .gitignore; then
    echo ".env" >> .gitignore
    fi

    # Stage the .env.example file
    git add .env.example
}

TIMEFORMAT="Task completed in %3lR"
# shellcheck disable=SC2068
time ${@:-help}

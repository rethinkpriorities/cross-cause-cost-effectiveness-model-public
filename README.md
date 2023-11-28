# Cross-Cause Cost-Effectiveness Model

## Overview

The project is contained in three repos:

1. `ccm`: The core model.

The Cross-Cause Cost-Effectiveness Model is a Python program that provides functions for computing distributions of outcome effectiveness under several models of intervention efficacy -- notably, existential risk and animal welfare.

2. `ccm_api`: The web server.

The project includes a web app for visualizing these distributions. The functions of `ccm` are served through an openapi framework built in `ccm_api`.

3. `ccm_react`: The front-end web app. This talks with the `ccm_api` server and displays results in html.

## Setup

### Requirements

You should have:

  * [Python 3.10](https://www.python.org/downloads/)
  * [Poetry](https://python-poetry.org/docs/#installation)
  * node 18
  * npm

### Setup Virtual Environment

From the top-level project directory, run:

- `poetry install`
- `cd ccm_react; npm install`

You don't need to re-run these commands unless the project dependencies change.

### Activate Virtual Environment

Running `poetry shell` will spawn a new shell within the virtual environment. You can run `exit` to exit the virtual environment.
You can also configure your editor to use this virtual environment. You can find the relevant path by running `poetry env info -p`.

## Running the API

- To start the API server, run `uvicorn ccm_api.main:app --reload` or `npm run uv` from the top-level directory.
- To see the API documentation, navigate to `http://localhost:8000/docs` in your browser.

## Running the web UI

> **Note**
> Web functionality requires the API being running locally.

- Install the dependencies by running `npm install` in the `ccm_react` directory.
- Run `npm run dev` to start the development server.
- Navigate to `http://localhost:5173/`.
- To see the UnoCSS inspector, navigate to `http://localhost:5173/__unocss/` in your browser.

## Regenerating Client

- The react app automatically configures some utilities to the structures returned by the webserver.
   After making changes to the API, you need to regenerate the client in `ccm_react`: 
  - Start up the API. If it was already running, top it and restart it.
  - While the API is running, from `ccm_react`, run `npm run generate-client`.

## Running tests

- To run all Python tests: `pytest`
  - Add `-s` argument to run all tests verbosely showing all stdout
  - Add `-m "not slow"` to skip slow tests
- You can also run individual test cases by providing the name: `pytest tests/test_population.py::test_get_life_years_affected`
- To run JavaScript tests: `npm run test` from the `ccm_react` directory
- To run Cypress E2E tests:  `npm run test-cypress` from the `ccm_react` directory

## Typechecking, formatting, and linting

- To validate Python code, run `ruff check .` and `pyright`.
- To format Python code, run `black`.
- To format JavaScript code, `cd ccm_react` and run `npm run format`.
- To validate JavaScript code, `cd ccm_react` and run `npm run lint`.

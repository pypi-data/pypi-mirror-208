# tap-totango

`tap-totango` is a Singer tap for the [Totango API](https://support.totango.com/hc/en-us/sections/360005893212-Totango-API). It extracts data from the Search API accounts, users, and events endpoints.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

Install from PyPi:

```bash
pipx install tap-totango
```

Install from BitBucket:

```bash
pipx install git+https://bitbucket.org/indiciumtech/tap-totango.git@main
```

## Configuration

### Accepted Config Options

A full list of supported settings and capabilities in a reasonably readable form for this tap is available by running:

```bash
tap-totango --about --format=json
```

Each endpoint from the [Totango Search API](https://support.totango.com/hc/en-us/sections/360005893212-Totango-API) requires some parameters with the same name for the query, such as `terms`, `count`, and `offset`. In these cases, we provide settings namespaced by the stream name (e.g. `accounts_terms`,  `users_offset` , etc.).

``` yaml
settings_group_validation: # An array of arrays listing the minimal valid group of settings required to use the connector
- - api_url
  - auth_token
  - events_terms
  - events_count
  - events_offset
  - accounts_terms
  - accounts_fields
  - users_terms
  - users_fields
settings:
  - name: api_url
    description: |
      The url for the API services. 
      
      https://api.totango.com is for US services, whereas https://api-eu1.totango.com is for EU services.
    documentation: https://support.totango.com/hc/en-us/articles/360048132792-Search-API-events-
    kind: string 
    value: https://api.totango.com
  - name: auth_token
    description: |
      The token to authenticate against the API service.
    documentation: https://support.totango.com/hc/en-us/articles/203036939-Personal-Access-Token-and-Service-ID
    kind: password
  - name: events_terms
    description: |
      An array containing filter conditions to use for the events stream search.
    documentation: https://support.totango.com/hc/en-us/articles/360048132792-Search-API-events-
    kind: array
    value: []
  - name: events_count
    description: |
      The maximum number of accounts to return in the events result set.

      The max. value for count is `1000`.
    documentation: https://support.totango.com/hc/en-us/articles/360048132792-Search-API-events-
    kind: integer
    value: 1000
  - name: events_offset
    description: |
      Page number (0 is the 1st-page).
    documentation: https://support.totango.com/hc/en-us/articles/360048132792-Search-API-events-
    kind: integer
    value: 0
  - name: account_id
    description: |
      Filter the events stream results for a specific account.
    documentation: https://support.totango.com/hc/en-us/articles/360048132792-Search-API-events-
    kind: string
  - name: accounts_terms
    description: |
      An array containing filter conditions to use for the accounts stream search.
    documentation: https://support.totango.com/hc/en-us/articles/204174135-Search-API-accounts-and-users-
    kind: array
    value: []
  - name: accounts_fields
    description: |
      List of fields to return as results. 

      Note that the account name and account-id are always returned as well.
    documentation: https://support.totango.com/hc/en-us/articles/204174135-Search-API-accounts-and-users-
    kind: array
    value: []
  - name: accounts_count
    description: |
      The maximum number of accounts to return in the accounts result set. 

      The max. value for count is 1000.
    documentation: https://support.totango.com/hc/en-us/articles/204174135-Search-API-accounts-and-users-
    kind: integer
    value: 1000
  - name: accounts_offset
    description: |
      Record number (0 states "start at record 0"). 
      
      The record size can be defined using the count parameter (and limited to 1000). 
      
      Tip: To page through results, ask for 1000 records (count: 1000). If you receive 1000 records, assume there’s more, in which case you want to pull the next 1000 records (offset: 1000…then 2000…etc.). Repeat paging until the number of records returned is less than 1000.
    documentation: https://support.totango.com/hc/en-us/articles/204174135-Search-API-accounts-and-users-
    kind: integer
    value: 0
  - name: accounts_sort_by
    description: |
      Field name to sort the accounts stream results set by.
    documentation: https://support.totango.com/hc/en-us/articles/204174135-Search-API-accounts-and-users-
    kind: string
    value: "display_name"
  - name: accounts_sort_order
    description: |
      Order to sort the accounts stream results set by.
    documentation: https://support.totango.com/hc/en-us/articles/204174135-Search-API-accounts-and-users-
    kind: string
    value: "ASC"
  - name: users_terms
    description: |
      An array containing filter conditions to use for the users stream search.
    documentation: https://support.totango.com/hc/en-us/articles/204174135-Search-API-accounts-and-users-
    kind: array
    value: []
  - name: users_fields
    description: |
      List of fields to return as results. 

      Note that the account name and account-id are always returned as well.
    documentation: https://support.totango.com/hc/en-us/articles/204174135-Search-API-accounts-and-users-
    kind: array
    value: []
  - name: users_count
    description: |
      The maximum number of accounts to return in the users result set. 

      The max. value for count is 1000.
    documentation: https://support.totango.com/hc/en-us/articles/204174135-Search-API-accounts-and-users-
    kind: integer
    value: 1000
  - name: users_offset
    description: |
      Record number (0 states "start at record 0"). 
      
      The record size can be defined using the count parameter (and limited to 1000). 
      
      Tip: To page through results, ask for 1000 records (count: 1000). If you receive 1000 records, assume there’s more, in which case you want to pull the next 1000 records (offset: 1000…then 2000…etc.). Repeat paging until the number of records returned is less than 1000.
    documentation: https://support.totango.com/hc/en-us/articles/204174135-Search-API-accounts-and-users-
    kind: integer
    value: 0
  - name: users_sort_by
    description: |
      Field name to sort the users stream results set by.
    documentation: https://support.totango.com/hc/en-us/articles/204174135-Search-API-accounts-and-users-
    kind: string
    value: "display_name"
  - name: users_sort_order
    description: |
      Order to sort the users stream results set by.
    documentation: https://support.totango.com/hc/en-us/articles/204174135-Search-API-accounts-and-users-
    kind: string
    value: "ASC"
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

You should create a [Totango API personal access token](https://support.totango.com/hc/en-us/articles/203036939-Personal-Access-Token-and-Service-ID) and provide it as the `auth_token` setting for the tap.

We recommend passing it as an environment variable. For instance, when using the tap with Meltano you should add the following line to your `.env` file:

``` bash
export TAP_TOTANGO_AUTH_TOKEN=< YOUR_PERSONAL_ACCESS_TOKEN >
```

## Usage

You can easily run `tap-totango` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-totango --version
tap-totango --help
tap-totango --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-totango` CLI interface directly using `poetry run`:

```bash
poetry run tap-totango --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-totango
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-totango --version
# OR run a test `elt` pipeline:
meltano elt tap-totango target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.

## Acknowledgements

Edson Nogueira thanks all members of the Meltaners group @ Indicium Tech, namely Cesar Rubim, Lucas Marques, Guilherme Tavares e Igor Benincá, for the professional guidance.

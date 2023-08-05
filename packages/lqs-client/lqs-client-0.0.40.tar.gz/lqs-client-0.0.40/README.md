<p align="center">
  <br/>
  <img src="misc/images/logqs_logo.png?raw=true" alt="LogQS Logo" width="250"/>
</p>

# LogQS Client

A Python library for interacting with a LogQS DataStore API.  More information and examples can be found at https://docs.logqs.com.

## Installation

Requires Python >= 3.6

Instally from PyPI, using pip:

    $ pip install logqs-client

## Quickstart

Create a client instance:

    from lqs_client import LogQS
    lqs = LogQS(
        api_url="<LQS API URL>",
        api_key_id="<LQS API KEY ID>",
        api_key_secret="<LQS API KEY SECRET>"
    )

Interact with the LogQS API:

    response = lqs.list.log()
    data = response["data"]
    print(data)

Alternatively, you can use the LogQS Client from the command line.  If you have the configuration set as environment variables or in a .env file:

    $ python -m lqs_client list log

## Configuration

### Required Parameters

The LogQS Client requires three parameters to be configured:

`LQS_API_URL`

&ensp;&ensp;The URL of the endpoint for the LogQS API.  This should be the base URL for all REST operations, i.e., if the DataStore's API includes a `/api` subpath, this should be included.

&ensp;&ensp;This parameter can be supplied/overridden with the `api_url` parameter.

`LQS_API_KEY_ID`

&ensp;&ensp;The ID of the API Key for which the client will operate as.

&ensp;&ensp;This parameter can be supplied/overridden with the `api_key_id` parameter.

`LQS_API_KEY_SECRET`

&ensp;&ensp;The secret of the API Key for which the client will operate as.

&ensp;&ensp;This parameter can be supplied/overridden with the `api_key_secret` parameter.

### Optional Parameters

Optional parameters include:

`LQS_PRETTY`

&ensp;&ensp;A boolean parameter indicating whether or not to "prettify" the output results.  Useful when using the client in the command line.  Default is `false`.

&ensp;&ensp;This parameter can be supplied/overrident with the `pretty` parameter.

`LQS_VERBOSE`

&ensp;&ensp;A boolean parameter indicating whether to log debug information.  Default is `false`.

&ensp;&ensp;This parameter can be supplied/overriden with the `verbose` parameter.

`LQS_DRY_RUN`

&ensp;&ensp;A boolean parameter indicating whether to execute actual API requests.  Default is `false`.

&ensp;&ensp;This parameter can be supplied/overriden with the `dry_run` parameter.

`LQS_RETRY_COUNT`

&ensp;&ensp;An integer parameter greater than or equal to 0 indicating the number of times we should retry failed API requests.  Default is `4`

&ensp;&ensp;This parameter can be supplied/overriden with the `retry_count` parameter.

`LQS_RETRY_DELAY`

&ensp;&ensp;An integer parameter greater than or equal to 0 indicating the initial value, in seconds, we use for exponential backoff when waiting to retry a failed request.  Default is `4`

&ensp;&ensp;This parameter can be supplied/overriden with the `retry_delay` parameter.

`LQS_RETRY_AGRESSIVE`

&ensp;&ensp;A boolean parameter indicating whether we should retry on "expected" errors from LogQS (such as "BadRequest", "Conflict", etc.).  Default is `false`.

&ensp;&ensp;This parameter can be supplied/overriden with the `retry_aggressive` parameter.

## Development

The LogQS Client module source is located in `lqs-client` and it's Python requirements are listed in the `requirements.txt` file.  You can install it locally with `pip install .`.

The project uses Python 3.9, which may require some dependencies to be required.  In one go,

    sudo apt install python3.9 python3.9-dev python3.9-distutils python3.9-venv

To run the application from this directory (i.e., for development):

1. Create a virtual environment:

    `python3.9 -m venv venv`

2. Source the environment:

    `source venv/bin/activate`

3. Install the requirements:
    
    `pip install -r requirements.txt`

4. Install LogQS Client in develop mode:
    
    `pip install -e .`

5. Run the module:
    
    `python -m lqs-client`

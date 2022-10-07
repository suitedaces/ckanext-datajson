# ckanext-datajson

[![Github Actions](https://github.com/GSA/ckanext-datajson/actions/workflows/test.yml/badge.svg)](https://github.com/GSA/ckanext-datajson/actions)
[![PyPI version](https://badge.fury.io/py/ckanext-datajson.svg)](https://badge.fury.io/py/ckanext-datajson)

A CKAN extension containing plugins `datajson`.
First is used by http://catalog.data.gov/ to harvest data sources
from a remote /data.json file according to the U.S. Project
Open Data metadata specification (https://resources.data.gov/schemas/dcat-us/v1.1/).

Plugin `datajson` provides a harvester to import datasets from other
remote /data.json files. See below for setup instructions.

And the plugin also provides a new view to validate /data.json files
at http://ckanhostname/pod/validate.


## Features

Three plugins are provided.

- [:heavy_check_mark:] **datajson** provides data.json export and DCAT-US metadata UI integration
- [:heavy_check_mark:] **datajson_harvest** extends [ckanext-harvest](https://github.com/ckan/ckanext-harvest/)
to collect metadata fromremote data.json sources
- [:warning:] **cmsdatanav_harvest** extends [ckanext-harvest](https://github.com/ckan/ckanext-harvest/)
to collect metadata from for the CMS Data Navigator catalog
- [:heavy_check_mark:] **datajson_validator** provides a web form to validate dcat-us metadata data.json compliance.


## Usage

### Requirements

All requirements are tracked `setup.py` when possible.  Some CKAN extensions are not on PyPI, so they 
(and their dependencies) must be tracked in `requirements.txt`.
- [ckanext-harvest](https://github.com/ckan/ckanext-harvest/)

CKAN version   | Compatibility
-------------- | -------------
<=2.7          | :x:
2.8            | :warning:
2.9.5          | :heavy_check_mark:
2.9.6          | :heavy_check_mark:

### Installation

To install, activate your CKAN virtualenv, install dependencies, and
install the module in develop mode, which just puts the directory in your
Python path.

	. path/to/pyenv/bin/activate
	pip install -r requirements.txt
	python setup.py develop

Then in your CKAN .ini file, add `datajson`
to your ckan.plugins line:

	ckan.plugins = (other plugins here...) datajson

That's the plugin for /data.json output. To make the harvester available,
also add:

	ckan.plugins = (other plugins here...) harvest datajson_harvest
	
To make the datajson validator route and web form available, also add:

	ckan.plugins = (other plugins here...) datajson_validator


### Caching /data.json

If you're deploying inside Apache, some caching would be a good idea
because generating the /data.json file can take a good few moments.
Enable the cache modules:

	a2enmod cache
	a2enmod disk_cache

And then in your Apache configuration add:

	CacheEnable disk /data.json
	CacheRoot /tmp/apache_cache
	CacheDefaultExpire 120
	CacheMaxFileSize 50000000
	CacheIgnoreCacheControl On
	CacheIgnoreNoLastMod On
	CacheStoreNoStore On

And be sure to create /tmp/apache_cache and make it writable by the Apache process.


### Generating /data.json Off-Line

Generating this file is a little slow, so an alternative instead of caching is
to generate the file periodically (e.g. in a cron job). In that case, you'll want
to change the path that CKAN generates the file at to something *other* than /data.json.
In your CKAN .ini file, in the app:main section, add:

	ckanext.datajson.path = /internal/data.json

Now create a crontab file ("mycrontab") to download this URL to a file on disk
every ten minutes:

	0-59/10 * * * * wget -qO /path/to/static/data.json http://localhost/internal/data.json

And activate your crontab like so:

	crontab mycrontab

In Apache, we'll want to block outside access to the "internal" URL, and also
map the URL /data.json to the static file. In your httpd.conf, add:

	Alias /data.json /path/to/static/data.json
	
	<Location /internal/>
		Order deny,allow
		Allow from 127.0.0.1
		Deny from all
	</Location>

And then restart Apache. Wait for the cron job to run once, then check if
/data.json loads (and it should be fast!). Also double check that
http://yourdomain.com/internal/data.json gives a 403 forbidden error when
accessed from some other location.


### Configuration

You can customize the URL that generates the data.json output:

	ckanext.datajson.path = /data.json
	ckanext.datajsonld.path = /data.jsonld
	ckanext.datajsonld.id = http://www.youragency.gov/data.json

You can enable or disable the Data.json output by setting

    ckanext.datajson.url_enabled = False

If ckanext.datajsonld.path is omitted, it defaults to replacing ".json" in your
ckanext.datajson.path path with ".jsonld", so it probably won't need to be
specified.

The option ckanext.datajsonld.id is the @id value used to identify the data
catalog itself. If not given, it defaults to ckan.site_url.

You can specify which export map file to use to generates the data.json

    ckanext.datajson.export_map_filename = export.map.json

There are three map files available in folder [export_map](https://github.com/GSA/ckanext-datajson/tree/main/ckanext/datajson/export_map)
to choose from, or you can add you own in the same folder. By default, it looks
for file `export.map.json`, if not found, it defaults to
`export.catalog.map.sample.json`.

### Harvesting

To use the data.json harvester, you'll also need to set up the CKAN harvester
extension. See the CKAN harvester README at https://github.com/okfn/ckanext-harvest
for how to do that. You'll set some configuration variables and then initialize the
CKAN harvester plugin using:

	ckan -c /path/to/ckan.ini harvester initdb

Now you can set up a new DataJson harvester by visiting:

	http://yourdomain.com/harvest

And when configuring the data source, just choose "/data.json" as the source type.


## Development

### Setup

Build the docker containers.

    $ make build

Start the docker containers.

    $ make up

CKAN will start at [localhost:5000](http://localhost:5000/).

Clean up any containers and volumes.

    $ make clean

Open a shell to run commands in the container.

    $ docker-compose exec app /bin/bash

If you're unfamiliar with docker-compose, see our
[cheatsheet](https://github.com/GSA/datagov-deploy/wiki/Docker-Best-Practices#cheatsheet)
and the [official docs](https://docs.docker.com/compose/reference/).

For additional make targets, see the help.

    $ make help


### Testing

They follow the guidelines for [testing CKAN
extensions](https://docs.ckan.org/en/2.9/extensions/testing-extensions.html#testing-extensions).

To run the extension tests, start the containers with `make up`, then:

    $ make test

Lint the code.

    $ make lint


### Matrix builds

The test development environment drops as many dependencies as possible. It is
not meant to have feature parity with
[GSA/catalog.data.gov](https://github.com/GSA/catalog.data.gov/). Tests should
mock external dependencies where possible.

In order to support multiple versions of CKAN, or even upgrade to new versions
of CKAN, we support development and testing through the `CKAN_VERSION`
environment variable.

    $ make CKAN_VERSION=2.9.5 test
    $ make CKAN_VERSION=2.9 test
    
Note: When testing patch versions of CKAN, the services may not have patch releases.
So, take note of the `SERVICES_VERSION` variable which tracks the minor release to 
pull for the `db` and `solr` images.


## Credit / Copying

Original work written by the HealthData.gov team. It has been modified in support of Data.gov.

As a work of the United States Government, this package is in the public
domain within the United States. Additionally, we waive copyright and
related rights in the work worldwide through the CC0 1.0 Universal
public domain dedication (which can be found at http://creativecommons.org/publicdomain/zero/1.0/).

## Ways to Contribute
We're so glad you're thinking about contributing to ckanext-datajson!

Before contributing to ckanext-datajson we encourage you to read our
[CONTRIBUTING](CONTRIBUTING.md) guide, our [LICENSE](LICENSE.md), and our README
(you are here), all of which should be in this repository. If you have any
questions, you can email the Data.gov team at
[datagov@gsa.gov](mailto:datagov@gsa.gov).

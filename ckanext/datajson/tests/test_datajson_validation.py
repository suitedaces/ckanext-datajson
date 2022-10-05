from datetime import datetime
import json
import logging

import pytest

from urllib.error import URLError

import ckan.plugins as p
import ckanext.harvest.model as harvest_model
import ckanext.harvest.queue as queue
from . import mock_datajson_source
from ckan import model
from ckan.lib.munge import munge_title_to_name
from ckanext.datajson.harvester_datajson import DataJsonHarvester
from ckanext.datajson.exceptions import ParentNotHarvestedException
from .factories import HarvestJobObj, HarvestSourceObj
from mock import Mock, patch

try:
    from ckan.tests.helpers import reset_db
    from ckan.tests.factories import Organization, Sysadmin
except ImportError:
    from ckan.new_tests.helpers import reset_db
    from ckan.new_tests.factories import Organization, Sysadmin

log = logging.getLogger(__name__)


class TestDataJsonValidation(object):

    @classmethod
    def setup(cls):
        # Start data json sources server we can test harvesting against it
        reset_db()
        harvest_model.setup()
        cls.user = Sysadmin()
        cls.org = Organization()

    def test_data_json_validator_route(self, app):
        ''' Test that route returns 200 '''

        res = app.get('/pod/validate')

        assert res.status_code == 200
        assert 'Validate a DCAT-US /data.json File' in res.body

    def test_data_json_without_url(self, app):
        ''' Test that a valid data.json passes '''

        res = app.post('/pod/validate')

        assert res.status_code == 200
        assert 'Bad Request' in res.body
        assert 'Please send a post request with &#39;url&#39; in the payload' in res.body

        res = app.post('/pod/validate', data={'url2':'data.gov'})

        assert res.status_code == 200
        assert 'Bad Request' in res.body
        assert 'Please send a post request with &#39;url&#39; in the payload' in res.body

    def test_data_json_valid(self, app):
        ''' Test that a valid data.json passes '''

        res = app.post('/pod/validate', data={'url':'https://raw.githubusercontent.com/GSA/ckanext-datajson/main/ckanext/datajson/tests/datajson-samples/collection-1-parent-2-children.data.json'})

        assert res.status_code == 200
        assert 'No Errors' in res.body
        assert 'Great job!' in res.body

    def test_data_json_bad_link(self, app):
        ''' Test that a bad link fails '''

        res = app.post('/pod/validate', data={'url':'data.gov'})

        assert res.status_code == 200
        assert 'Invalid JSON' in res.body
        assert 'The file does not meet basic JSON syntax requirements' in res.body

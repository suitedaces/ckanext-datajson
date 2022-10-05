import logging

log = logging.getLogger(__name__)


class TestDataJsonValidation(object):

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

        res = app.post('/pod/validate', data={'url2': 'data.gov'})

        assert res.status_code == 200
        assert 'Bad Request' in res.body
        assert 'Please send a post request with &#39;url&#39; in the payload' in res.body

    def test_data_json_valid(self, app):
        ''' Test that a valid data.json passes '''

        res = app.post('/pod/validate', data={
            'url': ('https://raw.githubusercontent.com/GSA/ckanext-datajson/main/ckanext/datajson/tests/datajson-samples/'
                    'collection-1-parent-2-children.data.json')
        })

        assert res.status_code == 200
        assert 'No Errors' in res.body
        assert 'Great job!' in res.body

    def test_data_json_bad_link(self, app):
        ''' Test that a bad link fails '''

        res = app.post('/pod/validate', data={'url': 'data.gov'})

        assert res.status_code == 200
        assert 'Invalid JSON' in res.body
        assert 'The file does not meet basic JSON syntax requirements' in res.body

    def test_data_json_invalid(self, app):
        ''' Test that an invalid data.json fails '''

        res = app.post('/pod/validate', data={
            'url': ('https://raw.githubusercontent.com/GSA/ckanext-datajson/f8ff81f9dfd2eaa89d51efb30d06cb7b25416672/ckanext/'
                    'datajson/tests/datajson-samples/bad.data.json')
        })

        assert res.status_code == 200
        assert 'Missing Required Fields' in res.body
        assert 'The &#39;accessLevel&#39; field is missing. (1 locations)' in res.body
        assert 'The &#39;bureauCode&#39; field is missing. (1 locations)' in res.body
        assert 'The &#39;contactPoint&#39; field is missing. (1 locations)' in res.body
        assert 'The &#39;description&#39; field is missing. (2 locations)' in res.body
        assert 'The &#39;identifier&#39; field is missing. (1 locations)' in res.body
        assert 'The &#39;keyword&#39; field is missing. (1 locations)' in res.body
        assert 'The &#39;modified&#39; field is missing. (1 locations)' in res.body
        assert 'The &#39;programCode&#39; field is missing. (1 locations)' in res.body
        assert 'The &#39;publisher&#39; field is missing. (1 locations)' in res.body
        assert 'The &#39;title&#39; field is missing. (1 locations)' in res.body

# ---- builtin modules ----
import json
import os
from random import choice
import sys

# ---- external modules ----
import arrow
from marshmallow import ValidationError
import pytest
import requests

# ---- user defined modules ----
import inspect
currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
from index import validate_location, ntn_site_runner, point_within_radius
from common.error_handling import get_error

# change working directory so relative file loads still work
root_dir = sys.path[0]
os.chdir(root_dir)


@pytest.mark.data
class TestIndexFunctions:
    '''
        Unit tests pertaining to helper functions found in index.py
    '''

    @pytest.mark.parametrize('location', ('string', 'empty', '( , -99.123456)', '(44.123456, )',
                                          '(-90.123456, -23.123456)', '(23.123456, -180.123456)',
                                          '(90.123456, -23.123456)', '(23.123456, 180.123456)',
                                          '-42.123456, -23.123456', '-42.123456,-23.123456'))
    def test_invalid_location(self, location):
        '''
            test invalid location
        '''

        if location == 'empty':
            location = ''

        assert pytest.raises(ValidationError, validate_location, location)


    @pytest.mark.parametrize('location', ('(-42.123456, -23.123456)', '(-42.123456,-23.123456)'))
    def test_valid_location(self, location):
        '''
            test valid location
        '''

        if location == 'empty':
            location = ''

        assert validate_location(location) == True

    @pytest.mark.parametrize('url', ('http://nadp.slh.wisc.edu/data/sites/CSV/?net=blargh',
                                     'http://www.google.com',
                                     'test'))
    def test_invalid_ntn_site(self, url):
        '''
            test invalid location
        '''

        assert ntn_site_runner(url) == {}

    @pytest.mark.parametrize('url', ('http://nadp.slh.wisc.edu/data/sites/CSV/?net=NTN',))
    def test_valid_ntn_site(self, url):
        '''
            test valid ntn site
        '''

        assert ntn_site_runner(url) != {}

    @pytest.mark.parametrize('url', ('http://nadp.slh.wisc.edu/data/sites/CSV/?net=blargh',
                                     'http://www.google.com',
                                     'test'))
    def test_invalid_ntn_site(self, url):
        '''
            test invalid ntn site
        '''

        assert ntn_site_runner(url) == {}
        
        
@pytest.mark.endpoint
class Test_NTN_Get_By_ID_Endpoint:
    '''
        tests pertaining to the ntn/samples/get/by_id/ endpoint
    '''

    ntn_samples_base_url = '{host}/{version}/ntn/samples/get/by_id/'
    ntn_samples_formattable_url = '{host}/{version}/ntn/samples/get/by_id/?site_id={site_id}&start_date={start_date}&end_date={end_date}'

    def test_ntn_get_by_id_200(self, host):
        '''
            test a good call
        '''

        response = requests.get(self.ntn_samples_formattable_url.format(host=host, version='v1.0', site_id="AB32", start_date=1472688000, end_date=1475193600))
        assert response.status_code == 200
        expected_response = {
            "data":{
                "AB32":{
                    "TQ0742SW":{
                        "Br":"-9",
                        "Ca":"-9.000",
                        "Cl":"-9.000",
                        "Conduc":"-9.000",
                        "K":"-9.000",
                        "Mg":"-9.000",
                        "NH4":"-9.000",
                        "NO3":"-9.000",
                        "Na":"-9.000",
                        "SO4":"-9.000",
                        "dateoff":"2016-09-20 15:10",
                        "dateon":"2016-09-13 18:40",
                        "flagBr":"0",
                        "flagCa":" ",
                        "flagCl":" ",
                        "flagK":" ",
                        "flagMg":" ",
                        "flagNH4":"<",
                        "flagNO3":" ",
                        "flagNa":" ",
                        "flagSO4":" ",
                        "invalcode":"c           ",
                        "modifiedOn":"",
                        "ph":"-9.000",
                        "ppt":"0.762",
                        "subppt":"0.762",
                        "svol":"74.800",
                        "valcode":"  ",
                        "yrmonth":"201609"
                    },
                    "TQ1132SW":{
                        "Br":"-9",
                        "Ca":"-9.000",
                        "Cl":"-9.000",
                        "Conduc":"-9.000",
                        "K":"-9.000",
                        "Mg":"-9.000",
                        "NH4":"-9.000",
                        "NO3":"-9.000",
                        "Na":"-9.000",
                        "SO4":"-9.000",
                        "dateoff":"2016-09-28 16:00",
                        "dateon":"2016-09-20 15:15",
                        "flagBr":"0",
                        "flagCa":" ",
                        "flagCl":" ",
                        "flagK":" ",
                        "flagMg":" ",
                        "flagNH4":" ",
                        "flagNO3":" ",
                        "flagNa":" ",
                        "flagSO4":" ",
                        "invalcode":"v           ",
                        "modifiedOn":"",
                        "ph":"-9.000",
                        "ppt":"0.508",
                        "subppt":"0.508",
                        "svol":"7.800",
                        "valcode":"  ",
                        "yrmonth":"201609"
                    }
                }
            },
            "errors":{}
        }
        assert json.loads(response.text) == expected_response

    def test_ntn_get_by_id_invalid_version(self, host):
        '''
            test invalid version
        '''

        response = requests.get(self.ntn_samples_formattable_url.format(host=host, version='v1.1', site_id="AB32", start_date=1472688000, end_date=1475193600))
        assert response.status_code == 400
        response_json = json.loads(response.text)
        assert '01x001' in response_json['errors']

    @pytest.mark.parametrize('site_id', ('123', '12345'))
    def test_ntn_get_by_id_invalid_site_id(self, host, site_id):
        '''
            test invalid site_id
        '''

        response = requests.get(self.ntn_samples_formattable_url.format(host=host, version='v1.0', site_id=site_id, start_date=1472688000, end_date=1475193600))
        assert response.status_code == 400
        response_json = json.loads(response.text)
        assert '01x004' in response_json['errors']

    def test_ntn_get_by_id_site_id_not_found(self, host):
        '''
            test site_id not found
        '''

        response = requests.get(self.ntn_samples_formattable_url.format(host=host, version='v1.0', site_id="9999", start_date=1472688000, end_date=1475193600))
        assert response.status_code == 200
        expected_response = {
            "data":{},
            "errors":{}
        }
        assert json.loads(response.text) == expected_response

    @pytest.mark.parametrize('date_type', ('start_date', 'end_date'))
    @pytest.mark.parametrize('date', ('-1', 'test', 'future'))
    def test_ntn_get_by_id_invalid_date(self, host, date_type, date):
        '''
            test invalid start_date/end_date
        '''
        
        args = {
            'host': host,
            'version': 'v1.0',
            'site_id': 'AB32',
            'start_date': 1472688000,
            'end_date': 1475193600
        }
        if date == 'future':
            args[date_type] = int(arrow.get().shift(hours=+1).timestamp)
        else:
            args[date_type] = date
        response = requests.get(self.ntn_samples_formattable_url.format(**args))
        assert response.status_code == 400
        response_json = json.loads(response.text)
        assert '01x002' in response_json['errors']

    @pytest.mark.parametrize('param', ('start_date', 'end_date', 'site_id'))
    def test_ntn_get_by_id_missing_param(self, host, param):
        '''
            test missing query string parameters
        '''

        url = self.ntn_samples_base_url.format(host=host, version='v1.0')
        args = {
            'site_id': 'AB32',
            'start_date': 1472688000,
            'end_date': 1475193600
        }
        args.pop(param)

        response = requests.get(url, params=args)
        assert response.status_code == 400
        response_json = json.loads(response.text)
        if param in ['start_date', 'end_date']:
            assert '01x002' in response_json['errors']
        else:
            assert '01x004' in response_json['errors']


@pytest.mark.endpoint
class Test_NTN_Site_Info_Endpoint:
    '''
        tests pertaining to the ntn/site/info/ endpoint
    '''

    ntn_site_info_base_url = '{host}/{version}/ntn/site/info/'
    ntn_site_info_formattable_url = '{host}/{version}/ntn/site/info/?site_id={site_id}'

    def test_ntn_get_by_id_200(self, host):
        '''
            test a good call
        '''

        response = requests.get(self.ntn_site_info_formattable_url.format(host=host, version='v1.0', site_id="AB32"))
        assert response.status_code == 200
        expected_response = {
            "data":{
                "county":"",
                "elevation":"265",
                "latitude":"57.2096",
                "longitude":"-111.6471",
                "network":"NTN",
                "siteName":"Fort Mackay",
                "startdate":"2016-09-13 05:00",
                "state":"AB",
                "status":"A",
                "stopdate":""
            },
            "errors":{}
        }
        assert json.loads(response.text) == expected_response

    def test_ntn_get_by_id_invalid_version(self, host):
        '''
            test invalid version
        '''

        response = requests.get(self.ntn_site_info_formattable_url.format(host=host, version='v1.1', site_id="AB32"))
        assert response.status_code == 400
        response_json = json.loads(response.text)
        assert '01x001' in response_json['errors']

    @pytest.mark.parametrize('site_id', ('123', '12345', '9999'))
    # 9999 is included here because a not site_id not found results in a 400.
    def test_ntn_get_by_id_invalid_site_id(self, host, site_id):
        '''
            test invalid site_id
        '''

        response = requests.get(self.ntn_site_info_formattable_url.format(host=host, version='v1.0', site_id=site_id))
        assert response.status_code == 400
        response_json = json.loads(response.text)
        assert '01x004' in response_json['errors']

    @pytest.mark.parametrize('param', ('site_id',))
    def test_ntn_get_by_id_missing_param(self, host, param):
        '''
            test missing query string parameters
        '''

        url = self.ntn_site_info_base_url.format(host=host, version='v1.0')
        args = {
            'site_id': "AB32"
        }
        args.pop(param)

        response = requests.get(url, params=args)
        assert response.status_code == 400
        response_json = json.loads(response.text)
        if param == 'site_id':
            assert '01x004' in response_json['errors']


@pytest.mark.endpoint
class Test_NTN_Site_Info_By_Radius_Endpoint:
    ntn_site_info_by_radius_base_url = '{host}/{version}/ntn/site/info/by_radius/'
    ntn_site_info_by_radius_formattable_url = '{host}/{version}/ntn/site/info/by_radius/?location={location}&radius={radius}'

    def test_ntn_get_by_id_200(self, host):
        '''
            test a good call
        '''

        response = requests.get(self.ntn_site_info_by_radius_formattable_url.format(host=host, version='v1.0', location='(42.4944,-108.8320)', radius=20))
        assert response.status_code == 200
        expected_response = {
            "data":{
                "WY02":{
                    "county":"Fremont",
                    "elevation":"2164",
                    "latitude":"42.7336",
                    "longitude":"-108.8498",
                    "network":"NTN",
                    "siteName":"Sinks Canyon",
                    "startdate":"1984-08-21 05:00",
                    "state":"WY",
                    "status":"A",
                    "stopdate":""
                },
                "WY97":{
                    "county":"Fremont",
                    "elevation":"2524",
                    "latitude":"42.4944",
                    "longitude":"-108.8320",
                    "network":"NTN",
                    "siteName":"South Pass City",
                    "startdate":"1985-04-30 05:00",
                    "state":"WY",
                    "status":"A",
                    "stopdate":""
                }
            },
            "errors":{}
        }
        assert json.loads(response.text) == expected_response

    def test_ntn_get_by_id_invalid_version(self, host):
        '''
            test invalid version
        '''

        response = requests.get(self.ntn_site_info_by_radius_formattable_url.format(host=host, version='v1.1', location='(42.4944,-108.8320)', radius=20))
        assert response.status_code == 400
        response_json = json.loads(response.text)
        assert '01x001' in response_json['errors']

    @pytest.mark.parametrize('location', ('(42.4944,)', '(,-108.8320)',
                                          '(42.4944,test)', '(test,-108.8320)',
                                          '(42.4944,-180.0000000001)', '(42.4944,180.0000000001)',
                                          '(-90.0000000001,-108.8320)', '(90.0000000001,-108.8320)',
                                          '42.4944,-108.8320', '42.4944, -108.8320',
                                          '', ',', 'test'))
    def test_ntn_get_by_id_invalid_location(self, host, location):
        '''
            test invalid location
        '''

        response = requests.get(self.ntn_site_info_by_radius_formattable_url.format(host=host, version='v1.0', location=location, radius=20))
        assert response.status_code == 400
        response_json = json.loads(response.text)
        assert '01x006' in response_json['errors']

    @pytest.mark.parametrize('location', ('(42.4944,-108.8320)', '(42.4944, -108.8320)',
                                          '(-42.4944,-108.8320)', '(-42.4944, -108.8320)',
                                          '(42.4944,108.8320)', '(42.4944, 108.8320)',
                                          '(-42.4944,108.8320)', '(-42.4944, 108.8320)'))
    def test_ntn_get_by_id_valid_location(self, host, location):
        '''
            test valid location
        '''

        response = requests.get(self.ntn_site_info_by_radius_formattable_url.format(host=host, version='v1.0', location=location, radius=20))
        assert response.status_code == 200

    @pytest.mark.parametrize('radius', ('test', '', '-1', '3958.9'))
    def test_ntn_get_by_id_invalid_radius(self, host, radius):
        '''
            test invalid radius
        '''

        response = requests.get(self.ntn_site_info_by_radius_formattable_url.format(host=host, version='v1.0', location='(42.4944,-108.8320)', radius=radius))
        assert response.status_code == 400
        response_json = json.loads(response.text)
        assert '01x002' in response_json['errors']

    @pytest.mark.parametrize('radius', ('0', '3958.8'))
    def test_ntn_get_by_id_valid_radius(self, host, radius):
        '''
            test valid radius
        '''

        response = requests.get(self.ntn_site_info_by_radius_formattable_url.format(host=host, version='v1.0', location='(42.4944,-108.8320)', radius=radius))
        assert response.status_code == 200

    @pytest.mark.parametrize('param', ('location', 'radius'))
    def test_ntn_get_by_id_missing_param(self, host, param):
        '''
            test missing query string parameters
        '''

        url = self.ntn_site_info_by_radius_base_url.format(host=host, version='v1.0')
        args = {
            'site_id': 'AB32',
            'location': '(42.4944,-108.8320)',
            'radius': 20
        }
        args.pop(param)

        response = requests.get(url, params=args)
        assert response.status_code == 400
        response_json = json.loads(response.text)
        if param == 'location':
            assert '01x006' in response_json['errors']
        elif param == 'radius':
            assert '01x002' in response_json['errors']

'''
    This file contains the code needed for the backend of a system intended to supply data
    provided by the National Atmospheric Deposition Program: National Trends Network.
'''

# -- built-in imports
import csv
import io
import json
import re

# -- external imports
import arrow
from flask import abort, Flask, jsonify, Response
from geopy import distance
from webargs import fields
import requests
from webargs.flaskparser import  use_kwargs
from marshmallow import EXCLUDE, post_load, Schema, validates_schema, ValidationError

# -- user-defined imports
from common import logger
from common.error_handling import get_error

# -- Setup Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# -- Setup logging
index_log = logger.get_logger('logger', 'ntn_index.log')

ntn_sites_url = 'http://nadp.slh.wisc.edu/data/sites/CSV/?net=NTN'
max_radius = 3958.8


@app.errorhandler(422)
def custom_handler(error):
    '''
        A custom error handler that allows us to return more useful errors.
    '''

    errors = []
    content_type = 'application/json; charset=utf8'
    response = dict(data=dict(), errors=dict())

    try:
        if 'query' in error.data['messages']:
            if '_schema' in error.data['messages']['query']:

                response['errors'].update(error.data['messages']['query']['_schema'].messages)
                return Response(json.dumps(response), 400, mimetype=content_type)
            if 'schema_validation' in error.data['messages']['query']:
                return Response(str(error.data['messages']['query']['schema_validation']), 400, mimetype=content_type)
            for arg in error.data['messages']['query']:
                if isinstance(error.data['messages']['query'][arg], list):
                    for item in error.data['messages']['query'][arg]:
                        response['errors'].update(error.data['messages']['query'][arg][0])
                        return Response(json.dumps(response), 400, mimetype=content_type)
                elif isinstance(error.data['messages']['query'][arg], dict):
                    for item in error.data['messages']['query'][arg]:
                        response['errors'].update(error.data['messages']['query'][arg])
                        return Response(json.dumps(response), 400, mimetype=content_type)

    except Exception as e:
        return Response(str(get_error("01x999")), 400, mimetype=content_type)
    return Response(str(errors), 400, mimetype=content_type)


def json_abort(status_code, data=None, ret_response=False):
    '''
        Create a json error response with appropriate headers.
        This is used in the event of having to abort any time
        after argument validation.
    '''
    response = Response()
    data = {} if data is None else data
    response = jsonify(data)
    response.status_code = status_code
    response.headers['Content-type'] = "application/json; charset=utf8"

    if not ret_response:
        abort(response)
    else:
        return response


# -- Validation functions
def validate_location(location):
    """
        Helper function to validate format of user-provided location.

        Input variables:
            'location':
                Type: string,
        Returns:
            Type: Boolean or throws a ValidationError
    """

    loc_regex = r'^\(-?(([1-8]?[0-9])(\.[0-9]{1,10})?|90(\.0{1,10})?), ?-?((([1-9]?[0-9]|1[0-7][0-9])(\.[0-9]{1,10})?)|180(\.0{1,10})?)\)$'

    if re.compile(loc_regex).match(location) is None:
        raise ValidationError(get_error('01x006'))

    return True


# -- Helper functions
def ntn_site_runner(url):
    '''
        Helper function to convert csv response to a dictionary.

        Input variables:
            'url':
                Type: string,
        Returns:
            Type: Dictionary
    '''

    result={}

    try:
        response = requests.get(url)
        assert response.status_code == 200
        reader = csv.DictReader(io.StringIO(response.text))
        data = list(reader)
        result.update({site.pop("siteid"): site for site in data})
    except Exception as e:
        index_log.error(e)

    return result


def point_within_radius(input_location, site_location, radius):
    '''
        Validation function that returns a boolean value of whether or not a given site_location is
        within the supplied distance (radius) of the input_location.

        Input variables:
            'input_location':
                Type: tuple(latitude, longitude),
            'site_location':
                Type: tuple(latitude, longitude),
            'radius':
                Type: float (in miles),
        Returns:
            Type: Boolean
    '''

    dis = distance.distance(input_location, site_location).miles

    if dis <= radius:
        return True
    else:
        return False


# -- Schemas and Endpoints
class ntn_get_by_id_schema(Schema):
    start_date=fields.Integer(
        required=True,
        validate=lambda timestamp: 0 <= timestamp <= int(arrow.utcnow().timestamp),
        error_messages={
            "null": get_error('01x002', key='start_date', minimum=0, maximum=int(arrow.utcnow().timestamp)),
            "required": get_error('01x002', key='start_date', minimum=0, maximum=int(arrow.utcnow().timestamp)),
            "invalid": get_error('01x002', key='start_date', minimum=0, maximum=int(arrow.utcnow().timestamp)),
            "type": get_error('01x002', key='start_date', minimum=0, maximum=int(arrow.utcnow().timestamp)),
            "validator_failed": get_error('01x002', key='start_date', minimum=0, maximum=int(arrow.utcnow().timestamp)),
        }
    )
    end_date=fields.Integer(
        required=True,
        validate=lambda timestamp: 0 <= timestamp <= int(arrow.utcnow().timestamp),
        error_messages={
            "null": get_error('01x002', key='end_date', minimum=0, maximum=int(arrow.utcnow().timestamp)),
            "required": get_error('01x002', key='end_date', minimum=0, maximum=int(arrow.utcnow().timestamp)),
            "invalid": get_error('01x002', key='end_date', minimum=0, maximum=int(arrow.utcnow().timestamp)),
            "type": get_error('01x002', key='end_date', minimum=0, maximum=int(arrow.utcnow().timestamp)),
            "validator_failed": get_error('01x002', key='end_date', minimum=0, maximum=int(arrow.utcnow().timestamp)),
        }
    )
    site_id=fields.String(
        required=True,
        validate=lambda p:  len(p) == 4,
        error_messages={
            "null": get_error('01x004'),
            "required": get_error('01x004'),
            "invalid": get_error('01x004'),
            "type": get_error('01x004'),
            "validator_failed": get_error('01x004'),
        }
    )

    class Meta:
        unknown = EXCLUDE
        strict = True

    def __init__(self):
        super().__init__()

    @validates_schema
    def validate_schema(self, args, **kwargs):
        '''
            A custom validator for the schema. This is used when multiple arguments or their
            validation rely upon other arguments.
        '''
        try:
            assert args['start_date'] <= args['end_date']
        except Exception as e:
            raise ValidationError(e, 'schema_validation')

    @post_load
    def massage_input(self, args, **kwargs):
        '''
            A custom formatter for input arguments. After input arguments are validated, this
            function can be ran to format/massage data into data that is more suitable for our use.
        '''
        for date in ['start_date', 'end_date']:
            if date in args:
                args[date] = arrow.get(args[date]).format('YYYYMM')

        return args


@app.route('/<version>/ntn/samples/get/by_id/', methods=['GET'], strict_slashes=False)
@use_kwargs(ntn_get_by_id_schema, location='query')
def ntn_get_by_site_id(version, **kwargs):
    '''
        An endpoint that returns all weekly samples for a given site ID, that were sampled between
        a given start and end date.

        Input variables:
            'site_id':
                Required: Yes,
                Type: String,
                Validation: Must contain 4 characters.
        Output:
            Type: application/json
    '''

    response = dict(data=dict(), errors=dict())

    if not version == 'v1.0':
        error = get_error('01x001')
        response['errors'].update(error)
        json_abort(400, response)

    try:
        with open('NTN-All-w.csv', 'r', encoding='utf8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                site_id = row.pop("siteID")

                # if its not our site_id or within the start_date - end_date window, throw it out.
                if site_id != kwargs['site_id'] \
                or not kwargs['start_date'] <= row["yrmonth"] <= kwargs["end_date"]:
                    continue

                if not site_id in response['data']:
                    response['data'][site_id] = {}

                lab_no = row.pop("labno")

                response['data'][site_id][lab_no] = row

    except Exception as e:
        index_log.error(e)

    return response


class ntn_site_info_schema(Schema):
    site_id=fields.String(
        required=True,
        validate=lambda id: len(id) == 4,
        error_messages={
            "null": get_error('01x004', key='end_date'),
            "required": get_error('01x004', key='end_date'),
            "invalid": get_error('01x004', key='end_date'),
            "type": get_error('01x004', key='end_date'),
            "validator_failed": get_error('01x004', key='end_date'),
        }
    )

    class Meta:
        unknown = EXCLUDE
        strict = True

    def __init__(self):
        super().__init__()

    @post_load
    def massage_input(self, args, **kwargs):
        if 'site_id' in args:
            args['site_id'] = args['site_id'].upper()

        return args


@app.route('/<version>/ntn/site/info/', methods=['GET'], strict_slashes=False)
@use_kwargs(ntn_site_info_schema, location='query')
def site_info(version, **kwargs):
    '''
        An endpoint that returns the site information for a given site ID.

        Input variables:
            'site_id':
                Required: Yes,
                Type: String,
                Validation: Must contain 4 characters.
        Output:
            Type: application/json
    '''

    response = dict(data=dict(), errors=dict())

    if not version == 'v1.0':
        error = get_error('01x001')
        response['errors'].update(error)
        json_abort(400, response)

    sites = ntn_site_runner(ntn_sites_url)

    if kwargs['site_id'] in sites:
        response['data'] = sites[kwargs['site_id']]
    else:
        error = get_error('01x004')
        response['errors'].update(error)
        json_abort(400, response)

    return response


class site_info_by_radius_schema(Schema):
    include_inactive=fields.Boolean(
        required=False,
        default=True,
        missing=True,
        truthy = ['True'], # sets custom truthy values
        falsy = ['False'], # sets custom falsy values
        error_messages={
            "null": get_error('01x005'),
            "required": get_error('01x005'),
            "invalid": get_error('01x005'),
            "type": get_error('01x005'),
            "validator_failed": get_error('01x005'),
        }
    )
    location = fields.String(
        required=True,
        validate=lambda p: validate_location(p),
        error_messages={
            "null": get_error('01x006'),
            "required": get_error('01x006'),
            "invalid": get_error('01x006'),
            "type": get_error('01x006'),
            "validator_failed": get_error('01x006'),
        }
    )
    radius=fields.Float(
        required=True,
        validate=lambda radius: 0 <= radius <= max_radius,
        error_messages={
            "null": get_error('01x002', key='radius', minimum=0, maximum=max_radius),
            "required": get_error('01x002', key='radius', minimum=0, maximum=max_radius),
            "invalid": get_error('01x002', key='radius', minimum=0, maximum=max_radius),
            "type": get_error('01x002', key='radius', minimum=0, maximum=max_radius),
            "validator_failed": get_error('01x002', key='radius', minimum=0, maximum=max_radius),
        }
    )

    class Meta:
        unknown = EXCLUDE
        strict = True

    def __init__(self):
        super().__init__()

    @post_load
    def massage_input(self, args, **kwargs):
        if 'location' in args:
            formatted_location = args['location'].strip('()').split(',')
            args['location'] = (float(formatted_location[0]), float(formatted_location[1]))

        return args


@app.route('/<version>/ntn/site/info/by_radius', methods=['GET'], strict_slashes=False)
@use_kwargs(site_info_by_radius_schema, location='query')
def site_info_by_radius(version, **kwargs):
    '''
        An endpoint that returns site information for all sites within a radius of a given latitude
        and longitude, filtering out inactive sites (status==I) if requested.

        Input variables:
            'include_inactive':
                Required: No,
                Default: True,
                Type: Boolean,
                Validation: Must be True or False.
            'location':
                Required: Yes,
                Type: Boolean,
                Validation: Must be in the format (latitude, longitude).
            'radius':
                Required: Yes,
                Type: Float,
                Validation: Must be greater than or equal to 0 and less than or equal to max_radius.
        Output:
            Type: application/json
    '''

    response = dict(data=dict(), errors=dict())

    if not version == 'v1.0':
        error = get_error('01x001')
        response['errors'].update(error)
        json_abort(400, response)

    sites = ntn_site_runner(ntn_sites_url)

    for site in sites:
        site_location = (float(sites[site]['latitude']), float(sites[site]['longitude']))

        if point_within_radius(kwargs['location'], site_location, kwargs['radius']):
            # if include_inactive flag is set, include inactive sites, otherwise only include active sites.
            if kwargs['include_inactive'] and sites[site]['status'] == 'I' \
            or sites[site]['status'] == 'A':
                response['data'][site] = sites[site]

    return response

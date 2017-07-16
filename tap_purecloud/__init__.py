#!/usr/bin/env python3

import argparse
import requests
import singer
import logging
import base64
import datetime
import time
import json
import backoff

import PureCloudPlatformApiSdk
from PureCloudPlatformApiSdk.rest import ApiException

import tap_purecloud.schemas as schemas


logger = singer.get_logger()

HTTP_SUCCESS = 200
HTTP_RATE_LIMIT_ERROR = 429
API_RETRY_INTERVAL_SECONDS = 30
API_RETRY_COUNT = 5
BASE_PURECLOUD_AUTH_HOST = 'https://login.{domain}'
BASE_PURECLOUD_API_HOST = 'https://api.{domain}'


def giveup(error):
    logger.warning("Encountered an error while syncing")
    logger.error(error)

    is_api_error = hasattr(error, 'status')
    is_rate_limit_error = error.status == HTTP_RATE_LIMIT_ERROR

    logger.debug("Is API Error? {}. Is Rate Limit Error? {}.".format(is_api_error, is_rate_limit_error))

    #  return true if we should *not* retry
    should_retry = is_api_error and is_rate_limit_error
    return not should_retry


def get_access_token(config):
    "Returns an access_token for the client credentials, or raises if unauthorized"

    client_id = config['client_id']
    client_secret = config['client_secret']
    client_domain = config['domain']

    auth_host = BASE_PURECLOUD_AUTH_HOST.format(domain=client_domain)
    auth_endpoint = '{}/oauth/token'.format(auth_host)

    client_creds = "{}:{}".format(client_id, client_secret).encode('utf-8')
    raw_authorization = base64.b64encode(client_creds)
    authorization = raw_authorization.decode('ascii')

    body = {'grant_type': 'client_credentials'}

    headers = {
        'Authorization': 'Basic {}'.format(authorization),
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(auth_endpoint, data=body, headers=headers)

    if response.status_code == HTTP_SUCCESS:
        response_json = response.json()
        return response_json['access_token']
    else:
        logger.fatal(response.json())
        raise RuntimeError("Unauthorized")


class FakeBody(object):
    def __init__(self, page_number=1, page_size=100):
        self.page_number = page_number
        self.page_size = page_size


@backoff.on_exception(backoff.constant,
                      (PureCloudPlatformApiSdk.rest.ApiException),
                      jitter=backoff.random_jitter,
                      max_tries=API_RETRY_COUNT,
                      giveup=giveup,
                      interval=API_RETRY_INTERVAL_SECONDS)

def fetch_one_page(get_records, body, entity_name, api_function_params):
    if isinstance(body, FakeBody):
        logger.info("Fetching {} records from page {}".format(body.page_size, body.page_number))
        response = get_records(page_size=body.page_size, page_number=body.page_number, **api_function_params)
    elif hasattr(body, 'page_size'):
        logger.info("Fetching {} records from page {}".format(body.page_size, body.page_number))
        response = get_records(body, **api_function_params)
    elif hasattr(body, 'paging'):
        logger.info("Fetching {} records from page {}".format(body.paging['pageSize'], body.paging['pageNumber']))
        response = get_records(body, **api_function_params)
    else:
        raise RuntimeError("Unknown body passed to request: {}".format(body))

    results = getattr(response, entity_name, [])

    if results is None:
        return response, []
    else:
        return response, results


def should_continue(api_response, body, entity_name):
    records = getattr(api_response, entity_name, [])

    if records is None or len(records) == 0:
        return False
    elif hasattr(api_response, 'page_count') and body.page_number < api_response.page_count:
        return False
    else:
        return True


def fetch_all_records(get_records, entity_name, body, api_function_params=None):
    if api_function_params is None:
        api_function_params = {}

    body.page_size = 100
    body.page_number = 1

    api_response, results = fetch_one_page(get_records, body, entity_name, api_function_params)
    yield results

    while should_continue(api_response, body, entity_name):
        body.page_number += 1

        api_response, results = fetch_one_page(get_records, body, entity_name, api_function_params)
        yield results


def fetch_all_analytics_records(get_records, body, entity_name):
    api_function_params = {}

    body.paging = {
        "pageSize": 100,
        "pageNumber": 1
    }

    api_response, results = fetch_one_page(get_records, body, entity_name, api_function_params)
    yield results

    while results is not None and len(results) > 0:
        body.paging['pageNumber'] += 1
        api_response, results = fetch_one_page(get_records, body, entity_name, api_function_params)
        yield results


def parse_dates(record):
    parsed = record.copy()
    for (k,v) in record.items():
        if isinstance(v, datetime.datetime):
            parsed[k] = v.isoformat()
    return parsed


def handle_object(obj):
    return parse_dates(obj.to_dict())


def stream_results(generator, transform_record, record_name, schema, primary_key, write_schema):
    if write_schema:
        singer.write_schema(record_name, schema, primary_key)
    for page in generator:
        records = [transform_record(record) for record in page]
        singer.write_records(record_name, records)

def sync_users(config):
    logger.info("Fetching users")
    api_instance = PureCloudPlatformApiSdk.UsersApi()
    body = FakeBody()
    gen_users = fetch_all_records(api_instance.get_users, 'entities', body, {'expand': ['locations']})
    stream_results(gen_users, handle_object, 'users', schemas.user, ['id'], True)


def sync_groups(config):
    logger.info("Fetching groups")
    api_instance = PureCloudPlatformApiSdk.GroupsApi()
    body = FakeBody()
    gen_groups = fetch_all_records(api_instance.get_groups, 'entities', body)
    stream_results(gen_groups, handle_object, 'groups', schemas.group, ['id'], True)


def sync_locations(config):
    logger.info("Fetching locations")
    api_instance = PureCloudPlatformApiSdk.LocationsApi()
    body = PureCloudPlatformApiSdk.LocationSearchRequest()
    gen_locations = fetch_all_records(api_instance.post_search, 'results', body)
    stream_results(gen_locations, handle_object, 'location', schemas.location, ['id'], True)


def handle_conversation(conversation_record):
    conversation = handle_object(conversation_record)

    participants = []
    for participant_record in conversation_record.participants:
        participants.append(handle_object(participant_record))

        sessions = []
        for session_record in participant_record.sessions:
            sessions.append(handle_object(session_record))

            segments = []
            for segment_record in session_record.segments:
                segments.append(handle_object(segment_record))

            sessions[-1]['segments'] = segments
        participants[-1]['sessions'] = sessions
    conversation['participants'] = participants

    return conversation


def sync_conversations(config):
    logger.info("Fetching conversations")
    api_instance = PureCloudPlatformApiSdk.ConversationsApi()

    sync_date = config['start_date']
    end_date = datetime.date.today() + datetime.timedelta(days=1)
    incr = datetime.timedelta(days=1)

    first_page = True
    while sync_date < end_date:
        logger.info("Syncing for {}".format(sync_date))
        next_date = sync_date + incr
        interval = '{}/{}'.format(
            sync_date.strftime('%Y-%m-%dT00:00:00.000Z'),
            next_date.strftime('%Y-%m-%dT00:00:00.000Z')
        )

        body = PureCloudPlatformApiSdk.ConversationQuery()
        body.interval = interval
        body.order = "asc"
        body.orderBy = "conversationStart"

        gen_conversations = fetch_all_analytics_records(api_instance.post_conversations_details_query, body, 'conversations')
        stream_results(gen_conversations, handle_conversation, 'conversation', schemas.conversation, ['conversation_id'], first_page)

        sync_date = next_date
        first_page = False

def handle_user_details(user_details_record):
    user_details = user_details_record.to_dict()

    primary_presence = user_details['primary_presence']
    routing_status = user_details['routing_status']

    parsed_presences = []
    if primary_presence is not None:
        for presence in primary_presence:
            parsed_presences.append(parse_dates(presence))

    parsed_statuses = []
    if routing_status is not None:
        for status in routing_status:
            parsed_statuses.append(parse_dates(status))

    user_details['primary_presence'] = parsed_presences
    user_details['routing_status'] = parsed_statuses

    return user_details


def sync_user_details(config):
    logger.info("Fetching user details")
    api_instance = PureCloudPlatformApiSdk.UsersApi()

    sync_date = config['start_date']
    end_date = datetime.date.today() + datetime.timedelta(days=1)
    incr = datetime.timedelta(days=1)

    first_page = True
    while sync_date < end_date:
        logger.info("Syncing for {}".format(sync_date))
        next_date = sync_date + incr
        interval = '{}/{}'.format(
            sync_date.strftime('%Y-%m-%dT00:00:00.000Z'),
            next_date.strftime('%Y-%m-%dT00:00:00.000Z')
        )

        body = PureCloudPlatformApiSdk.UserDetailsQuery()
        body.interval = interval
        body.order = "asc"


        gen_user_details = fetch_all_analytics_records(api_instance.post_users_details_query, body, 'user_details')
        stream_results(gen_user_details, handle_user_details, 'user_details', schemas.user_details, ['user_id'], first_page)
        sync_date = next_date

        first_page = False


def validate_config(config):
    required_keys = ['domain', 'client_id', 'client_secret', 'start_date']
    missing_keys = []
    null_keys = []
    has_errors = False

    for required_key in required_keys:
        if required_key not in config:
            missing_keys.append(required_key)

        elif config.get(required_key) is None:
            null_keys.append(required_key)

    if len(missing_keys) > 0:
        logger.fatal("Config is missing keys: {}"
                     .format(", ".join(missing_keys)))
        has_errors = True

    if len(null_keys) > 0:
        logger.fatal("Config has null keys: {}"
                     .format(", ".join(null_keys)))
        has_errors = True

    if has_errors:
        raise RuntimeError


def load_config(filename):
    config = {}

    try:
        with open(filename) as f:
            config = json.load(f)
    except Exception as e:
        logger.fatal("Failed to decode config file. Is it valid json?")
        logger.fatal(e)
        raise RuntimeError

    validate_config(config)

    return config


def load_state(filename):
    if filename is None:
        return {}

    try:
        with open(filename) as f:
            return json.load(f)
    except:
        logger.fatal("Failed to decode state file. Is it valid json?")
        raise RuntimeError


def parse_input_date(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()


def do_sync(args):
    logger.info("Starting sync.")

    config = load_config(args.config)
    state = load_state(args.state)

    # grab start date from state file. If not found
    # default to value in config file

    if 'start_date' in state:
        start_date = parse_input_date(state['start_date'])
    else:
        start_date = parse_input_date(config['start_date'])

    logger.info("Syncing data from: {}".format(start_date))

    config['start_date'] = start_date

    logger.info("Getting access token")
    access_token = get_access_token(config)

    api_host = 'https://api.{domain}'.format(domain=config['domain'])
    PureCloudPlatformApiSdk.configuration.host = api_host
    PureCloudPlatformApiSdk.configuration.access_token = access_token

    sync_users(config)
    sync_groups(config)
    sync_locations(config)
    sync_conversations(config)
    sync_user_details(config)


    new_state = {
        'start_date': datetime.date.today().strftime('%Y-%m-%d')
    }

    # singer.write_state(state)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--config', help='Config file', required=True)
    parser.add_argument(
        '-s', '--state', help='State file')

    args = parser.parse_args()

    try:
        do_sync(args)
    except RuntimeError:
        logger.fatal("Run failed.")
        exit(1)


if __name__ == '__main__':
    main()


# different schema files
# fix the imports/file structure
# state file

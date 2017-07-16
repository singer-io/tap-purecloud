user = {
    'type': 'object',
    'properties': {
        'email': {
            'type': 'string',
            'description': 'email for the user',
        },
        'id': {
            'type': 'string',
            'description': 'id for the user',
        },
        'name': {
            'type': 'string',
            'description': 'name for the user',
        },
        'username': {
            'type': 'string',
            'description': 'username for the user',
        }
    }
}

group = {
    'type': 'object',
    'properties': {
        'name': {
            'type': 'string',
            'description': 'name for the group',
        },
        'id': {
            'type': 'string',
            'description': 'id for the group',
        },
        'state': {
            'type': 'string',
            'description': 'state for the group',
        },
        'visibility': {
            'type': 'string',
            'description': 'visibility for the group',
        }
    }
}

location = {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'string',
            'description': 'id for the location',
        },
        'name': {
            'type': 'string',
            'description': 'name for the location',
        },
        'state': {
            'type': 'string',
            'description': 'state for the location',
        }
    }
}


segment = {
    'type': 'object',
    'properties': {
        'session_id': {
            'type': 'string',
            'description': 'id for the session',
        },
        'segment_start': {
            'type': ['string', 'null'],
            'format': 'date-time',
            'description': 'start datetime for the segment',
        },
        'segment_end': {
            'type': ['string', 'null'],
            'format': 'date-time',
            'description': 'end datetime for the segment',
        }
    }
}


session = {
    'type': 'object',
    'properties': {
        'session_id': {
            'type': 'string',
            'description': 'id for the session',
        },
        'segments': {
            'type': ['array', 'null'],
            'items': segment
        }
    }
}


participant = {
    'type': 'object',
    'properties': {
        'participant_id': {
            'type': 'string',
            'description': 'id for the participant',
        },
        'participant_name': {
            'type': ['string', 'null'],
            'description': 'name for the participant',
        },
        'sessions': {
            'type': ['array', 'null'],
            'items': session
        }
    }
}


conversation = {
    'type': 'object',
    'properties': {
        'conversation_id': {
            'type': 'string',
            'description': 'id for the conversation',
        },
        'conversation_start': {
            'type': ['string', 'null'],
            'format': 'date-time',
            'description': 'start timestamp for the conversation',
        },
        'conversation_end': {
            'type': ['string', 'null'],
            'format': 'date-time',
            'description': 'end timestamp for the conversation',
        },

        'participants': {
            'type': ['array', 'null'],
            'items': participant
        }
    }
}


user_details_primary_presence = {
    'type': 'object',
    'properties': {
        'start_time': {
            'type': ['string', 'null'],
            'format': 'date-time',
            'description': 'start timestamp for presence indicator',
        },
        'end_time': {
            'type': ['string', 'null'],
            'format': 'date-time',
            'description': 'end timestamp for presence indicator',
        },
        'system_presence': {
            'type': 'string',
            'description': 'presence state'
        }
    }
}

user_details_routing_status = {
    'properties': {
        'start_time': {
            'type': ['string', 'null'],
            'format': 'date-time',
            'description': 'start time for the routing status',
        },
        'end_time': {
            'type': ['string', 'null'],
            'format': 'date-time',
            'description': 'end time for the routing status',
        },
        'routing_status': {
            'type': 'string',
            'description': 'routing state'
        }
    }
}


user_details = {
    'type': 'object',
    'properties': {
        'user_id': {
            'type': 'string',
            'description': 'id for the user',
        },
        'primary_presence': {
            'type': ['array', 'null'],
            'items': user_details_primary_presence
        },
        'routing_status': {
            'type': ['array', 'null'],
            'items': user_details_routing_status
        }
    }
}


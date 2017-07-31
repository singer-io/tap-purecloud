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


user_state = {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'string',
            'description': 'id for the user state',
        },
        'user_id': {
            'type': 'string',
            'description': 'id for the user',
        },
        'start_time': {
            'type': ['string', 'null'],
            'format': 'date-time',
            'description': 'start time',
        },
        'end_time': {
            'type': ['string', 'null'],
            'format': 'date-time',
            'description': 'end time',
        },
        'state': {
            'type': 'string',
            'description': 'state'
        },
        'state_id': {
            'type': ['string', 'null'],
            'description': 'state id'
        },
        'type': {
            'type': 'string',
            'description': 'message type'
        }
    }
}

management_unit = {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'string',
            'description': 'id for the management unit',
        },
        'name': {
            'type': 'string',
            'description': 'name for the management unit',
        }
    }
}

activity_code = {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'string',
            'description': 'id for the activity code',
        },
        'management_unit_id': {
            'type': 'string',
            'description': 'id for the management unit for this activity code',
        },
        'name': {
            'type': 'string',
            'description': 'name for this activity code',
        },
        'category': {
            'type': 'string',
            'description': 'category for this activity code',
        }
    }
}

management_unit_users = {
    'type': 'object',
    'properties': {
        'management_unit_id': {
            'type': 'string',
            'description': 'id for the management unit for this user',
        },
        'user_id': {
            'type': 'string',
            'description': 'id for the user',
        }
    }
}

user_schedule_shifts_activities = {
    'type': 'object',
    'properties': {
        'activity_code_id': {
            'type': 'string',
            'description': 'id for the activity_code',
        }
    }
}

user_schedule_shifts = {
    'type': 'object',
    'properties': {
        'start_date': {
            'type': ['string', 'null'],
            'format': 'date-time',
            'description': 'date for the shift',
        },
        'activities': {
            'type': ['array', 'null'],
            'items': user_schedule_shifts_activities
        }
    }
}

user_schedule = {
    'type': 'object',
    'properties': {
        'user_id': {
            'type': 'string',
            'description': 'id for the user',
        },
        'start_date': {
            'type': ['string', 'null'],
            'format': 'date-time',
            'description': 'date for the sync',
        },
        'shifts': {
            'type': ['array', 'null'],
            'items': user_schedule_shifts
        }
    }
}

presence_label = {
    'type': 'object',
    'properties': {
        'en_US': {
            'type': 'string',
            'description': 'English presence label'
        }
    }
}

presence = {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'string',
            'description': 'presence id',
        },
        'language_labels': presence_label,
        'created_date': {
            'type': ['string', 'null'],
            'format': 'date-time',
            'description': 'presence creation date',
        },
        'modified_date': {
            'type': ['string', 'null'],
            'format': 'date-time',
            'description': 'presence modification date',
        }
    }
}

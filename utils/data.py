new_message = {
    'type': 'new_message',
    'payload': {
        'chat_id': '123e4567-e89b-12d3-a456-426614174000',
        'sender_id': '987e6543-e21b-43d3-a456-426614174000',
        'text': 'Hello, how are you?',
    },
}

create_group = {
    'type': 'create_group',
    'payload': {
        'title': 'new_group',
        'creator_id': '9cecd1c9-02f3-4f4f-9bc8-1526f0da4bdf',
    },
}

add_user_to_group = {
    'type': 'add_user_to_group',
    'payload': {
        'group_id': '17f1115a-ae3a-485e-8a21-3f234d33dc80',
        'user_id': 'c5da617c-3551-4f73-9fc0-d3cb548e8c4f',
    },
}

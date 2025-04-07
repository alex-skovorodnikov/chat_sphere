new_message = {
    'type': 'new_message',
    'payload': {
        'chat_id': 'a91b063c-3fbf-4fea-adcc-c3625ebbd984',
        'sender_id': '9cecd1c9-02f3-4f4f-9bc8-1526f0da4bdf',
        'text': 'Hello, '';drop database'';''ow are you?',
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

create_group_chat = {
    'type': 'create_group_chat',
    'payload': {
        'chat_title': 'group_chat_title1',
        'group_title': 'group_title1',
        'creator_id': '9cecd1c9-02f3-4f4f-9bc8-1526f0da4bdf',
    },
}

create_personal_chat = {
    'type': 'create_personal_chat',
    'payload': {
        'creator_id': '9cecd1c9-02f3-4f4f-9bc8-1526f0da4bdf',
        'other_user_id': 'c5da617c-3551-4f73-9fc0-d3cb548e8c4f',
    },
}

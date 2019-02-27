import mongoengine


class Role(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    role_id = mongoengine.IntField(required=True)
    message_id = mongoengine.IntField(default=None)
    category = mongoengine.StringField(required=True)
    reaction = mongoengine.StringField()

    meta = {
        'db_alias': "core",
        'collection': "roles"
    }

import mongoengine


class Guild(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    guild_id = mongoengine.IntField(required=True)

    welcome_message = mongoengine.StringField(required=True)
    log_channel = mongoengine.IntField(default=None)
    verification_channel = mongoengine.IntField(default=None)
    update_channel = mongoengine.IntField(default=None)
    member_update_channel = mongoengine.IntField(default=None)

    message_saved = mongoengine.IntField(default=0)
    message_edited = mongoengine.IntField(default=0)
    message_deleted = mongoengine.IntField(default=0)
    verified_user = mongoengine.IntField(default=0)
    underaged_user = mongoengine.IntField(default=0)
    retarded_user = mongoengine.IntField(default=0)

    should_show_deleted = mongoengine.BooleanField(default=False)
    should_show_edited = mongoengine.BooleanField(default=False)
    should_show_leaving = mongoengine.BooleanField(default=False)
    should_show_joining = mongoengine.BooleanField(default=False)
    should_welcome_members = mongoengine.BooleanField(default=True)
    should_verify = mongoengine.BooleanField(default=False)
    should_save_messages = mongoengine.BooleanField(default=False)

    password = mongoengine.StringField(default='')

    roles = mongoengine.ListField()
    bans = mongoengine.ListField()

    meta = {
        'db_alias': "core",
        'collection': "guilds"
    }

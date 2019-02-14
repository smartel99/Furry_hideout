USER_IS_UNDERAGED = "User {0.author.name} entered a date less than 18 years ago ({0.content})"
USER_IS_VERIFIED = "You are now verified, please setup your roles in the #get_roles channel."
INPUT_NOT_VALID = "Input is not valid, please enter a '{}'"

WELCOME_MESSAGE = """Welcome to Furry HideOut!

Please check the rule channels (#rules), then follow the steps hidden somewhere in that channel.
If you get kicked after entering your date and think it is by mistake, just rejoin the server!
https://discord.gg/5xqjzdQ
Once you are verified, please use the #get-roles channel to set your basic roles.

Enjoy your stay in the Furry Hideout!"""

GIVEN_VERIFIED_TO_USER = "Given the verified role to user {0.name}. (birthday entered: {1})\n" \
                         "{0.name} joined discord on {0.created_at}"

USER_FILE_INFO = "Username: {0.name}, ID: {0.id}, joined the server: {0.joined_at}, created account: {0.created_at}\n"

USER_NEW_MESSAGE_TO_LOG = "[Created: {0.created_at}][Channel: {0.channel.name}][ID: {0.id}] {0.content}\n"

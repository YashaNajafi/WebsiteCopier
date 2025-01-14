#----------<Library>----------
import random,string
#----------<Functions>----------
def GeneratePassword():
    chars = string.ascii_uppercase + string.digits + string.ascii_lowercase

    Password = 'FastCodeTeam-'.join(random.choices(chars,k=12))

    return Password

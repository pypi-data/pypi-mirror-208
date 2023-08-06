import logging
from fbclient import get, set_config
from fbclient.config import Config

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%m-%d %H:%M')

env_secret = 'fXWjg00OTEa-M_iBCyYiBwFPfdBisjAkiY3ycIMOWw1Q'
event_url = 'http://localhost:5100'
streaming_url = 'ws://localhost:5100'

set_config(Config(env_secret, event_url, streaming_url))
client = get()

if client.initialize:
    flag_key = 'ff-test-bool'
    user_key = 'user-test-1'
    user_name = 'user-test-1'
    user = {'key': user_key, 'name': user_name}
    detail = client.variation_detail(flag_key, user, default=None)
    print(f'flag {flag_key} returns {detail.variation} for user {user_key}, reason: {detail.reason}')

# ensure that the SDK shuts down cleanly and has a chance to deliver events to FeatBit before the program exits
client.stop()

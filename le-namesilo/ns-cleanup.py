#!/usr/bin/env python3

import os
import namesilo
import json

API_KEY = os.environ['NAMESILO_API_KEY']
CERTBOT_AUTH_OUTPUT = os.environ['CERTBOT_AUTH_OUTPUT']

info = json.loads(CERTBOT_AUTH_OUTPUT)
ns = namesilo.NameSilo(API_KEY)
ns.del_record(info['domain'], info['id'])

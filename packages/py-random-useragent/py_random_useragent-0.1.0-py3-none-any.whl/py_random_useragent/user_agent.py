# -*- coding: utf-8 -*-
# @Author: Suvorinov Oleg <olegsuvorinov@me.com>
# @Date:   2023-02-28 10:01:30
# @Last Modified by:   Oleg Suvorinov
# @Last Modified time: 2023-05-15 14:30:18

import os
import random
import logging

import requests
from lxml import html

logger = logging.getLogger(__name__)


class UserAgent(object):
    """docstring for UserAgent"""

    def __init__(self):
        super(UserAgent, self).__init__()

        self.u_agents = []

        self.__get_most_common_user_agents()
        self.__get_from_file()

    def __get_most_common_user_agents(self):
        # From google cache
        url = ("https://webcache.googleusercontent.com/"
               "search?q=cache:FxxmQW9XrRcJ:https://techblog.willshouse.com/"
               "2012/01/03/most-common-user-agents/+&cd=4&hl=en&ct=clnk&gl=us")
        xpath = '//*[@id="post-2229"]/div[2]/textarea[1]'

        try:
            r = requests.get(url)
            r.raise_for_status()
            xml = html.fromstring(r.content)
            elem = xml.xpath(xpath)[0]
        except Exception as e:
            logger.error(e, exec_info=True)
        else:
            cur_dir, _ = os.path.split(__file__)
            ua_file = os.path.join(cur_dir, 'useragents.txt')
            with open(ua_file, 'w') as f:
                f.write(elem.text_content())

    def __get_from_file(self):
        cur_dir, _ = os.path.split(__file__)
        ua_file = os.path.join(cur_dir, 'useragents.txt')
        with open(ua_file) as f:
            for line in f:
                self.u_agents.append(line.strip())

    def get_ua(self):
        return random.choice(self.u_agents)

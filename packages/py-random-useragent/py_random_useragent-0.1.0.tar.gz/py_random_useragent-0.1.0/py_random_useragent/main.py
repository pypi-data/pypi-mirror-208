# -*- coding: utf-8 -*-
# @Author: Oleg Suvorinov
# @Date:   2023-01-17 07:26:45
# @Last Modified by:   Oleg Suvorinov
# @Last Modified time: 2023-05-15 14:30:47

from .user_agent import UserAgent


def main():

    print(UserAgent().get_ua())


if __name__ == '__main__':
    main()

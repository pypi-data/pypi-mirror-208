import datetime
import getopt
import hashlib
import random
import time
import os
import sys
import traceback
from typing import Dict, Tuple, List


def get_text_md5(text) -> str:
    """
    计算字符串md5
    :param text:
    :return:
    """
    # print('md5处理：%s' % text)
    md5 = hashlib.md5(text.encode("utf-8")).hexdigest()
    return md5



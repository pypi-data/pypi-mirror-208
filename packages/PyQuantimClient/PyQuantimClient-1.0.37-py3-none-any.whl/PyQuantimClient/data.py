# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime as dt
from .api import quantim

class time_series(quantim):
    def __init__(self, username, password, secretpool, env="qa"):
        super().__init__(username, password, secretpool, env)

    def get_series(self, tks, ref_curr='Origen', join='outer', verify=False):
        '''
        Get series
        '''
        data = {'tks':list(tks), 'ref_curr':ref_curr, 'join':join}
        resp = self.api_call('get_series', method="post", data=data, verify=verify)
        ts, summ, tks_invalid = pd.DataFrame(resp['ts']).set_index("Date"), pd.DataFrame(resp['summ']), resp['tks_invalid']
        return ts, summ, tks_invalid

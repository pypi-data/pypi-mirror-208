import os


class Config:

    SHOP_URL = os.environ.get('SHOP_URL', 'https://segmenthee.myshoprenter.hu/')
    SCORE_THRESHOLD = float(os.environ.get('SCORE_THRESHOLD', 0.19))
    FRUSTRATION_TOLERANCE = float(os.environ.get('FRUSTRATION_TOLERANCE', 0.5))

    AB_A = int(os.environ.get('AB_A', 1))
    SCORE_REQUESTS = os.environ.get('SCORE_REQUESTS', 'yes')
    STORE_REQUESTS = os.environ.get('STORE_REQUESTS', 'yes')
    
    CD_REFERRER = os.environ.get('CD_REFERRER', 'cd4')
    CD_REDIRECTS = os.environ.get('CD_REDIRECTS', 'cd5')
    CD_NAVIGATION = os.environ.get('CD_NAVIGATION', 'cd6')
    CD_TABTYPE = os.environ.get('CD_TABTYPE', 'cd7')
    CD_TABCOUNT = os.environ.get('CD_TABCOUNT', 'cd8')
    CD_SESSION_ID = os.environ.get('CD_SESSION_ID', 'cd11')

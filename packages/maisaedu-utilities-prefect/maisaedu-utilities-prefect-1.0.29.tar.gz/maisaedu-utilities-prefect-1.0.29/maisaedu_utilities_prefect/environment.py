import os
from maisaedu_utilities_prefect.constants import PRODUCTION, LOCAL


def get_env():
    ## That comparison should be changed in future, depending on variable put in SO environment. Example: os.environ.get('DATAWAREHOUSE_DSN')
    if os.environ.get("DATAWAREHOUSE_DSN") is not None:
        return PRODUCTION
    else:
        return LOCAL

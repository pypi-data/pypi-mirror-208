import datetime
from dhi.platform.base.exceptions import MikeCloudException
from .constants import DATETIMEFORMAT_SECONDS_URL


def sanitize_from_to(from_:datetime.datetime=None, to:datetime.datetime=None):
    #if not (from_ or to):
    #    raise MikeCloudException("At least one of from_ and to parameters must be specified")
    
    if (from_ and to) and  (to < from_):
        raise MikeCloudException("Parameter from_ must be lower than parameter to")

    if from_:
        from_ = datetime.datetime.strftime(from_, DATETIMEFORMAT_SECONDS_URL)
    
    if to:
        to = datetime.datetime.strftime(to, DATETIMEFORMAT_SECONDS_URL)
    
    return (from_, to)
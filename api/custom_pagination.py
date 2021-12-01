from rest_framework.pagination import LimitOffsetPagination


# Used limit
class StandardResultsSetPagination(LimitOffsetPagination):
    default_limit = 2  # default set but can be overridden by client
    limit_query_param = 'limit'  # name of the parameter, once set, this limit_data only works
    offset_query_param = 'next_all_data'

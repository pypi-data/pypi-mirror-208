class EulithAuthException(Exception):
    pass


class EulithRpcException(Exception):
    pass


class EulithUnsafeRequestException(Exception):
    pass


def guard_non_safe_atomic(ew3):
    if ew3.eulith_data.atomic and 'gnosis_address' not in str(ew3.eulith_data.eulith_url):
        raise EulithUnsafeRequestException('calling this method in an atomic '
                                           'transaction without a Safe exposes you to '
                                           'leaving funds in your toolkit contract accidentally')

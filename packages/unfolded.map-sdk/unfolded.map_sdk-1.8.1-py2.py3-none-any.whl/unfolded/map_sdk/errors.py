from traitlets import TraitError


class DataException(TraitError):
    pass


class UnfoldedStudioException(Exception):
    pass


class MapSDKException(Exception):
    pass

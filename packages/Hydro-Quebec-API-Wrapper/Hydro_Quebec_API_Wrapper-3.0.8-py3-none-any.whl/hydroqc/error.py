"""HydroQc Error Module."""


class HydroQcError(Exception):
    """Base HydroQc Error."""


class HydroQcHTTPError(HydroQcError):
    """HTTP HydroQc Error."""


class HydroQcAnnualError(HydroQcError):
    """Annual HydroQc Error."""


class HydroQcCPCPeakError(HydroQcError):
    """CPC peak HydroQc Error."""


class HydroQcDPCPeakError(HydroQcError):
    """DPC peak HydroQc Error."""

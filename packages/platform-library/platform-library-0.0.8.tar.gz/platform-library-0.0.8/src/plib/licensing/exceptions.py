class LicenseAPIError(Exception):
    ...


class LicenseServiceError(LicenseAPIError):
    ...


class LicenseLimitAttribute(LicenseAPIError):
    def __init__(self, attribute: str, limit: int):
        self.attribute = attribute
        self.limit = limit
        super().__init__()

    def __str__(self):
        return f"License attribute '{self.attribute}' limit exceeded. Limit - {self.limit} items."


class LicenseSignatureCorrupted(LicenseServiceError):
    def __str__(self) -> str:
        return f'License service signature was corrupted.'

class Version:
    """
    Lightweight temporary class for version comparison.

    Create at least one instance of Version to compare two semantic versions:

    >>> v = Version('1.5.2')
    >>> v < '4.1.0'
    >>> True

    Args:
        ver (str):
            Semantic version in x.y.z form
    """

    def __init__(self, ver):
        self._version = ver

        self._major, self._minor, self._patch = [int(v) for v in ver.split(".")]

    def _coerce_version(self, other):
        if not isinstance(other, Version):
            other = Version(other)
        return other

    def _compare(self, other):
        if self.major != other.major:
            return -1 if self.major < other.major else 1
        if self.minor != other.minor:
            return -1 if self.minor < other.minor else 1
        if self.patch != other.patch:
            return -1 if self.patch < other.patch else 1
        return 0

    def __eq__(self, other):
        other = self._coerce_version(other)
        return self._compare(other) == 0

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        other = self._coerce_version(other)
        return self._compare(other) < 0

    def __gt__(self, other):
        other = self._coerce_version(other)
        return self._compare(other) > 0

    def __le__(self, other):
        other = self._coerce_version(other)
        return self._compare(other) <= 0

    def __ge__(self, other):
        other = self._coerce_version(other)
        return self._compare(other) >= 0

    def __repr__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    @property
    def major(self):
        return self._major

    @property
    def minor(self):
        return self._minor

    @property
    def patch(self):
        return self._patch

    @property
    def version(self):
        return self._version

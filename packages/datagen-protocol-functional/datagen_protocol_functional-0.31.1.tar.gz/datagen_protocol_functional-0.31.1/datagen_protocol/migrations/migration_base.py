from pydantic import BaseModel


class APIVersion(BaseModel):
    major: int
    minor: int

    @classmethod
    def from_string(cls: "APIVersion", version: str) -> "APIVersion":
        major, minor = version.split(".")
        return cls(major=major, minor=minor)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"

    def __iter__(self) -> iter:
        return iter((self.major, self.minor))

    def __hash__(self) -> int:
        return hash(str(self))

    def __lt__(self, other: "APIVersion"):
        return (self.major, self.minor) < (other.major, other.minor)

    def __le__(self, other: "APIVersion"):
        return (self.major, self.minor) <= (other.major, other.minor)

    def __eq__(self, other: "APIVersion"):
        return (self.major, self.minor) == (other.major, other.minor)

    def __ne__(self, other: "APIVersion"):
        return (self.major, self.minor) != (other.major, other.minor)

    def __ge__(self, other: "APIVersion"):
        return (self.major, self.minor) >= (other.major, other.minor)

    def __gt__(self, other: "APIVersion"):
        return (self.major, self.minor) > (other.major, other.minor)


def schema_change(f):
    f.is_schema_change = True
    return f


class MigrationMeta(type):
    def __new__(mcs, name, bases, attrs):
        if name.startswith("None"):
            return None
        new_attributes = {}
        for attr_name, attr_value in attrs.items():
            if getattr(attr_value, "is_schema_change", False):
                new_attributes[f"_schema_change_{attr_name}"] = attr_value
            else:
                new_attributes[attr_name] = attr_value
        return super(MigrationMeta, mcs).__new__(mcs, name, bases, new_attributes)


class MigrationBase(metaclass=MigrationMeta):
    version: APIVersion
    migration_type: str

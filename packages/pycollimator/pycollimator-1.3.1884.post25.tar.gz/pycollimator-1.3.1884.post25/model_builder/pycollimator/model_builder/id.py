from collections import defaultdict
import hashlib


def _to_uuid(s):
    """Generates something that looks like a valid UUIDv4 from an existing string."""
    # generate the MD5 hash
    hash_object = hashlib.md5(s.encode())
    hash_string = hash_object.hexdigest()

    # convert the hash to a UUIDv4-like format
    # note: we removed characters 12 and 16
    uuid_string = "{}-{}-4{}-8{}-{}".format(
        hash_string[:8],
        hash_string[8:12],
        hash_string[13:16],
        hash_string[17:20],
        hash_string[20:],
    ).lower()

    return uuid_string


class Id:
    uuid_mapping = {}

    @classmethod
    def set_uuid_mapping(cls, uuid_mapping):
        Id.uuid_mapping = uuid_mapping

    def with_id(klass):
        class Wrapped(klass):
            _id_counts = defaultdict(int)

            def __init__(self, *args, id=None, uuid=None, **kwargs):
                self._id = id
                if uuid is not None:
                    Id.uuid_mapping[self.id] = uuid
                if not isinstance(self, tuple):
                    super().__init__(*args, **kwargs)

            @classmethod
            def _new_id(_, klass):
                name = klass.__class__.__name__
                idx = Wrapped._id_counts[name]
                Wrapped._id_counts[name] += 1
                return f"{name}_{idx}"

            @property
            def id(self):
                if self._id is None:
                    self._id = Wrapped._new_id(self)
                return self._id

            @property
            def uuid(self):
                if self.id not in Id.uuid_mapping:
                    Id.uuid_mapping[self.id] = _to_uuid(self.id)
                return Id.uuid_mapping[self.id]

        Wrapped.__qualname__ = klass.__qualname__
        Wrapped.__name__ = klass.__name__

        return Wrapped

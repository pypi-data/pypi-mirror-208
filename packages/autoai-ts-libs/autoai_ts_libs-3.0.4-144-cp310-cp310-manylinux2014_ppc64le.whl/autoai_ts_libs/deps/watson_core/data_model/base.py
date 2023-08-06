# *****************************************************************#
# (C) Copyright IBM Corporation 2021.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
# *****************************************************************#
"""Base classes and functionality for all data structures.
"""

# metaclass-generated field members cannot be detected by pylint
# pylint: disable=no-member

import base64
from typing import Optional, Type
import importlib
import json

from google.protobuf import json_format

from autoai_ts_libs.deps.watson_core.toolkit import alog
from ..toolkit.errors import error_handler

from . import enums
from . import protobufs


log = alog.use_channel("DATAM")
error = error_handler.get(log)


class _DataBaseMetaClass(type):
    """Meta class for all structures in the data model."""

    # store a registry of all classes that use this metaclass, i.e.,
    # all classes that extend DataBase.  This is used for constructing new
    # instances by name without having to introspect all modules in data_model.
    class_registry = {}
    proto_registry = {}

    # This sentinel value is used to determine whether a given attribute is
    # present on a class without doing `getattr` twice in the case where the
    # attribute does exist.
    _MISSING_ATTRIBUTE = "missing attribute"

    def __new__(cls, name, bases, attrs):
        """When constructing a new data model class, we set the 'fields' class variable from the
        protobufs descriptor and then set the '__slots__' magic class attribute to fields.  This
        provides two benefits: (a) performance is improved since the classes only need to know
        about these attributes (b) it helps to enforce that all member variables in these classes
        are described in the protobufs.

        Note:  If you want to add a variable for internal use that is not described in the
        protobufs, it can be named in the tuple class variable _private_slots and will
        automatically be added to __slots__.
        """
        # get all fields in protobuf with same name as class,
        # except for DataBase, which has no matching protobuf
        fields = ()

        # protobuf fields can be divided into these categories, which are used to automatically
        # determine appropriate behavior in a number of methods
        fields_enum_map = {}
        fields_enum_rev = {}
        _fields_message = ()
        _fields_message_repeated = ()
        _fields_enum = ()
        _fields_enum_repeated = ()
        _fields_primitive = ()
        _fields_primitive_repeated = ()
        _fields_map = ()
        proto_class = None
        if name != "DataBase":

            # Look for the proto class. There are two places it could be:
            #
            # 1. The "protobufs" module in watson_core (injected via
            #   import_protobufs)
            # 2. The "protobufs" module in the derived library.
            #
            # The second option is primarily needed when using import_tracker on
            # a watson_core derived library. The side-effects of
            # import_protobufs break the import_tracker mechanism, so this
            # fallback avoids the reliance on side-effects.
            proto_class = attrs.get(
                "_proto_class", _DataBaseMetaClass.proto_registry.get(name)
            )
            if proto_class is None:
                parent_mod = attrs.get("__module__")
                log.debug3(
                    "No proto class found in central registry for [%s]. Looking in [%s]",
                    name,
                    parent_mod,
                )
                if parent_mod is not None:
                    parent_mod_protos_name = ".".join(
                        [parent_mod.rpartition(".")[0], "protobufs"]
                    )
                    try:
                        parent_mod_protos = importlib.import_module(
                            parent_mod_protos_name
                        )
                        proto_class = getattr(parent_mod_protos, name, None)
                    except ImportError:
                        log.debug3(
                            "Could not find a protobufs module in [%s]: %s",
                            parent_mod,
                            parent_mod_protos_name,
                        )
                        pass
            if proto_class is None:
                raise AttributeError(
                    f"Failed to find {name} in watson_core.data_model.protobufs or derived library protobufs"
                )

            # all fields
            fields += tuple(proto_class.DESCRIPTOR.fields_by_name)

            # all fields of type map
            _fields_map = tuple(
                field.name
                for field in proto_class.DESCRIPTOR.fields
                if field.message_type and field.message_type.GetOptions().map_entry
            )

            # map from all enum fields to their enum classes
            # note: enums are also primitives, these overlap
            fields_enum_map = {
                field.name: getattr(enums, field.enum_type.name)
                for field in proto_class.DESCRIPTOR.fields
                if field.enum_type is not None
            }

            fields_enum_rev = {
                field.name: getattr(enums, field.enum_type.name + "Rev")
                for field in proto_class.DESCRIPTOR.fields
                if field.enum_type is not None
            }

            # all repeated fields
            fields_repeated = tuple(
                field.name
                for field in proto_class.DESCRIPTOR.fields
                if field.label == field.LABEL_REPEATED
            )

            # all messages, repeated or not
            _fields_message_all = tuple(
                field.name
                for field in proto_class.DESCRIPTOR.fields
                if field.type == field.TYPE_MESSAGE
            )

            # all enums, repeated or not
            _fields_enum_all = tuple(
                field.name
                for field in proto_class.DESCRIPTOR.fields
                if field.enum_type is not None
            )

            # all primitives, repeated or not
            _fields_primitive_all = (
                frozenset(fields)
                .difference(_fields_map)
                .difference(_fields_message_all)
                .difference(_fields_enum_all)
            )

            # messages that are not repeated
            _fields_message = frozenset(_fields_message_all).difference(fields_repeated)

            # messages that are repeated
            _fields_message_repeated = frozenset(fields_repeated).intersection(
                _fields_message_all
            )

            _fields_enum = frozenset(_fields_enum_all).difference(fields_repeated)

            _fields_enum_repeated = frozenset(_fields_enum_all).intersection(
                fields_repeated
            )

            # primitives that are not repeated
            _fields_primitive = frozenset(_fields_primitive_all).difference(
                fields_repeated
            )

            # primitives that are repeated
            _fields_primitive_repeated = frozenset(fields_repeated).intersection(
                _fields_primitive_all
            )

        # look if any private slots are declared as class variables
        private_slots = attrs.setdefault("_private_slots", ())

        # class slots are fields + private slots, this prevents other
        # member attributes from being set and also improves performance
        attrs["__slots__"] = tuple(
            [f"_{field}" for field in fields] + list(private_slots) + ["_backend"]
        )

        # add properties that use the underlying backend
        for field in fields:
            attrs[field] = cls._make_property_getter(field)

        # If there is not already an __init__ function defined, make one
        current_init = attrs.get("__init__")
        if current_init is None or current_init is DataBase.__init__:
            attrs["__init__"] = cls._make_init(fields)

        # set fields class variable for reference
        # these are valuable for validating attributes and
        # also for recursively converting to and from protobufs
        attrs["fields"] = fields
        attrs["fields_enum_map"] = fields_enum_map
        attrs["fields_enum_rev"] = fields_enum_rev
        attrs["_fields_message"] = _fields_message
        attrs["_fields_message_repeated"] = _fields_message_repeated
        attrs["_fields_enum"] = _fields_enum
        attrs["_fields_enum_repeated"] = _fields_enum_repeated
        attrs["_fields_primitive"] = _fields_primitive
        attrs["_fields_primitive_repeated"] = _fields_primitive_repeated
        attrs["_fields_map"] = _fields_map
        attrs["_proto_class"] = proto_class
        instance = super().__new__(cls, name, bases, attrs)

        # Update the global class and proto registries
        if name != "DataBase":
            cls.class_registry[name] = instance
            cls.proto_registry[name] = proto_class

        # Return the constructed class instance
        return instance

    @classmethod
    def _make_property_getter(cls, field):
        """This helper creates an @property attribute getter for the given field

        NOTE: This needs to live as a standalone funciton in order for the given
            field name to be properly bound to the closure for the attrs
        """
        private_name = f"_{field}"

        @property
        def _property_getter(self):
            f"""Access the {field} attribute"""
            # Check to see if the private name is defined and just return it if
            # it is
            current = getattr(self, private_name, cls._MISSING_ATTRIBUTE)
            if current is not cls._MISSING_ATTRIBUTE:
                return current

            # If not currently set, delegate to the backend
            attr_val = self._backend.get_attribute(self.__class__, field)

            # If the backend says that this attribute should be cached, set it
            # as an attribute on the class
            if self._backend.cache_attribute(field, attr_val):
                setattr(self, private_name, attr_val)

            # Return the value found by the backend
            return attr_val

        return _property_getter

    @staticmethod
    def _make_init(fields):
        """This helper creates an __init__ function for a class which has the
        arguments for all the fields and just sets them as instance attributes.
        """

        def __init__(self, *args, **kwargs):
            """Construct with arguments for each field on the object

            Args:
                {}
            """.format(
                "\n    ".join(fields)
            )

            used_fields = []
            field_nums = {i: field for i, field in enumerate(fields)}
            if len(args) + len(kwargs) > len(fields):
                error(
                    "<COR71444420E>",
                    ValueError(f"Too many arguments given. Args are: {fields}"),
                )
            for i, arg in enumerate(args):
                field = field_nums[i]
                used_fields.append(field)
                setattr(self, field, arg)
            for field_name, field_val in kwargs.items():
                if field_name not in fields:
                    error("<COR71444421E>", ValueError(f"Unknown field {field_name}"))
                elif field_name in used_fields:
                    error(
                        "<COR71444422E>",
                        ValueError(f"Got multiple values for field {field_name}"),
                    )
                setattr(self, field_name, field_val)
                used_fields.append(field_name)

            # Default all unspecified fields to None
            for field_name in fields:
                if field_name not in used_fields:
                    setattr(self, field_name, None)

        return __init__


class DataBase(metaclass=_DataBaseMetaClass):
    """Base class for all structures in the data model.

    Notes:
        All leaves in the hierarchy of derived classes should have a corresponding protobuf class
        defined in the interface definitions.  If not, an exception will be thrown at runtime.
    """

    def __setattr__(self, name, val):
        """If attempting to set one of the named fields, instead set the
        "private" version of the attribute.
        """
        if name in self.__class__.fields:
            super().__setattr__(f"_{name}", val)
        else:
            super().__setattr__(name, val)

    @classmethod
    def get_field_message_type(cls, field_name: str) -> Optional[Type["DataBase"]]:
        """Get the data model class for the given field if the field is a
        message or a repeated message

        Args:
            field_name:  str
                Field name to check (AttributeError raised if name is invalid)

        Returns:
            data_model_type:  Type[DataBase]
                The data model class type for the given field
        """
        if field_name not in cls.fields:
            raise AttributeError(f"Invalid field {field_name}")
        if (
            field_name in cls._fields_message
            or field_name in cls._fields_message_repeated
        ):
            return DataBase.class_registry[
                cls._proto_class.DESCRIPTOR.fields_by_name[field_name].message_type.name
            ]
        return None

    @classmethod
    def from_backend(cls, backend):
        instance = cls.__new__(cls)
        setattr(instance, "_backend", backend)
        return instance

    @classmethod
    def from_binary_buffer(cls, buf):
        """Builds the data model object out of the binary string

        Args:
            buf: The binary buffer containing a serialized protobuf message

        Returns:
            A data model object instantiated from the protobuf message deserialized out of `buf`
        """
        proto_class = _DataBaseMetaClass.proto_registry.get(cls.__name__)
        if proto_class is None:
            error(
                "<COR71444427E>",
                AttributeError(
                    "protobuf not found for class `{}`".format(cls.__name__)
                ),
            )

        proto_message = proto_class()
        proto_message.ParseFromString(buf)

        return cls.from_proto(proto_message)

    @classmethod
    def from_proto(cls, proto):
        """Build a DataBase from protobuf.

        Args:
            proto:
                A protocol buffer to serialize from.

        Returns:
            protobuf
                A DataBase object.
        """
        if cls.__name__ != proto.DESCRIPTOR.name:
            error(
                "<COR71783894E>",
                ValueError(
                    "class name `{}` does not match protobuf name `{}`".format(
                        cls.__name__, proto.DESCRIPTOR.name
                    )
                ),
            )

        kwargs = {}
        for field in cls.fields:
            try:
                proto_attr = getattr(proto, field)
            except AttributeError:
                error(
                    "<COR71783905E>",
                    AttributeError(
                        "protobuf `{}` does not have field `{}`".format(
                            proto.DESCRIPTOR.name, field
                        )
                    ),
                )

            if field in cls._fields_primitive or field in cls._fields_enum:
                kwargs[field] = proto_attr

            elif (
                field in cls._fields_primitive_repeated
                or field in cls._fields_enum_repeated
            ):
                kwargs[field] = list(proto_attr)

            elif field in cls._fields_map:
                kwargs[field] = {}
                for key, value in proto_attr.items():
                    # Similar to filling; if our value is a non-primitive, i.e., a message,
                    # we need to look up the data model class attached to it.
                    if hasattr(value, "DESCRIPTOR"):
                        _, contained_class = cls._get_class_for_proto(value)
                        kwargs[field][key] = contained_class.from_proto(value)
                    # If it's not a message, the value can be left alone, i.e., it's a primitive
                    else:
                        kwargs[field][key] = value

            elif field in cls._fields_message:
                if proto.HasField(field):
                    _, contained_class = cls._get_class_for_proto(proto_attr)
                    contained_obj = contained_class.from_proto(proto_attr)
                    kwargs[field] = contained_obj

            elif field in cls._fields_message_repeated:

                def gen_repeated_objects():
                    class_name = None
                    contained_class = None
                    for item in proto_attr:
                        if contained_class is None:
                            class_name, contained_class = cls._get_class_for_proto(
                                item, class_name
                            )
                        yield contained_class.from_proto(item)

                kwargs[field] = list(gen_repeated_objects())

            else:
                error(
                    "<COR71783815E>",
                    AttributeError(
                        "field `{}` is not a protobuf primitive, message, map or "
                        "repeated".format(field)
                    ),
                )

        return cls(**kwargs)

    @classmethod
    def from_json(cls, json_str):
        """Build a DataBase from a given JSON string. Use google's protobuf.json_format for
        deserialization

        Args:
            json_str: str or dict
                A stringified JSON specification/dict of the data_model

        Returns:
            watson_core.data_model.DataBase
                A DataBase object.
        """
        # Get protobuf class required for parsing
        proto_class = getattr(protobufs, cls.__name__)

        error.type_check("<COR91037250E>", str, dict, json_str=json_str)
        if isinstance(json_str, dict):
            # Convert dict object to a JSON string
            json_str = json.dumps(json_str)

        try:
            # Parse given JSON into google.protobuf.pyext.cpp_message.GeneratedProtocolMessageType
            parsed_proto = json_format.Parse(
                json_str, proto_class(), ignore_unknown_fields=False
            )

            # Use from_proto to return the DataBase object from the parsed proto
            return cls.from_proto(parsed_proto)

        except json_format.ParseError as ex:
            error("<COR90619980E>", ValueError(ex))

    def to_proto(self):
        """Return a new protobuf populated with the information in this data structure."""
        # get the name of the protobuf class
        proto_class = _DataBaseMetaClass.proto_registry.get(self.__class__.__name__)
        if proto_class is None:
            error(
                "<COR71783827E>",
                AttributeError(
                    "protobuf not found for class `{}`".format(self.__class__.__name__)
                ),
            )

        # create the protobuf and call fill_proto to populate it
        return self.fill_proto(proto_class())

    def to_binary_buffer(self):
        """Returns a binary buffer with a serialized protobuf message of this data model"""
        return self.to_proto().SerializeToString()

    def fill_proto(self, proto):
        """Populate a protobuf with the values from this data model object.

        Args:
            proto:
                A protocol buffer to be populated.

        Returns:
            protobuf
                The filled protobuf.

        Notes:
            The protobuf is filled in place, so the argument and the return
            value are the same at the end of this call.
        """
        for field in self.fields:
            try:
                attr = getattr(self, field)

            except AttributeError:
                error(
                    "<COR71783840E>",
                    AttributeError(
                        "class `{}` has no attribute `{}` but it is in the protobuf".format(
                            self.__class__.__name__, field
                        )
                    ),
                )

            if attr is None:
                continue

            if field in self._fields_primitive or field in self._fields_enum:
                setattr(proto, field, attr)

            elif field in self._fields_map:
                subproto = getattr(proto, field)
                for key, value in attr.items():
                    # If our values aren't primitives, the subproto will have a DESCRIPTOR;
                    # in this case we need to fill down recursively, i.e., this is a
                    # protobuf message map container
                    if hasattr(subproto[key], "DESCRIPTOR"):
                        value.fill_proto(subproto[key])
                    # Otherwise we have a protobuf scala map container, and we can set the
                    # primitive value like a normal dictionary.
                    else:
                        subproto[key] = value
            elif (
                field in self._fields_primitive_repeated
                or field in self._fields_enum_repeated
            ):
                subproto = getattr(proto, field)
                subproto.extend(attr)

            elif field in self._fields_message:
                subproto = getattr(proto, field)
                attr.fill_proto(subproto)

            elif field in self._fields_message_repeated:
                subproto = getattr(proto, field)
                for item in attr:
                    item.fill_proto(subproto.add())

            else:
                error(
                    "<COR71783852E>",
                    AttributeError(
                        "field `{}` is not a protobuf primitive, message or repeated".format(
                            field
                        )
                    ),
                )

        return proto

    def to_dict(self):
        """Convert to a dictionary representation."""
        return {field: self._field_to_dict_element(field) for field in self.fields}

    def to_json(self, **kwargs):
        """Convert to a json representation."""

        def _default_serialization_overrides(obj):
            """Default handler for nonserializable objects; currently this only handles bytes."""
            if isinstance(obj, bytes):
                return base64.encodebytes(obj).decode("utf-8")
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        if "default" not in kwargs:
            kwargs["default"] = _default_serialization_overrides
        return json.dumps(self.to_dict(), **kwargs)

    def __repr__(self):
        """Human-friendly representation."""
        return self.to_json(indent=2, ensure_ascii=False)

    def _field_to_dict_element(self, field):
        """Convert field into a representation that can be placed into a dictionary.  Recursively
        calls to_dict on other data model objects.
        """
        try:
            attr = getattr(self, field)

        except AttributeError:
            error(
                "<COR71783864E>",
                AttributeError(
                    "class `{}` has no attribute `{}` but it is in the protobuf".format(
                        self.__class__.__name__, field
                    )
                ),
            )

        # if field is None, assume it's unset and just return None
        if attr is None:
            return None

        if field in self._fields_enum:
            # if field is an enum, do the reverse lookup from int -> str
            enum_rev = self.fields_enum_rev.get(field)
            if enum_rev is not None:
                return enum_rev[attr]

        if field in self._fields_enum_repeated:
            # if field is an enum, do the reverse lookup from int -> str
            enum_rev = self.fields_enum_rev.get(field)
            if enum_rev is not None:
                return [enum_rev[item] for item in attr]

        # if field is a primitive, just return it to be placed in dict
        if field in self._fields_primitive or field in self._fields_primitive_repeated:
            return attr

        def _recursive_to_dict(_attr):
            if isinstance(_attr, dict):
                return {key: _recursive_to_dict(value) for key, value in _attr.items()}
            if isinstance(_attr, list):
                return [_recursive_to_dict(listitem) for listitem in _attr]
            elif isinstance(_attr, DataBase):
                return _attr.to_dict()
            else:
                return _attr

        # If field is an object in out data model/map/list call to_dict recursively on each element
        if (
            field in self._fields_map
            or field in self._fields_message
            or field in self._fields_message_repeated
        ):
            return _recursive_to_dict(attr)

        # fallback to the string representation
        return str(attr)

    @staticmethod
    def _get_class_for_proto(proto, class_name=None):
        """Return the string class name and actual class of the data model wrapper for a
        given protobuf.
        """
        if class_name is None:
            class_name = proto.DESCRIPTOR.name

        cls = DataBase.class_registry.get(class_name, None)
        if cls is None:
            error(
                "<COR71783879E>",
                AttributeError(
                    "no data model class found in registry for protobuf named `{}`".format(
                        class_name
                    )
                ),
            )

        return class_name, cls

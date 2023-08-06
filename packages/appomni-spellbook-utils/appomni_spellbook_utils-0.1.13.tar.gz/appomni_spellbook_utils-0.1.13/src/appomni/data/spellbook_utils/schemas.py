import json
from enum import unique, Enum
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Type

import cattrs
import yaml
from attr import Attribute
from attrs import define, field
from glom import assign, glom, PathAccessError

import appomni.data.spellbook_utils.globals

valueset_converter = cattrs.Converter(prefer_attrib_converters=True)


def allowed_converter(
    value: Optional[List[Union[str, Dict]]]
) -> List["AllowedFieldValues"] | None:
    if value is None:
        return value

    assert type(value) is list
    return_list = []
    for item in value:
        if type(item) == str:
            return_list.append(AllowedFieldValues(name=item))
        elif type(item) == dict:
            return_list.append(AllowedFieldValues(**item))
        else:
            raise ValueError(f"{item} is of type {type(item)}; only support str and dict.")
    return return_list


@unique
class FieldType(Enum):
    OBJECT = ("object", "object", "Dict[str, Any]")
    STRING = ("string", "string", "str")
    INTEGER = ("integer", "integer", "int")
    FLOAT = ("float", "number", "Decimal")
    ARRAY = ("array", "array", "List")
    DATETIME = ("datetime", "string", "datetime")
    UUID = ("uuid", "string", "UUID")
    ULID = ("ulid", "string", "ULID")
    LAT_LON = ("lat_lon", "object", "Dict[str, Decimal]")
    IP_ADDRESS = ("ip_address", "string", "_BaseAddress")
    BOOL = ("bool", "boolean", "bool")

    def __new__(
        cls: Type["FieldType"], constant: str, jsonschema_type: str, py_type: str
    ) -> "FieldType":
        obj = object.__new__(cls)
        obj._value_ = constant
        obj.jsonschema_type = jsonschema_type
        obj.py_type = py_type
        return obj

    def format_value(self, value: Any) -> Any:
        match self:
            case FieldType.OBJECT:
                return json.loads(value)
            case FieldType.STRING:
                return str(value)
            case FieldType.INTEGER:
                return int(value)
            case FieldType.FLOAT:
                return float(value)
            case FieldType.ARRAY:
                return list(value)
            case FieldType.DATETIME:
                return str(value)
            case FieldType.UUID:
                return str(value)
            case FieldType.ULID:
                return str(value)
            case FieldType.LAT_LON:
                return json.loads(value)
            case FieldType.IP_ADDRESS:
                return str(value)
            case FieldType.BOOL:
                return bool(value)


@define
class AllowedFieldValues:
    value: str | int = field()
    description: str = field(default="")


@define
class FieldsetField:
    name: str = field()
    type: FieldType = field()
    example: str = field()
    item_types: List[FieldType] | None = field(default=None)
    normalization: List[Dict[str, str]] | None = field(default=None)
    allowed_values: List[AllowedFieldValues] | None = field(
        default=None, converter=allowed_converter
    )
    import_allowed_values: str | None = field(default=None)
    description: str = field(default="")
    supports_detection: bool = field(default=True)
    required: bool = field(default=False)
    _source_path: Path = field(default=None)

    @type.validator
    def _validate_type(self, attribute: Attribute, value: Any):
        if not isinstance(value, FieldType):
            raise ValueError("type must be a FieldType")

        if value == FieldType.ARRAY:
            if self.item_types is None:
                raise ValueError("item_types must be set if type is ARRAY")

    def set_source_path(self, path: Path):
        self._source_path = path

    @property
    def formatted_example(self) -> Any:
        if self.type == FieldType.ARRAY:
            # For purposes here; we're taking the first defined item_type for the array to serve as the type for all
            # elements in the array. Will need to figure out a different strategy if we want mixed type array examples.
            example_type = self.item_types[0]
            return [example_type.format_value(x) for x in self.example.split(",")]
        return self.type.format_value(self.example)

    @property
    def all_allowed_values(self) -> List[AllowedFieldValues]:
        merged_list = []
        if self.allowed_values:
            merged_list.extend(self.allowed_values)

        if self.import_allowed_values is not None:
            if self._source_path:
                map_path = Path(self._source_path).joinpath(self.import_allowed_values)
            else:
                map_path = Path(appomni.data.spellbook_utils.globals.SCHEMA_WORKING_DIR).joinpath(
                    self.import_allowed_values
                )
            with map_path.open("r") as values_in:
                values_doc = yaml.safe_load(values_in)
                for valueset in values_doc:
                    vs_instance = valueset_converter.structure(valueset, ValueSet)
                    merged_list.extend(vs_instance.values_map)

        return merged_list

    @property
    def defined_allowed_values(self) -> bool:
        return self.allowed_values is not None or self.import_allowed_values is not None


@define
class FieldsetExpected:
    at: str = field()
    expected_as: str | None = field(default=None)

    # TODO: Maybe? Can we somehow reference the Fieldset name automatically; and turn this into a property instead of
    #  passing a default?
    def as_value(self, default) -> str:
        if self.expected_as is None:
            return default
        else:
            return self.expected_as

    def full_dotted_path(self, default) -> str:
        return f"{self.at}.{self.as_value(default)}"


@define
class FieldsetReusable:
    top_level: bool = field(default=True)
    expected: List[FieldsetExpected] = field(factory=list)


@define
class Fieldset:
    name: str = field()
    title: str = field()
    reusable: FieldsetReusable = field(factory=FieldsetReusable)
    description: str = field(default="")
    root: bool = field(default=False)
    fields: List[FieldsetField] = field(factory=list)

    def get_fields_dict(self) -> Dict:
        output_dict = {}
        for fld in self.fields:
            _ = assign(output_dict, fld.name, fld.formatted_example, missing=dict)
        return output_dict

    def set_source_path(self, path: Path):
        for f in self.fields:
            f.set_source_path(path)

    def build_jsonschema(self) -> Dict:
        schema_dict = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }
        for fld in self.fields:
            prop_dict = {
                "description": fld.description,
                "type": fld.type.jsonschema_type,
            }
            if fld.type == FieldType.ARRAY:
                prop_dict["items"] = {"type": [x.jsonschema_type for x in fld.item_types]}
                if fld.defined_allowed_values:
                    prop_dict["items"]["enum"] = [av.value for av in fld.all_allowed_values]
            else:
                if fld.defined_allowed_values:
                    prop_dict["enum"] = [av.value for av in fld.all_allowed_values]

            dotted_name = fld.name.split(".")
            base_field_name = dotted_name[len(dotted_name) - 1]
            if len(dotted_name) > 1:
                base_prop_dict = {
                    "type": "object",
                    "required": [],
                    "additionalProperties": False,
                }

                for idx, path_name in enumerate(dotted_name):
                    update_required = False
                    path = f"properties.{'.properties.'.join(dotted_name[:idx+1])}"
                    if idx != len(dotted_name) - 1:
                        if idx == len(dotted_name) - 2 and fld.required:
                            update_required = True
                        try:
                            glom(schema_dict, path)
                        except PathAccessError:
                            if update_required:
                                base_prop_dict["required"].append(base_field_name)
                            _ = assign(schema_dict, path, base_prop_dict, dict)
                        else:
                            if update_required:
                                required_path = f"{path}.required"
                                required_values = glom(schema_dict, required_path)
                                required_values.append(base_field_name)
                                _ = assign(schema_dict, required_path, required_values)

                            continue
                    else:
                        _ = assign(schema_dict, path, prop_dict, dict)

            else:
                if fld.required:
                    schema_dict["required"].append(fld.name)
                _ = assign(schema_dict, f"properties.{fld.name}", prop_dict)

        return schema_dict


@define
class ValueSet:
    values_map: List[AllowedFieldValues] = field(converter=allowed_converter)

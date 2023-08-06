import cattrs

from appomni.data.spellbook_utils.schemas import Fieldset

schema_converter = cattrs.Converter(prefer_attrib_converters=True)

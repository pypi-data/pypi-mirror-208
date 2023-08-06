# Welcome to Kirzner's Serializer!
## This module supports two formats: *json* and *xml*
### Each serializer contains:
* `dump(obj, filepath)` - serialize `obj` into the file with provided `filepath`
* `dumps(obj)` - serialize `obj` and returns string result
* `load(obj, filepath)` - return the result of deserialization content from the file with provided `filepath`
* `loads(obj, s)` - return the result of deserialization content from the provided string `s`
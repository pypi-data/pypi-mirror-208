# CleanChausie

CleanChausie is a data validation and transformation library for Python. It is a successor to CleanCat.

Check out the [docs](https://closeio.github.io/cleanchausie/)!

*Interested in working on projects like this? [`Close`](https://close.com) is looking for [great engineers](https://jobs.close.com) to join our team.*

Key features:

- Operate on/with type-checked objects that have good IDE/autocomplete support
- Annotation-based declarations for simple fields
- Composable/reusable fields and field validation logic
- Support (but not require) passing around a context (to avoid global state)
  - Context pattern is compatible with explicit sqlalchemy-based session management. i.e. pass in a session when validating
- Cleanly support intra-schema field dependencies (i.e. one field can depend on the validated value of another)
- Explicit nullability/omission parameters
- Errors returned for multiple fields at a time, with field attribution

## CleanChausie by example

This is a short example of how a schema might be used to support a flask 
endpoint. More detailed examples can be found in the
[docs](https://closeio.github.io/cleanchausie/).

```python
from typing import List
from cleanchausie import (
  clean, ListField, URLField, EmailField, field, ValidationError, Schema
)
from flask import app, request, jsonify

class JobApplication(Schema):
  first_name: str
  last_name: str
  email: str = field(EmailField())
  urls: List[str] = field(ListField(URLField(default_scheme='http://')))

@app.route('/job_application', methods=['POST'])
def test_view():
  result = clean(JobApplication, request.json)
  if isinstance(result, ValidationError):
    return jsonify(result.serialize()), 400

  # Now "result" has the validated data, in the form of a `JobApplication` instance.
  assert isinstance(result, JobApplication)
  name = f'{result.first_name} {result.last_name}'
```

## Release process

- Make sure to thoroughly review and test the code changes.
- Prepare for a new release
  - Update the package version within `cleanchausie/__init__.py`.
  - Add a changelog entry for the new version.
  - Merge to master
- Dispatch a new "build and release" workflow action within the github actions tab.

The resulting workflow will build and publish the new version to PyPi.

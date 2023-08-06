# djungle-rulesengine-client
A client to Djungle Studio rulesengine API


## Tests
This project uses `tox` to run the test suite:
simply run the command `tox` in the root of the repository.

## Release
This project uses `tox` to release a version to PyPI.
Run `tox -e release -- <env>`, where `<env>` is an index identifier in
your `~/.pypirc` file.

Alternatively, push a tag to the `main` branch to make a release
using GitHub Actions.

## Usage examples
```python
from rulesengine.async_client import AsyncEngineClient
from rulesengine.client import EngineClient

engine = EngineClient(base_url="https://example.com", token="abcde")

# To push an action to the engine:
engine.push_action(subject_id="sys-1", action="my-action", payload={"key": "value"})

# To get a pluggable prop from the engine
prop_value = engine.get_pluggable_props(subject_id="sys-1", props="my-prop")

# To make a "direct" call to the engine
return_value = engine.direct_post(
    subject_id="sys-1", path="/my/path/", params={"key": "value"}, data={"my": "payload"}
)

# To push an action to the engine (async client):
async_engine = AsyncEngineClient(base_url="https://example.com", token="abcde")

await async_engine.push_action(subject_id="sys-1", action="my-action", payload={"key": "value"})
```

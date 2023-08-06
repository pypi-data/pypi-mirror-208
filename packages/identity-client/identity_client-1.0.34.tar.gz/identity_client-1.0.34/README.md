# identity-client
Client lib for the identity service

## Creating a new release

Update the version in pyproject.toml and create a new tag with that version number and push it,
this will trigger the release.yml GitHub Action.

```bash
git push origin <tag_name>
```
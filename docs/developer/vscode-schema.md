# VS Code and the summary schema

Not a format note: this is about working with the files `tools/mine_saves.py` writes.

Each `tf3-save-summary.json` starts with a `$schema` link to the schema on GitHub (`tools/schema/tf3-save-summary.v<N>.schema.json` on `main`). VS Code only downloads schemas from locations it trusts, and that one is not on its list. The editor shows "Unable to load schema ... is untrusted" on the first line. The file is fine; only the editor hints (hover text, completion, validation) are missing.

## Fix: map the schema to the local copy

Create `.vscode/settings.json` in the repo root (the folder is gitignored, so this stays on your machine):

```json
{
  "json.schemas": [
    {
      "fileMatch": ["**/tf3-save-summary.json"],
      "url": "./tools/schema/tf3-save-summary.v2.schema.json"
    }
  ]
}
```

- Works offline and needs no trust prompt.
- Every summary file has the same name, so a mapping can only pick one version. Point it at the newest `schema_version`. Summaries of an older version will show false errors; rebuild them with `mine_saves.py` or add a mapping for that case.
- The `$schema` line inside each file still holds the remote URL, so the warning may stay on that line. It does no harm. To clear it, use the Quick Fix in the hover (Ctrl+.) to trust the location, or add this to your user settings:

```json
"json.schemaDownload.trustedDomains": {
  "https://raw.githubusercontent.com/WuphonsReach/tf3-save-format/": true
}
```

Do not change the `$schema` URL the tool writes to suit one editor: summaries are shared outside the repo, and the URL is the schema's stable public address (see `SCHEMA_URL` in `tools/mine_saves.py`).

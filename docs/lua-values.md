# Lua values

Used by the header's info table and settings, and by script states. Checked on 604.

A value is a u32 tag followed by its payload:

| Tag | Type | Payload |
|---|---|---|
| 0 | nil | nothing |
| 1 | boolean | u8 |
| 2 | number | f64 |
| 3 | string | `str` |
| 4 | table | u8 flag. 0 means a nil table and nothing follows. 1 is followed by a u32 pair count, then that many key value, value value pairs |

Keys are values too, so a key can be a number or a string. Pairs appear in sorted order.

## Finding a known table

To find a named entry inside a script state, search for its key encoded as a string value: `03 00 00 00`, the u32 length, then the bytes. For `townStates`:

```
03 00 00 00  0a 00 00 00  74 6f 77 6e 53 74 61 74 65 73
```

The table value follows directly. Check that it parses before trusting the hit, since the same bytes can appear elsewhere.

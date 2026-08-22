# Fonts

Both files are the **latin subset**, variable-weight, downloaded from Google
Fonts and self-hosted so the site makes no third-party requests.

`source-serif.woff2` has additionally had its `opsz` (optical size) axis pinned
at 24 with `fontTools.varLib.instancer`, leaving only `wght` variable. The serif
is used for display only, so a fixed optical size in that range is invisible —
and it takes the file from 122KB to 51KB.

| File | Family | Designer | Licence |
| --- | --- | --- | --- |
| `source-serif.woff2` | [Source Serif 4](https://fonts.google.com/specimen/Source+Serif+4) | Frank Grießhammer / Adobe | SIL Open Font License 1.1 |
| `inter.woff2` | [Inter](https://fonts.google.com/specimen/Inter) | Rasmus Andersson | SIL Open Font License 1.1 |

The OFL permits redistribution and web embedding, including as part of this
repository. Full text: <https://openfontlicense.org>.

To swap a font, download its latin-subset `woff2`, drop it in here under the
same filename, and update the `--serif` / `--sans` stacks in
`assets/css/main.scss`.

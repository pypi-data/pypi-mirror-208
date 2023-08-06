# dashtable-ext

Shitty Extension to doakey3/DashTable

## Installation

```zsh
$ pip install -U dashtable-ext
```

### RST 2 ASCII:

```rst
+-----------+-----------+-----------------------+
| Heading 1 | Heading 2 | Heading 3             |
|           +-----------+-----------+-----------+
|           | Heading 4 | Heading 5 | Heading 6 |
+===========+-----------+-----------+-----------+
| A         | B         | C                     |
|           +-----------+                       |
|           | D         |                       |
|           +-----------+-----------+-----------+
|           | E         | F         | G         |
+-----------+-----------+-----------+-----------+
| H                     | I         | J         |
+-----------------------+-----------+           |
| K                     | L         |           |
|                       +-----------+-----------+
|                       | M         | N         |
+-----------------------+-----------+-----------+
```

```py
from dashtable.ext import rst2ascii, PresetStyle
import dashtable

with open("table.html", "r") as f:
    html = f.read()

table = dashtable.html2rst(html)
print(rst2ascii(table = table, preset=PresetStyle.thin_thick_rounded))
```

Output:

```bash
╭───────────┬───────────┬───────────────────────╮
│ Heading 1 │ Heading 2 │ Heading 3             │
│           ├───────────┼───────────┬───────────┤
│           │ Heading 4 │ Heading 5 │ Heading 6 │
├━━━━━━━━━━━┼───────────┼───────────┴───────────┤
│ A         │ B         │ C                     │
│           ├───────────┤                       │
│           │ D         │                       │
│           ├───────────┼───────────┬───────────┤
│           │ E         │ F         │ G         │
├───────────┴───────────┼───────────┼───────────┤
│ H                     │ I         │ J         │
├───────────────────────┼───────────┤           │
│ K                     │ L         │           │
│                       ├───────────┼───────────┤
│                       │ M         │ N         │
╰───────────────────────┴───────────┴───────────╯
```

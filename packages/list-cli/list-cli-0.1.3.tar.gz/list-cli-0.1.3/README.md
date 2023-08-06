# list-cli

List Management Application (CLI)

## To install from _PyPi_ (_packaged installation_)

```bash
pip install list-cli
```

## To install from _GitHub_ (_source installation_)

```bash
git clone https://github.com/jzaleski/list-cli
cd list-cli
bin/setup
```

## Running the packaged version

```bash
list-cli
```

## Running from source

```bash
cd list-cli && bin/run
```

## Environment Variable Reference

* `DATABASE_FILE_PATH`: The full-path to the database-file -- it will be created
  if it does not exist (default: `$HOME/.list/LIST`)
* `DATABASE_NAME`: The database file-name -- if `DATABASE_FILE_PATH` was not
  specified, the `DATABASE_NAME` value will be used to check in the current
  directory, and if a matching file is not found, your home directory
  (e.g. `$HOME/.list/<DATABASE_FILE_PATH>`)

## Helpful aliases to emulate different "buckets" of list[-items]

```bash
alias goal='DATABASE_NAME="GOAL" list-cli';
alias question='DATABASE_NAME="QUESTION" list-cli';
alias todo='DATABASE_NAME="TODO" list-cli';
...
```

---

The above assumes a "packaged installation" to emulate the same behavior from a
"source installation" do the following:

```bash
alias goal='cd list-cli && DATABASE_NAME="GOAL" bin/run';
alias question='cd list-cli && DATABASE_NAME="QUESTION" bin/run';
alias todo='cd list-cli && DATABASE_NAME="TODO" bin/run';
...
```

## Available Operations

### Listing "list-items"

#### Usage:
```bash
list-cli [a|d|h|m|r]
```
(_the "added" bucket is rendered when no arguments are specified_)

---

### Adding a "list-item"
`"add"` (_short-hand:_ `"a"`)

#### Usage:
```bash
list-cli [a[dd]] <list-item>
```
(_this is the "default" operation if the first argument is not an "operation"_)

---

### Marking a "list-item" as "done":
`"done"` (_short-hand:_ `"d"`)

#### Usage:
```bash
list-cli d[one] <list-item-index>
```

---

### Editing a "list-item":
`"edit"` (short-hand: `"e"`)

#### Usage:
```bash
list-cli e[dit] <list-item-index> <list-item>
```

---

### Marking a "list-item" as "handed-off":
`"handoff"` (short-hand: `"h"`)

#### Usage:
```bash
list-cli h[andoff] <list-item-index>`
```

---

### Marking a "list-item" as "moved":
`"move"` (short-hand: `"m"`)

#### Usage:
```bash
list-cli m[ove] <list-item-index>
```

---

### Marking a "list-item" as "removed":
`"remove"` (short-hand: `"r"`)

#### Usage:
```bash
list-cli r[emove] <list-item-index>
```

---

### Touching a "list-item" (updates recency; used when sorting):
`"touch"` (short-hand: `"t"`)

#### Usage:
```bash
list-cli t[ouch] <list-item-index>
```

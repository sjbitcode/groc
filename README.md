# Groc

*Streamline your purchase history*

Groc is a Python CLI designed to help you keep track of purchases. You can enter data manually or via csv, and view various purchase stats.

Installing ✨
--------------
Install and update groc using pip:
```
pip install groc
```
Groc officially supports Python 3.7.


Usage
--------------
```
groc [COMMAND] [flags]
```
See also `groc --help`.



Commands
--------------
**init** 🔮

Create a groc database in user's home directory. If a database already exists, the command will abort.

To see detailed output, use the `--verbose` flag.
```
groc init
```

**add** 📝

Add a purchase to the groc database manually or by reading in a file or directory.

To enter purchase data manually, use the flags `--date`, `--total`, `--store`, `--description`.
The `--date` flag is optional and can be omitted _(the current date will be used)_.
The `--description` flag is optional and can be omitted.

To enter purchases via file or directory, use the `--source` flag provided with the path. Only csv files are currently supported.

Adding a purchase that already exists will abort the action, unless the `--ignore-duplicate` flag is passed; this can be especially useful when adding purchases from a file
or multiple files.
```
groc add --date 2019-01-01 --total 20.00 --store "Awesome Cakes" --description "birthday cake"

groc add --source ./my-purchases/january.csv

groc add --source ./my-purchases/ --ignore-duplicate
```

**delete** 🗑

Delete a purchase by id by passing the `--id`, `-i` flag. Multiple id flags can be passed.

Passing the flag `--dry-run` will output purchases to be deleted without actually deleting it.

To see complete purchase details of a purchase, use the `--verbose` flag.
```
groc delete --id 2 --dry-run
```

**breakdown** 📊

Provides a breakdown of purchases for the current month and year categorized by month.

Target specific months by passing one or multiple month flags like `--month`, `-m` or years like `--year`, `-y`.

To see extended stats, use the `--verbose`.
```
groc breakdown

groc breakdown --month=01 --month=03 --year=2019
```

**list** 🔍

Lists the latest 50 purchases by default, unless otherwise specified by the `--limit` flag.

View purchases for a specific month by passing in `--month`, `-m` flag, optionally with a year with the `--year`, `-y` flag.
To see all purchases of a month, pass the `--all`, `-a` flag.

To see detailed output, such as purchase id, use the `--verbose` flag.
```
groc list --limit 10

groc list -m 02 --all
```

**reset** 🚽

Reset a groc database by deleting all entries. The database and schema will not be deleted, so this does not require an init from the user.

Passing the `--dry-run` flag will output the purchase count to be reset.
```
groc reset --verbose
```

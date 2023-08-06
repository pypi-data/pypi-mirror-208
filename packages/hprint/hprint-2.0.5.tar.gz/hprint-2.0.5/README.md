hprint
======

Print python object as table/json format in an easy way based on [python-tabulate](https://github.com/astanin/python-tabulate).


The main use cases of the library are:

-   table print list of records (dict)
-   customize table header name
-   customize missing value
-   automatically print json string when fail to print as table
-   support expanded output, like postgres

Installation
------------

To install the Python library and the command line utility, run:

```shell
pip install -U hprint
```

Library usage
-------------

The module provides just one function, `hprint` or `pretty_print`(which is just alias of hprint), which takes a list of
dict or just a single dict as the first argument, and outputs a
nicely formatted plain-text table or json string as fallback.

```pycon
>>> from hprint import pretty_print

>>> data = [{'name': 'John Doe', 'age': 18}, {'name': 'Jane Doe', 'age': 20}]

>>> pretty_print(data)
name        age
--------  -----
John Doe     18
Jane Doe     20
```

### Show index

```pycon
>>> pretty_print(data, numbered=True)
  No  name        age    _no
----  --------  -----  -----
   1  John Doe     18      1
   2  Jane Doe     20      2
>>> pretty_print(data, numbered=True, offset=-1)
  No  name        age    _no
----  --------  -----  -----
   0  John Doe     18      0
   1  Jane Doe     20      1
```

## Expanded output

```pycon
>>> pretty_print(data, x=True)
-[ RECORD 1 ]--+---------
name           | John Doe
age            | 18
-[ RECORD 2 ]--+---------
name           | Jane Doe
age            | 20
```


### Customize Headers

```pycon
>>> pretty_print(data, mappings={'NAME': 'name', 'AGE': 'age'})
NAME        AGE
--------  -----
John Doe     18
Jane Doe     20
>>> pretty_print(data, mappings={'NAME': 'name', 'AGE': 'age'}, header=False)
--------  --
John Doe  18
Jane Doe  20
--------  --
>>> pretty_print(data, mappings={'NAME': ('name', lambda n: n.upper()), 'AGE': 'age'})
NAME        AGE
--------  -----
JOHN DOE     18
JANE DOE     20
>>> pretty_print(data, mappings={'Aggregate': ('', lambda person: person['name'] + ": " + str(person['age']))})
Aggregate
------------
John Doe: 18
Jane Doe: 20
>>> pretty_print(data, mappings={'NAME': 'name', 'AGE': 'age'}, header=False, x=True)
NAME           | John Doe
AGE            | 18
NAME           | Jane Doe
AGE            | 20
```

### Missing value

```pycon
>>> pretty_print(data, mappings={'NAME': 'name', 'AGE': 'age', 'GENDER': 'gender'})
NAME        AGE  GENDER
--------  -----  --------
John Doe     18  n/a
Jane Doe     20  n/a
>>> pretty_print(data, mappings={'NAME': 'name', 'AGE': 'age', 'GENDER': 'gender'}, missing_value='unknown')
NAME        AGE  GENDER
--------  -----  --------
John Doe     18  unknown
Jane Doe     20  unknown
```

### Table format

Supported format are the same with those supported by [tabulate](https://github.com/astanin/python-tabulate/blob/master/README.md#table-format).

```pycon
>>> pretty_print(data, tf='plain')
name        age
John Doe     18
Jane Doe     20
>>> pretty_print(data, tf='github')
| name     |   age |
|----------|-------|
| John Doe |    18 |
| Jane Doe |    20 |
>>> pretty_print(data, tf='pretty')
+----------+-----+
|   name   | age |
+----------+-----+
| John Doe | 18  |
| Jane Doe | 20  |
+----------+-----+
>>> pretty_print(data, tf='psql')
+----------+-------+
| name     |   age |
|----------+-------|
| John Doe |    18 |
| Jane Doe |    20 |
+----------+-------+
>>> pretty_print(data, tf='orgtbl')
| name     |   age |
|----------+-------|
| John Doe |    18 |
| Jane Doe |    20 |
>>> pretty_print(data, tf='html')
<table>
<thead>
<tr><th>name    </th><th style="text-align: right;">  age</th></tr>
</thead>
<tbody>
<tr><td>John Doe</td><td style="text-align: right;">   18</td></tr>
<tr><td>Jane Doe</td><td style="text-align: right;">   20</td></tr>
</tbody>
</table>
```

### Print as JSON

```pycon
>>> pretty_print(data, as_json=True)
[
    {
        "age": 18,
        "name": "John Doe"
    },
    {
        "age": 20,
        "name": "Jane Doe"
    }
]
```

### Raw output

```pycon
>>> s = pretty_print(data, raw=True)
>>> s
'name        age\n--------  -----\nJohn Doe     18\nJane Doe     20'
```




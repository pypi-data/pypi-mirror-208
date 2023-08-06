Changelog
=========

6.0 (2023-05-17)
----------------

- Drop support for Python 2.7, 3.5, 3.6.

- Drop support for deprecated ``python setup.py test``.


5.0 (2022-12-08)
----------------

- Add support for Python 3.7, 3.8, 3.9, 3.10, 3.11.

- Update PyPy version for Travis.

- Drop support for Python 3.4.


4.3 (2017-09-08)
----------------

- Add ``__ne__`` to the Prefix class.
  Fix a problem with undoLog/undoInfo filtering in ZODB.UndoLogCompatible

4.2 (2017-04-26)
----------------

- Add support for Python 3.6, drop support for Python 3.3.

4.1 (2016-04-03)
----------------

- Add compatibility with Python 3.4 and 3.5.

- Drop support for Python 2.6 and 3.2.

4.0 (2013-03-02)
----------------

- Add compatibility with Python 3.2 and 3.3. Note that the Prefix class
  only provides equality testing, but doesn't support ordering.

2.12.0 (2010-04-05)
-------------------

- Released as separate package.

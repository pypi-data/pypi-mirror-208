3.0
===
3.0.6
-----
Changed
^^^^^^^
- allow to use `str` as alert for notification payload (by @tartansandal)

Added
^^^^^
- some tests with Python version 3.6-3.11
- some payload serialization tests (by @tartansandal)
- some type annotations
- some docstrings

3.0.5
-----

Fixed
^^^^^
- have `auth.py` use the `Dict` type hint from the typing module by @tinycogio

3.0.0
-----

Refactored
^^^^^^^^^^
- extract authentication classes

2.1
===
2.1.0
-----

Added
^^^^^
- async/await support with `AsyncAPNSClient`

2.0
===
2.0.7
-----

Added
^^^^^
- usage as context manager
- certificate-based authentication

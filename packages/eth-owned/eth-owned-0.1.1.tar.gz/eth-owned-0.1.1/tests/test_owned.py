# standard imports
import unittest

# local imports
from eth_owned.unittest import TestOwned as TestOwnedBase
from eth_owned.unittest import TestInterface


class TestOwned(TestOwnedBase, TestInterface):
    pass


if __name__ == '__main__':
    unittest.main()

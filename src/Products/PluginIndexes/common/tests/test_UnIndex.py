##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
#############################################################################

import unittest


class UnIndexTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.PluginIndexes.common.UnIndex import UnIndex
        return UnIndex

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def _makeConflicted(self):
        from ZODB.POSException import ConflictError

        class Conflicted:

            def __str__(self):
                return 'Conflicted'
            __repr__ = __str__

            def __getattr__(self, id, default=object()):
                raise ConflictError('testing')

        return Conflicted()

    def test_empty(self):
        unindex = self._makeOne(id='empty')
        self.assertEqual(unindex.indexed_attrs, ['empty'])

    def test_removeForwardIndexEntry_with_ConflictError(self):
        from ZODB.POSException import ConflictError
        unindex = self._makeOne(id='conflicted')
        unindex._index['conflicts'] = self._makeConflicted()
        self.assertRaises(ConflictError, unindex.removeForwardIndexEntry,
                          'conflicts', 42)

    def test_get_object_datum(self):
        from Products.PluginIndexes.common.UnIndex import _marker
        idx = self._makeOne('interesting')

        dummy = object()
        self.assertEquals(idx._get_object_datum(dummy, 'interesting'), _marker)

        class DummyContent2(object):
            interesting = 'GOT IT'
        dummy = DummyContent2()
        self.assertEquals(idx._get_object_datum(dummy, 'interesting'),
                          'GOT IT')

        class DummyContent3(object):
            exc = None

            def interesting(self):
                if self.exc:
                    raise self.exc
                return 'GOT IT'
        dummy = DummyContent3()
        self.assertEquals(idx._get_object_datum(dummy, 'interesting'),
                          'GOT IT')

        dummy.exc = AttributeError
        self.assertEquals(idx._get_object_datum(dummy, 'interesting'), _marker)

        dummy.exc = TypeError
        self.assertEquals(idx._get_object_datum(dummy, 'interesting'), _marker)

    def test_getCounter(self):
        index = self._makeOne('counter')

        self.assertEqual(index.getCounter(), 0)

        class Dummy(object):
            id = 1
            counter = 'counter'

        obj = Dummy()
        index.index_object(obj.id, obj)
        self.assertEqual(index.getCounter(), 1)

        index.unindex_object(obj.id)
        self.assertEqual(index.getCounter(), 2)

        # unknown id
        index.unindex_object(1234)
        self.assertEqual(index.getCounter(), 2)

        index.clear()
        self.assertEqual(index.getCounter(), 0)

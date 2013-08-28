#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

import sys
import os
DIR = os.path.abspath(os.path.normpath(os.path.join(__file__,
    '..', '..', '..', '..', '..', 'trytond')))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

import unittest
from decimal import Decimal
import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT, test_view,\
    test_depends
from trytond.transaction import Transaction
from trytond.exceptions import UserError


class ProductTestCase(unittest.TestCase):
    '''
    Test Product customizations to product_code module.
    '''

    def setUp(self):
        trytond.tests.test_tryton.install_module('product_code')
        self.product = POOL.get('product.product')
        self.uom = POOL.get('product.uom')
        self.product_code = POOL.get('product.product.code')
        self.template = POOL.get('product.template')

    def test0005views(self):
        '''
        Test views.
        '''
        test_view('product_code')

    def test0006depends(self):
        '''
        Test depends.
        '''
        test_depends()

    def test0010code_constraints(self):
        '''Test EAN and UPC-A code length constraints
        '''
        with Transaction().start(DB_NAME, USER, context=CONTEXT) as transaction:
            template, = self.template.create([{
                'name': 'Test product',
                'default_uom': self.uom.search([('name', '=', 'Unit')])[0],
                'list_price': Decimal('10'),
                'cost_price': Decimal('5'),
            }])
            self.assert_(template)

            product, = self.product.search([])

            self.assertRaises(UserError, self.product_code.create, [{
                'product': product,
                'code': '123456',
                'code_type': 'ean'
            }])
            self.product_code.create([{
                'product': product,
                'code': '1234567890123',
                'code_type': 'ean'
            }])
            self.assertRaises(UserError, self.product_code.create, [{
                'product': product,
                'code': '123456',
                'code_type': 'upc-a'
            }])
            self.product_code.create([{
                'product': product,
                'code': '123456789012',
                'code_type': 'upc-a'
            }])

            transaction.cursor.rollback()

    def test0020product_rec_name_search(self):
        '''Test the rec name search on product
        '''
        with Transaction().start(DB_NAME, USER, context=CONTEXT) as transaction:
            template, = self.template.create([{
                'name': 'Test product',
                'default_uom': self.uom.search([('name', '=', 'Unit')])[0],
                'list_price': Decimal('10'),
                'cost_price': Decimal('5'),
            }])
            self.assert_(template)

            product, = self.product.search([])

            self.product_code.create([{
                'product': product,
                'code': '1231231231231',
                'code_type': 'ean'
            }])
            self.product_code.create([{
                'product': product,
                'code': '789789789789',
                'code_type': 'upc-a'
            }])
            self.product_code.create([{
                'product': product,
                'code': 'somecode',
                'code_type': 'other'
            }])

            self.assertEqual(
                len(self.product.search([('rec_name', 'ilike', '%123%')])), 1
            )
            self.assertEqual(
                len(self.product.search([('rec_name', 'ilike', '%test%')])), 1
            )
            self.assertEqual(
                len(self.product.search([('rec_name', 'ilike', '%78%')])), 1
            )
            self.assertEqual(
                len(self.product.search([('rec_name', 'ilike', '%code%')])), 1
            )
            self.assertEqual(
                len(self.product.search([('rec_name', 'ilike', '%wrong%')])), 0
            )

            transaction.cursor.rollback()


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        ProductTestCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

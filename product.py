# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool, PoolMeta

__all__ = ['Product', 'ProductCode']
__metaclass__ = PoolMeta


class Product:
    "Product"
    __name__ = 'product.product'

    codes = fields.One2Many(
        'product.product.code', 'product', 'Codes'
    )

    @classmethod
    def search_rec_name(cls, name, clause):
        ProductCode = Pool().get('product.product.code')

        ids = map(int, cls.search([('code',) + tuple(clause[1:])], order=[]))
        ids += map(int, cls.search(
            [('template.name',) + tuple(clause[1:])], order=[]
        ))

        if not ids:
            codes = ProductCode.search(
                [('code',) + tuple(clause[1:])], order=[]
            )
            ids += map(int, cls.search([('codes', 'in', map(int, codes))]))

        return [('id', 'in', ids)]


class ProductCode(ModelSQL, ModelView):
    "Product Code"
    __name__ = 'product.product.code'
    _rec_name = 'code'

    code = fields.Char('Value', required=True, select=True)
    code_type = fields.Selection([
        ('ean', 'EAN'),
        ('upc-a', 'UPC-A'),
        ('other', 'Other')
    ], 'Type', required=True)
    active = fields.Boolean('Active')
    product = fields.Many2One(
        'product.product', 'Product', ondelete='CASCADE', select=True
    )

    @classmethod
    def __setup__(cls):
        super(ProductCode, cls).__setup__()
        cls._error_messages.update({
            'wrong_code': 'The code entered is wrong.'
            '\nFor EAN, length should be 13.'
            '\nFor UPC-A, length should be 12.'
        })
        # XXX: The uniqueness should be global or based on code type.
        # But its a problem to worry about later
        cls._sql_constraints = [(
            'code_uniq', 'UNIQUE(code)',
            'Another code with the same value already exists!'
        )]

    def check_code(self):
        '''
        Check the length of the code depending on type.
        EAN should be 13 characters
        UPC-A should be 12 characters
        '''
        if self.code_type == 'ean' and len(self.code) != 13:
            self.raise_user_error('wrong_code')
        if self.code_type == 'upc-a' and len(self.code) != 12:
            self.raise_user_error('wrong_code')

        return True

    @staticmethod
    def default_active():
        return True

    @classmethod
    def validate(cls, records):
        """
        Validate records.

        :param records: active record list of productcode objects
        """
        super(ProductCode, cls).validate(records)
        for record in records:
            record.check_code()

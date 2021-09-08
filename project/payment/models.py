import enum

from django.db import models
from django.utils.timezone import now

from wagtail.snippets.models import register_snippet


class IncorrectCustomer (Exception):
    pass

class IncorrectProduct (Exception):
    pass

class IncorrectAmount (Exception):
    pass

class IncorrectPayload (Exception):
    pass

# Create your models here.

class OrderStatusEnum (enum.IntEnum):
    WAITING             = 0
    UNKNOW_TRANSACTION  = 1             # Failed to create a transaction row
    TEST_TRANSACTION    = 2             # Transaction is in TEST mode
    PARSE_FAILED        = 3             # Failed to parse ext data
    INCORRECT_INFORMATIONS = 4          # Ext data contains errors
    INCORRECT_PAYLOAD   = 10
    INCORRECT_AMOUNT    = 11
    INCORRECT_PRODUCT   = 12
    INCORRECT_CUSTOMER  = 13
    COMPLETED           = 20
    
    @classmethod
    def choices (cls):
        return [(key.value, key.name) for key in cls]

class TransactionVADSManager(models.Manager):
    def create_transaction (self, data):
        t = TransactionVADS()

        try:
            t.amount        = int(data['vads_amount'])
            
            t.trans_id      = data['vads_trans_id']
            t.trans_date    = data['vads_trans_date']
            t.trans_status  = data['vads_trans_status']

            t.cust_email    = data['vads_cust_email']

            t.ext_info_1 = data['vads_ext_info_Informations']
            
            t.save()
            return t

        except:
            raise Exception


@register_snippet
class TransactionVADS (models.Model):

    amount = models.IntegerField()

    # VADS Payload data
    trans_id = models.CharField(max_length=20)
    trans_date = models.CharField(max_length=20, default= '')
    trans_status = models.CharField(max_length=50)

    cust_email = models.EmailField()

    ext_info_1 = models.TextField()

    order_id = models.PositiveIntegerField(default=0)
    order_message = models.TextField(default='')
    
    date = models.DateTimeField(default=now)
    # Final status
    status = models.IntegerField(choices=OrderStatusEnum.choices(), default=OrderStatusEnum.WAITING)

    objects = TransactionVADSManager()

    def __str__ (self):
        return f'#{self.id} - Email ({self.cust_email}) - Amount ({self.amount}) Date ({self.date}) Status ({self.status}) '
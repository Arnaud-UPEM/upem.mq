from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view

from .models import TransactionVADS, OrderStatusEnum as OSE
from .parser import parse

# Create your views here.

@api_view(['POST'])
def api_vads_ipn (request):
    # print (request.META['REMOTE_HOST'])
    # print (request.META['REMOTE_ADDR'])

    if not request.data:
        # response_object['message'] = 'Payload vide.'
        return JsonResponse({'status': 'Failure'}, status=400)

    data = request.data.dict()
    print (data)

    if not settings.DEBUG:
        if data['vads_ctx_mode'] != 'PRODUCTION':
            return JsonResponse({'status': 'Failure', 'message': 'Transaction TEST refusée'}, status=400) 

    try:
        # 1 - Save transaction
        # print ('1')
        transaction = TransactionVADS.objects.create_transaction(data)

        if transaction.trans_status != 'AUTHORIZED':
            return JsonResponse({
                'status': 'Failure',
                'message': 'Paiement non authorisé.'
            }, status=400)

        # 2 - Parse received data with payment_vads
        # print ('2')
        parsed = parse(transaction.ext_info_1)

        print (transaction.ext_info_1)
        print (parsed)

        if not parsed['status']:
            raise Exception('Impossible d\'analyser le contenu de la requête.')

    except Exception as e:
        return JsonResponse({
            'status': 'Failure',
            'message': str(e)
        }, status=400)

    # print (parsed)

    try:
        # Gift
        # ...

        # Contribution
        # ...

        # Else - Error
        # ...
        raise Exception ('Objet du paiement inconnu.')


        if parsed['version'] == 1:
            # 3 - Query order
            # raise BadRequest on error 
            # print ('3')
            res = OrderHelper.ipn_pay_v1({
                'cart': parsed['cart'],
                'payer': parsed['parent_id'],
                'amount': transaction.amount / 100,
                'transaction_id': transaction.id
            })

            # 4 - Attach order to transaction
            # print ('4')
            transaction.order_id = res['order'].id

        elif parsed['version'] == 2:
            order = OrderHelper.ipn_pay_v2({
                'order_id': parsed['order_id'],
                'amount': transaction.amount / 100,
                'transaction_id': transaction.id
            })

            transaction.order_id = order.id

        else:
            raise Exception

        transaction.order_status = OSE.COMPLETED
        transaction.save()

    except Exception as e:
        if str(e) == 'Création impossible: le panier contient des produits invalides.':
            transaction.order_status = OSE.INCORRECT_PRODUCT
        elif 'Montant incorrect.' in str(e):
            transaction.order_status = OSE.INCORRECT_AMOUNT
        else:
            transaction.order_status = OSE.INCORRECT_PAYLOAD

        transaction.order_message = str(e)
        transaction.save()

        # print (transaction.order_status)
        # print (transaction.order_message)

        return JsonResponse({
            'status': 'Failure',
            'message': str(e)
        }, status=400)


    return JsonResponse({'status': 'Success'}, status=200)
    
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AccountsModel
from .serializers import AccountsSerializer
from rest_framework import viewsets
from rest_framework import status
import json
from django.db import DatabaseError, IntegrityError, transaction
import time
from decimal import Decimal
import logging


logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


class AccountsViewSet(viewsets.ModelViewSet):
    """хотя это и нет в ТЗ, но сделал стандартный CRUD
        /api/accounts
        /api/accounts/<unique_id>
    """
    serializer_class = AccountsSerializer
    queryset = AccountsModel.objects.all()
    lookup_field = 'unique_id'


def serialize(resp_dict):
    """сериализовать ответ с учётом кодировки"""
    return json.dumps(resp_dict, ensure_ascii=False).encode('utf8')


class PingView(APIView):
    """пинг, возвратит время выполнения (/api/ping)"""

    def __init__(self, **kwargs):
        self.start_time = time.time()
        super().__init__(**kwargs)

    def get(self, request):
        logging.info('ping..')
        return Response(serialize({'ping': 'alive', 'elapsed_time': f'{time.time() - self.start_time} sec'}),
                        status=status.HTTP_200_OK)


class OperationsInterface:
    """интерфейс для операций сложения/вычитания заданной суммы к балансу"""

    def __init__(self):
        # шаблон ответа
        self.resp = {'status': '',
                     'result': False,
                     'addition': {},
                     'description': {}
                     }
        self.operation_type: str = ''  # тип операции
        self.is_performed: bool = True  # выполнена ли операция
        # ответ для невалидных данных
        self.resp_no_valid = {'status': status.HTTP_400_BAD_REQUEST,
                              'result': False,
                              'addition': {},
                              'description': {'error': 'check_your_input_data'}
                              }

    def save(self, account):
        serializer_class = AccountsSerializer(account, data={'status': account.status})
        if serializer_class.is_valid():
            try:
                with transaction.atomic():
                    serializer_class.save()
                    self.resp['status'] = status.HTTP_200_OK if self.is_performed else status.HTTP_400_BAD_REQUEST
            except (DatabaseError, IntegrityError) as ex:
                logging.exception(f'OperationsInterface-->saving error-> {ex}')
                self.resp['status'] = status.HTTP_400_BAD_REQUEST
                self.resp['result'] = False
                self.resp['description'] = {self.operation_type: 'error during transaction performing..'}
        else:
            self.resp['status'] = status.HTTP_400_BAD_REQUEST
        self.resp['addition'] = serializer_class.data

    @staticmethod
    def is_input_valid(request):
        if 'unique_id' not in request.data or 'amount' not in request.data:
            return False
        try:
            unique_id = request.data['unique_id']
            amount = Decimal(request.data['amount'])
            if amount < 0:
                return False
            AccountsModel.objects.get(unique_id=unique_id)
            return True
        except Exception as ex:
            logging.exception(f'OperationsInterface-->validation error-> {ex}')
            return False


class AddView(OperationsInterface, APIView):
    """пополнение баланса (/api/add)"""

    @transaction.atomic
    def put(self, request):
        self.operation_type = 'addition'

        if self.is_input_valid(request):

            unique_id = request.data['unique_id']
            amount_to_add = Decimal(request.data['amount'])
            account = AccountsModel.objects.get(unique_id=unique_id)

            # выполним сложение, если аккаунт активен
            if account.status:
                balance = Decimal(account.balance) / 100
                new_balance = (balance + amount_to_add) * 100
                account.balance = int(new_balance)
                self.is_performed = True
                self.resp['description'] = {self.operation_type: 'performed'}
            else:
                self.resp['description'] = {self.operation_type: 'operation is not allowed for this account'}
            self.resp['result'] = self.is_performed

            # сохраним данные
            self.save(account=account)
            return Response(serialize(self.resp), status=status.HTTP_200_OK)
        else:
            return Response(serialize(self.resp_no_valid), status=status.HTTP_400_BAD_REQUEST)


class SubtractView(OperationsInterface, APIView):
    """уменьшение баланса (/api/substract)"""

    @transaction.atomic
    def put(self, request):
        self.operation_type = 'subtraction'

        if self.is_input_valid(request):

            unique_id = request.data['unique_id']
            amount_to_subtract = Decimal(request.data['amount'])
            account = AccountsModel.objects.get(unique_id=unique_id)

            # выполним вычитание
            if account.status and amount_to_subtract > 0:

                current_balance = Decimal(account.balance) / 100
                hold = Decimal(account.hold) / 100
                final_balance = current_balance - hold - amount_to_subtract
                self.is_performed = False if final_balance < 0 else True

                if self.is_performed:
                    # как я понял из ТЗ, при выполнении вычета нужно вычесть холд - а значит и его (холд) - обнулить
                    account.balance = int(final_balance)
                    account.hold = 0
                    self.resp['description'] = {self.operation_type: 'performed'}
                else:
                    self.resp['description'] = {self.operation_type: 'not enough money!'}

            else:
                self.resp['description'] = {'subtraction': 'operation is not allowed for this account!'}

            # сохраним данные
            self.save(account=account)

            return Response(serialize(self.resp), status=status.HTTP_200_OK)
        else:
            return Response(serialize(self.resp_no_valid), status=status.HTTP_400_BAD_REQUEST)


class StatusView(APIView):
    """показать статус счета /api/status"""

    def get(self, request):
        try:
            unique_id = request.data['unique_id']
            account = AccountsModel.objects.get(unique_id=unique_id)
            account_status = 'Открыт' if account.status else 'Закрыт'
            resp = {'Статус счёта': account_status}
            return Response(serialize(resp), status=status.HTTP_200_OK)
        except Exception as e:
            logging.exception(f'StatusView: error-> {e}')
            return Response(serialize({'error: check your request'}), status=status.HTTP_400_BAD_REQUEST)


class SubtractHoldView(OperationsInterface, APIView):
    """ вычесть холд (/api/hold) """
    @transaction.atomic
    def put(self, request):
        self.operation_type = 'hold'
        try:
            unique_id = request.data['unique_id']
            account = AccountsModel.objects.get(unique_id=unique_id)

            balance = account.balance
            hold = account.hold
            if balance >= hold or not account.status:
                account.balance = balance - hold
                account.hold = 0
                self.resp['description'] = {self.operation_type: 'performed'}
                self.is_performed = True
            else:
                self.resp['description'] = {self.operation_type: 'not performed'}

            # сохраним данные
            self.save(account=account)

            return Response(serialize(self.resp), status=status.HTTP_200_OK)
        except Exception as ex:
            logging.exception(f'SubtractHoldView: error-> {ex}')
            return Response(serialize(self.resp_no_valid), status=status.HTTP_400_BAD_REQUEST)

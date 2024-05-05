import asyncio
from typing import Union

import aiohttp
from datacls import ServerResponse, Receiver
from enums import PaymentStatus


class YooMoneyP2P:
    """Урезанный функционал YooMoney API. Здесь подразумевается, что у пользователя уже есть постоянный токен авторизации, поэтому метод авторизации отсутствует"""

    _base_url = "https://yoomoney.ru/"

    def __init__(self, api_token: str):
        """Конструктор.

        :param api_token: Постоянный токен приложения YooMoney API
        """
        self.__token = api_token

        self._basic_headers = {
            "Host": "yoomoney.ru",
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    @property
    def token(self):
        """YooMoney API Bearer токен"""
        return self.__token

    async def _p2p_request_payment(self, to: str, amount_due: float, comment: str, message: str) -> ServerResponse:
        """Запрос перевода денег на счет другого пользователя. (пользователь должен иметь YooMoney)

        :param to: Идентификатор получателя перевода (номер счета, номер телефона или email)
        :param amount_due: Сумма к получению (придет на счет получателя после оплаты)
        :param comment: Комментарий к переводу, отображается в истории отправителя
        :param message: Комментарий к переводу, отображается получателю
        """
        endpoint = f"/api/request-payment?pattern_id=p2p&to={to}&amount_due={amount_due}&message={message}&comment={comment}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url=self._base_url + endpoint, headers=self._basic_headers) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))

    async def _p2p_process_payment(self, request_payment_response: ServerResponse) -> ServerResponse:
        """Подтверждение платежа, ранее созданного методом request-payment

        :param request_payment_response: Ответ на запрос request-payment
        """
        endpoint = f"api/process-payment?request_id={request_payment_response.json['request_id']}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url=self._base_url + endpoint, headers=self._basic_headers) as response:
                return ServerResponse(response, (await response.json()), (await response.text()))

    async def withdrawal_funds(self, receiver: Receiver, reaction_ruble_rate: float) -> tuple[
        PaymentStatus, Union[ServerResponse, None]]:
        """Отдельный метод для вывода средств.

        :param receiver: Объект получателя средств
        :param reaction_ruble_rate: Курс, по которому будет воспроизведена выплата (Сколько рублей за одну реакцию).
        """

        request = await self._p2p_request_payment(
            to=receiver.yoomoney_account,
            amount_due=receiver.reactions_count * reaction_ruble_rate,
            comment=f"Выплата пользователю с Telegram ID {receiver.telegram_id} ({receiver.telegram_username}). {receiver.reactions_count} реакций.",
            message=f"Выплата за {receiver.reactions_count} реакций."
        )
        if request.json['status'] == PaymentStatus.REFUSED.value:
            return PaymentStatus.BROKEN, None

        process = await self._p2p_process_payment(request)
        attempts = 0
        while process.json['status'] == PaymentStatus.IN_PROGRESS.value:
            process = await self._p2p_process_payment(request)
            attempts += 1
            if attempts >= 10:
                return PaymentStatus.BROKEN, None
            await asyncio.sleep(60)
        if process.json['status'] == PaymentStatus.REFUSED.value:
            return PaymentStatus.REFUSED, process
        if process.json['status'] == PaymentStatus.SUCCESS.value:
            return PaymentStatus.SUCCESS, process

import atexit
import enum
import os
import pickle
from BGLogger import BGC


class BotConfigError(Exception):
    """Ошибка при настройке конфигурации бота"""
    pass


class BotConfigKeys(enum.Enum):
    TELEGRAM_API_TOKEN = "telegram_api_token"
    YOUMONEY_API_TOKEN = "youmoney_api_token"


class BotConfig:
    """Сохранение конфигурации бота для быстрого перезапуска. (Сериализация и десериализация данных)"""

    def __init__(self):

        self.__bytes_file: str = 'bot_config.pickle'

        if not os.path.exists(self.__bytes_file):
            with open(self.__bytes_file, 'wb') as file:
                serializable = {
                    BotConfigKeys.TELEGRAM_API_TOKEN.value: None,
                    BotConfigKeys.YOUMONEY_API_TOKEN.value: None
                }
                pickle.dump(serializable, file)

        with open(self.__bytes_file, 'rb') as bytes_file:
            data = pickle.load(bytes_file)
            self.__telegram_token = data[BotConfigKeys.TELEGRAM_API_TOKEN.value]
            self.__youmoney_token = data[BotConfigKeys.YOUMONEY_API_TOKEN.value]

        if self.__telegram_token is not None and self.__youmoney_token is not None:
            reset = BGC.scan(
                'Сбросить текущую конфигурацию бота (Telegram API токен, YouMoney API токен) ?\nY - Да, настроить всё заново\n<Enter> - Нет, запустить бота с текущей конфигурацией\n\n/> ',
                label_color=BGC.Color.MUSTARD
            )
            if reset.upper() == 'Y':
                self.__telegram_token = self.set_telegram_token()
                self.__youmoney_token = self.set_youmoney_token()
            else:
                pass
        else:
            self.__telegram_token = self.get_telegram_token()
            self.__youmoney_token = self.get_youmoney_token()
        atexit.register(self.__dump_config)

    @property
    def telegram_token(self):
        return self.__telegram_token

    @property
    def youmoney_token(self):
        return self.__youmoney_token

    def __dump_config(self):
        with open(self.__bytes_file, 'wb') as file:
            serializable = {
                BotConfigKeys.TELEGRAM_API_TOKEN.value: self.__telegram_token,
                BotConfigKeys.YOUMONEY_API_TOKEN.value: self.__youmoney_token
            }
            pickle.dump(serializable, file)

    def __read_config(self):
        with open(self.__bytes_file, 'rb') as bytes_file:
            data = pickle.load(bytes_file)
            return data

    def get_telegram_token(self) -> str:
        token = self.__read_config()[BotConfigKeys.TELEGRAM_API_TOKEN.value]
        if token is not None:
            return token
        new_token = BGC.scan('Telegram API токен /> ', label_color=BGC.Color.CRIMSON)
        return new_token

    def get_youmoney_token(self) -> str:
        token = self.__read_config()[BotConfigKeys.YOUMONEY_API_TOKEN.value]
        if token is not None:
            return token
        new_token = BGC.scan('YouMoney API токен /> ', label_color=BGC.Color.CRIMSON)
        return new_token

    @classmethod
    def set_telegram_token(cls) -> str:
        new_token = BGC.scan('Telegram API токен /> ', label_color=BGC.Color.CRIMSON)
        return new_token

    @classmethod
    def set_youmoney_token(cls) -> str:
        new_token = BGC.scan('YouMoney API токен /> ', label_color=BGC.Color.CRIMSON)
        return new_token

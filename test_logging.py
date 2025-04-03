import logging
import json
import sys

# Настраиваем логирование
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname.lower(),
            "function": f"{record.module}:{record.funcName}:{record.lineno}",
            "message": record.getMessage()
        }
        
        # Добавляем дополнительные поля
        if hasattr(record, 'command_name'):
            log_record['command_name'] = record.command_name
        if hasattr(record, 'username'):
            log_record['username'] = record.username
            
        return json.dumps(log_record)

# Настраиваем логгер
logger = logging.getLogger("test_logger")
logger.setLevel(logging.INFO)

# Создаем обработчик для консоли
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(JSONFormatter())
logger.addHandler(console_handler)

# Создаем класс фильтра
class CommandFilter(logging.Filter):
    def __init__(self, command_name, username):
        super().__init__()
        self.command_name = command_name
        self.username = username
        
    def filter(self, record):
        record.command_name = self.command_name
        record.username = self.username
        return True

# Тестируем разные способы добавления полей command_name и username
print("\n--- Тест 1: Использование фильтра ---")
command_filter = CommandFilter("/help", "test_user")
logger.addFilter(command_filter)
logger.info("Обработка команды через фильтр")
logger.removeFilter(command_filter)

print("\n--- Тест 2: Прямое добавление атрибутов ---")
class AttrLogger:
    def __init__(self, logger):
        self.logger = logger
        
    def log_with_attr(self, msg, command_name, username):
        record = logging.LogRecord(
            name=self.logger.name,
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=msg,
            args=(),
            exc_info=None
        )
        record.command_name = command_name
        record.username = username
        
        for handler in self.logger.handlers:
            handler.handle(record)

attr_logger = AttrLogger(logger)
attr_logger.log_with_attr("Обработка команды через прямые атрибуты", "/status", "direct_user")

print("\n--- Тест 3: Использование extra параметра ---")
class ExtraAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs["extra"] = self.extra
        return msg, kwargs

extra_logger = ExtraAdapter(logger, {"command_name": "/me", "username": "extra_user"})
extra_logger.info("Обработка команды через extra")

print("\n--- Тест 4: Сеттер для LogRecord ---")
original_factory = logging.getLogRecordFactory()

def record_factory(*args, **kwargs):
    record = original_factory(*args, **kwargs)
    record.command_name = "/settings"
    record.username = "factory_user"
    return record

logging.setLogRecordFactory(record_factory)
logger.info("Обработка команды через factory")

# Возвращаем оригинальную фабрику
logging.setLogRecordFactory(original_factory)

# Прямой способ
print("\n--- Тест 5: Прямое использование __dict__ ---")
logging.info("Обработка команды напрямую", 
             extra={"command_name": "/reflect", "username": "direct_dict_user"}) 
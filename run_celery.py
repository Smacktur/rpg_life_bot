"""
Скрипт для запуска Celery worker и scheduler.
Использование:
    python run_celery.py worker  # Запустить worker
    python run_celery.py beat    # Запустить scheduler
    python run_celery.py flower  # Запустить мониторинг (если установлен flower)
    python run_celery.py all     # Запустить все компоненты
"""

import sys
import subprocess
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Команды для запуска различных компонентов Celery
COMMANDS = {
    "worker": "celery -A celery_app worker --loglevel=info",
    "beat": "celery -A celery_app beat --loglevel=info",
    "flower": "celery -A celery_app flower --port=5555",
    "all": None,  # Особый случай, запускает несколько команд
}

def run_command(cmd):
    """Запуск команды через subprocess"""
    print(f"Executing: {cmd}")
    subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    # Проверка аргументов
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: python {sys.argv[0]} [{'|'.join(COMMANDS.keys())}]")
        sys.exit(1)
    
    # Получение команды
    command = sys.argv[1]
    
    # Запуск команды
    if command == "all":
        # Запуск нескольких процессов
        processes = []
        for cmd_name, cmd_str in COMMANDS.items():
            if cmd_name != "all" and cmd_str:
                process = subprocess.Popen(cmd_str, shell=True)
                processes.append((cmd_name, process))
                print(f"Started {cmd_name} with PID {process.pid}")
        
        # Ожидание нажатия клавиши для завершения
        print("Press Enter to terminate all processes...")
        input()
        
        # Завершение процессов
        for cmd_name, process in processes:
            print(f"Terminating {cmd_name}...")
            process.terminate()
    else:
        # Запуск одной команды
        run_command(COMMANDS[command]) 
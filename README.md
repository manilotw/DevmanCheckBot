# DVMN Telegram Bot

## Описание

Этот бот предназначен для отправки результата проверки работ с сайта DVMN.org в ваш чат в Telegram. Также к нему прилагается бот, следящий за работой первого и в случае возникновения ошибок, информирующего об этом в телеграме.

## Установка и использование

### Предварительные шаги

1. Убедитесь, что у вас установлен Python (рекомендуется Python 3).
2. Зарегистрируйте бота в Telegram и получите токен.
3. Получите токен разработчика DVMN.org.

### Установка зависимостей

Используйте `pip` (или `pip3`, если есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```

### Инструкция по настройке рабочего окружения
Создайте файл .env и добавьте следующие переменные окружения:

    DEVMAN_TOKEN=ваш_токен_разработчика_DVMN
    TG_BOT_TOKEN=ваш_токен_Telegram_бота
    CHAT_ID=ващ_чат_айди

### Пример запуска проекта
Для запуска пропишите:

```
python bot.py
```

## 🚀 Логирование и автоперезапуск

Бот теперь умеет:

- сохранять логи в файл `/opt/devman/DevmanCheckBot/bot.log`;
- отправлять ошибки прямо в Telegram;
- восстанавливаться после сбоев (благодаря `while True` и `try...except`);
- работать как системный сервис в фоне.

---

## 🔄 Настройка автозапуска через systemd

Создай новый сервис:

```bash
sudo nano /etc/systemd/system/devman-bot.service
```
Вставь содержимое
```
[Unit]
Description=Devman Telegram Bot
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/devman/DevmanCheckBot/bot.py
WorkingDirectory=/opt/devman/DevmanCheckBot
Restart=always

[Install]
WantedBy=multi-user.target
```
сохрани нажав Ctrl + O -> Enter -> Ctrl + X

Запусти

```
sudo systemctl daemon-reload
sudo systemctl enable devman-bot
sudo systemctl start devman-bot

```
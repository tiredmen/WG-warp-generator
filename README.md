# confgen

***НЕ РАБОТАЕТ***

Генератор WireGuard-конфигов с поддержкой Cloudflare WARP и прокси

## Описание

Этот скрипт автоматически:

- Генерирует ключи WireGuard
- Создаёт рабочий конфиг WireGuard
- Генерирует QR-код для быстрой настройки на мобильных устройствах
- Поддерживает работу через SOCKS5-прокси (необходимость в условиях заблокированного CloudFlare в рф)

## Требования

- Python 3.7+
- [WireGuard для Windows](https://www.wireguard.com/install/) (должен быть установлен и путь к `wg.exe` прописан в коде)
- Установленные зависимости:

  ```установка библиотек
  pip install requests[socks] qrcode[pil]
  ```

## Использование

1. **Запустите скрипт**

   ```запуск скрипта
   python confGen.py
   ```

1. **Результат**
   - Конфиг WireGuard будет выведен в консоль и сохранён в файл `WARP.conf`
   - Будет сгенерирован QR-код для быстрой настройки
   - Будет выведена ссылка для скачивания конфига

1. **VPN**
   - Загрухаем файл конфига в приложение для пк и андроид WireGuard/AmneziaWG(AmneziaVPN)
   - Сканируем код в приложении смартфона WireGuard/AmneziaWG(AmneziaVPN)
   - Позволяет смотреть YouTube использовать Discord без повышенного пинга

## Примечания

- Для работы с SOCKS5-прокси необходим пакет `requests[socks]`
- Если не нужен прокси, закомментируйте строку с `proxies = get_random_proxy()`
- Для корректной работы убедитесь, что путь к `wg.exe` в функции `gen_wg_keys` указан правильно

---

**Автор:**  
tireddud

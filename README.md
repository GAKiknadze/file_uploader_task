# Тестовое задание "File uploader"

## Цель проекта

Реализовать асинхронный сервис для загрузки и управления аудиофайлами с авторизацией через Яндекс.
Сервис должен предоставлять REST API с использованием FastAPI, PostgreSQL и Docker.

[Подробнее об условиях реализации](./docs/technical_specification.md)

## Перед началом установки

Убедитесь, что на вашем устройстве установлены следующие программы:

1. [Git](https://git-scm.com/book/ru/v2/Введение-Установка-Git)
2. [Docker](https://docs.docker.com/engine/install/)
3. [Docker Compose](https://docs.docker.com/compose/install/)

## Установка

### Клонируйте репозиторий
```bash
git clone https://github.com/GAKiknadze/file_uploader_task.git
cd ./file_uploader_task
```

### Измените настройки в `.env` файле

Поддерживаемые переменные

| Наименование переменной | Обязательный параметр | Тип данных | Значение по умолчанию | Описание |
| - | - | - | - | - |
| `PORT` |  | int | 8000 | Номер порта, на котором будет работать docker-контейнер |
| `JWT_SECRET_KEY` | ✅ | str | - | Ключ подписи jwt-токенов |
| `JWT_ALGORITHM` |  | str | "HS256" | Алгоритм подписи jwt-токенов |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` |  | int | 30 | Количество **минут** валидности access-токена |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` |  | int | 7 | Количество **дней** валидности refresh-токена |
| `YANDEX_CLIENT_ID` | ✅ | str | - | Идентификатор приложения |
| `YANDEX_CLIENT_SECRET` | ✅ | str | - | Секретный ключ |
| `YANDEX_CLIENT_URI` | ✅ | str | - | URL, по которому пользователи перенаправляются после успешной авторизации |
| `FILE_MAX_SIZE` | - | int | 20 | Максимальный размер файла в MB |
| `FILE_UPLOAD_PATH` | ✅ | str | - | Путь папки, хранящей файлы  |
| `FILE_SUPPORTED_FORMATS` |  | str | "*" | MIME-типы файлов допустимые к загрузке. Если указана строка "*", пользователи могут загружать файлы любого типа. |

## Запуск проекта

```bash
docker compose up -d
```

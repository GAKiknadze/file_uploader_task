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

1. Клонируйте репозиторий проекта
```bash
git clone https://github.com/GAKiknadze/file_uploader_task.git
cd ./file_uploader_task
```

2. Измените настройки проекта ([Подробнее](./docs/settings.md))


## Запуск проекта

```bash
docker compose up -d
```

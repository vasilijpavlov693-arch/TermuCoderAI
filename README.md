<p align="center">
  <h1 align="center">🤖 TermuCoderAI</h1>
  <p align="center">
    <strong>Локальный AI-ассистент для разработчика</strong><br>
    Работает на вашем устройстве — без облака и без отправки данных
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.7.0-green" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License">
  <img src="https://img.shields.io/badge/platforms-Windows%20%7C%20Linux%20%7C%20Termux-lightgrey" alt="Platforms">
  <img src="https://img.shields.io/badge/llama--cpp-ready-orange" alt="llama.cpp">
</p>

<p align="center">
  <a href="#быстрый-старт">Быстрый старт</a> •
  <a href="#установка">Установка</a> •
  <a href="#команды">Команды</a> •
  <a href="#дорожная-карта">Дорожная карта</a>
</p>

---

TermuCoderAI — **консольная оболочка** вокруг локальной языковой модели. Вся
генерация происходит через llama.cpp на вашем железе: нет ключей API, нет
облака, полная приватность.

> Работает на **Termux (Android)**, **Linux** и **Windows**.

## Содержание

- [Быстрый старт](#быстрый-старт)
- [Установка](#установка)
- [Команды](#команды)
  - [ask](#ask--вопрос-модели)
  - [chat](#chat--интерактивный-чат)
  - [edit](#edit--ai-правка-файла)
  - [memory](#memory--память-проекта)
  - [analyze](#analyze--анализ-проекта)
  - [config](#config--настройки)
  - [server](#server--управление-сервером)
  - [model](#model--управление-моделями)
  - [plugin](#plugin--плагины)
  - [setup](#setup--настройка-окружения)
  - [doctor](#doctor--диагностика)
- [Конфигурация](#конфигурация)
- [Структура проекта](#структура-проекта)
- [Дорожная карта](#дорожная-карта)

## Быстрый старт

```bash
# 1. Установка
bash installers/termux/install.sh    # Termux
bash installers/linux/install.sh     # Linux
installers\windows\install.bat       # Windows

# 2. Запуск сервера
termucoder server start

# 3. Задайте вопрос
termucoder ask "Напиши функцию для бинарного поиска"

# 4. Или начните чат
termucoder chat
```

## Установка

### Автоматическая (рекомендуется)

| ОС       | Команда                                  |
|----------|------------------------------------------|
| Termux   | `bash installers/termux/install.sh`      |
| Linux    | `bash installers/linux/install.sh`       |
| Windows  | Запустите `installers/windows/install.bat`|

### Вручную

```bash
git clone https://github.com/vasilijpavlov693-arch/TermuCoderAI.git
cd TermuCoderAI
pip install -e .
```

Требуется: Python 3.11+, llama.cpp с `llama-server`, GGUF-модель.

## Команды

### ask — вопрос модели

```bash
termucoder ask "Чем list отличается от tuple?"
```

Одиночный запрос без сохранения истории.

### chat — интерактивный чат

```bash
termucoder chat              # новая или последняя сессия
termucoder chat --new        # принудительно новая
termucoder chat --list       # список сессий
termucoder chat --session ID  # продолжить сессию
termucoder chat --delete ID   # удалить сессию
termucoder chat --no-memory  # без авто-запоминания
```

Команды внутри чата: `/exit`, `/quit`, `/clear`.

### edit — AI-правка файла

```bash
termucoder edit script.py "замени pass на print('hello')"
termucoder edit --preview script.py "добавь docstring"
termucoder edit --undo script.py
```

| Флаг        | Действие                                      |
|-------------|-----------------------------------------------|
| без флагов  | Показывает diff и применяет изменения         |
| `--preview` | Только показывает diff, файл не меняется      |
| `--undo`    | Восстанавливает файл из `.bak` резервной копии|

### memory — память проекта

```bash
termucoder memory add "API использует REST v2" --tags "api,rest"
termucoder memory list
termucoder memory search "API"
termucoder memory delete <id>
termucoder memory context
```

Знания автоматически подставляются в контекст AI при анализе проекта.

### analyze — анализ проекта

```bash
termucoder analyze .                         # структура и сводка
termucoder analyze . --ask "где здесь API?"  # вопрос по проекту
termucoder analyze . --json                  # вывод в JSON
```

### config — настройки

```bash
termucoder config                             # показать всё
termucoder config set generation.temperature 0.4
termucoder config set model.path "~/AI/models/model.gguf"
```

### server — управление сервером

```bash
termucoder server start    # запустить
termucoder server stop     # остановить
termucoder server restart  # перезапустить
termucoder server status   # статус
```

### model — управление моделями

```bash
termucoder model list                          # список моделей
termucoder model info                          # текущая модель
termucoder model use qwen2.5-coder-1.5b.gguf  # выбрать модель
```

### plugin — плагины

```bash
termucoder plugin list   # список загруженных плагинов
termucoder plugin info   # информация о плагинах
```

Плагины хранятся в `~/.termucoder/plugins/` (глобальные) и `.termucoder/plugins/` (проектные).

### setup — настройка окружения

```bash
termucoder setup           # базовая
termucoder setup --full    # полная (зависимости + llama.cpp + модель)
```

### doctor — диагностика

```bash
termucoder doctor  # проверит Python, llama-server, модель, API
```

## Конфигурация

Настройки хранятся в `settings.json`:

```json
{
  "server": { "host": "127.0.0.1", "port": 8080 },
  "model": { "name": "model.gguf", "path": "~/AI/models/model.gguf" },
  "generation": { "temperature": 0.2, "max_tokens": 512 },
  "memory": { "enabled": true, "auto_learn": true }
}
```

## Структура проекта

```
TermuCoderAI/
├── termucoder/
│   ├── cli.py            Точка входа, разбор команд
│   ├── api.py            Клиент LLM (ask / chat / ask_context)
│   ├── config.py         Работа с settings.json
│   ├── editor.py         AI-редактор кода (diff / preview / undo)
│   ├── search_replace.py Механизм SEARCH/REPLACE
│   ├── edit_validator.py Валидация ответов LLM
│   ├── diff.py           Генерация unified diff
│   ├── history.py        История чата (сессии)
│   ├── memory.py         Память проектов (знания)
│   ├── search.py         Сканирование файлов проекта
│   ├── context.py        Анализ проекта и контекст для AI
│   ├── server.py         Управление llama-server
│   ├── model.py          Управление моделями
│   ├── plugins/          Система плагинов
│   │   ├── __init__.py   Реестр плагинов
│   │   └── loader.py     Загрузчик плагинов
│   ├── setup.py          Первоначальная настройка
│   ├── doctor.py         Диагностика системы
│   ├── prompts.py        Системные промпты
│   ├── utils.py          Общие helper-функции
│   └── version.py        Номер версии
├── installers/           Скрипты установки
├── tests/                Юнит-тесты (79 тестов)
├── settings.example.json Пример конфигурации
├── VERSION
├── pyproject.toml
└── README.md
```

## Дорожная карта

| Версия | Статус | Назначение                                    |
|--------|--------|-----------------------------------------------|
| v0.4   | ✅ Done | Анализ проектов                               |
| v0.5   | ✅ Done | AI-редактор кода (diff / preview / undo)      |
| v0.6   | ✅ Done | Память проектов (локальное хранилище знаний)  |
| v0.7   | ✅ Done | Расширения и плагины                          |
| v0.8   | 🔜     | Полировка (цветной вывод, автодополнение)     |
| v1.0   | 📋     | Первый стабильный релиз                       |

## Лицензия

Открытый исходный код, доступно для всех.

<div align="center">

# 💿 cue-splitter

**Массовая нарезка образов FLAC + CUE на отдельные пронумерованные треки с тегами**

[![CI](https://github.com/YOUR_USERNAME/cue-splitter/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/cue-splitter/actions)
![Python](https://img.shields.io/badge/python-3.8%2B-blue?logo=python&logoColor=white)
![FFmpeg](https://img.shields.io/badge/requires-ffmpeg-green?logo=ffmpeg&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

</div>

---

Скачали дискографию, а каждый альбом — один большой `.flac` и `.cue`? Этот скрипт обойдёт всю коллекцию, разрежет каждый образ на треки **без перекодирования** (FLAC → FLAC), проставит теги и аккуратно уберёт оригиналы в сторону.

## ✨ Возможности

- 📂 **Рекурсивный обход** — достаточно указать корневую папку с музыкой
- ✂️ **Точная нарезка** по `INDEX 01` из CUE (разрешение 1/75 секунды)
- 🏷️ **Теги из CUE**: название, исполнитель, альбом, исполнитель альбома, номер трека, всего треков, год, жанр
- 🔢 **Нумерация в имени файла**: `01. New Born.flac`
- 🧪 **Режим `--dry-run`** — посмотреть, что будет сделано, ничего не трогая
- 🛡️ **Безопасность**: оригиналы не удаляются, а переносятся в `_original/`; при ошибке ffmpeg созданные треки откатываются
- 🔤 **Кодировки CUE**: UTF-8 (с BOM), CP1251, CP1252 — кракозябр в русских альбомах не будет
- 🚫 **Без зависимостей** — только стандартная библиотека Python и ffmpeg

## 📁 Как это выглядит

**До:**

```text
Muse/
└── 2001 - Origin of Symmetry/
    ├── Muse - Origin of Symmetry.flac
    └── Muse - Origin of Symmetry.cue
```

**После:**

```text
Muse/
└── 2001 - Origin of Symmetry/
    ├── 01. New Born.flac
    ├── 02. Bliss.flac
    ├── 03. Space Dementia.flac
    ├── ...
    └── _original/
        ├── Muse - Origin of Symmetry.flac
        └── Muse - Origin of Symmetry.cue
```

## 🚀 Установка

1. Установите [Python 3.8+](https://www.python.org/downloads/)
2. Установите [ffmpeg](https://ffmpeg.org/download.html) и убедитесь, что он доступен в `PATH`:

   | ОС | Команда |
   |---|---|
   | Windows | `winget install Gyan.FFmpeg` |
   | macOS | `brew install ffmpeg` |
   | Debian/Ubuntu | `sudo apt install ffmpeg` |

3. Скачайте скрипт:

   ```bash
   git clone https://github.com/ebelvladimir/cue-splitter
   cd cue-splitter
   ```

## 📖 Использование

Сначала **пробный запуск** — ничего не изменяется, только выводится план:

```bash
python split_cue.py "D:\Музыка\Muse Japan CD" --dry-run
```

Если всё выглядит правильно — запускаем по-настоящему:

```bash
python split_cue.py "D:\Музыка\Muse Japan CD"
```

Пример вывода:

```text
D:\Музыка\Muse Japan CD\Muse\Origin of Symmetry
  01. New Born.flac
  02. Bliss.flac
  03. Space Dementia.flac

Готово: обработано 12, пропущено 1
```

### Параметры

| Параметр | Описание |
|---|---|
| `root` | Корневая папка, в которой (рекурсивно) ищутся `.cue` файлы |
| `--dry-run` | Только показать, что будет сделано, без изменений на диске |

## ⚙️ Как это работает

1. Находит все `*.cue` (папки `_original` пропускаются — повторный запуск безопасен).
2. Разбирает CUE: теги альбома и треков, время начала каждого трека (`INDEX 01`).
3. Находит соответствующий FLAC: по имени из `FILE`, затем одноимённый, затем единственный `.flac` в папке.
4. Для каждого трека вызывает `ffmpeg -ss <начало> -t <длительность>` и записывает теги.
5. Переносит исходные `.flac` и `.cue` в `_original/`.

## ⚠️ Ограничения

Альбом **пропускается** (с понятным сообщением), если:

- в CUE больше одной записи `FILE` (образ разбит на несколько файлов);
- не удалось прочитать время треков;
- не найден FLAC-файл.

Дополнительно:

- Поддерживается формат FLAC. Для APE/WV/WAV образов нужен другой вход.
- Обложки (`cover.jpg`) остаются в папке как есть.
- Пре-гэпы (`INDEX 00`) не вырезаются отдельно — они остаются в конце предыдущего трека.

## 🧪 Тесты

```bash
pip install pytest
pytest -v
```

## 🗺️ Планы

- [ ] Поддержка образов APE / WV / WAV
- [ ] Поддержка CUE с несколькими `FILE`
- [ ] Встраивание обложки в теги
- [ ] Параметр `--keep-originals` / `--delete-originals`
- [ ] Шаблон имени файла (`--template "{num}. {artist} - {title}"`)
- [ ] Параллельная обработка альбомов

## 🤝 Участие в разработке

Issues и Pull Request'ы приветствуются. Если какой-то CUE не обработался — приложите его (без аудио) к issue.

## 📄 Лицензия

[MIT](LICENSE)

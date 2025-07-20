# 💰 Telegram Bot – Financial Assistant

Личный ассистент в Telegram для учёта расходов.  
Бот помогает фиксировать траты по категориям, анализировать статистику и визуализировать расходы в диаграммах.

Ссылка на бота: [Financial assistant](https://t.me/FinanceAssit_bot)

## Возможности

- 📌 Создание, переименование и удаление категорий
- ✍️ Запись расходов с указанием суммы и категории
- 📊 Просмотр статистики за последнюю неделю или месяц
- 📈 Отображение диаграмм:
  - Столбчатая диаграмма всех трат
  - Круговая диаграмма трёх основных категорий и остального

---
## 🖼️ Пример работы

### Старт
<img src="images/start.jpg" width="45%">

### Запись расходов
<img src="images/write_down_expense_1.jpg" style="width: 45%; display: inline-block; margin-right: 1%;">
<img src="images/write_down_expense_2.jpg" style="width: 45%; display: inline-block;">

### Статистика
<img src="images/statistics_interval.jpg" style="width: 45%; display: inline-block; margin-right: 1%;">
<img src="images/statistics.jpg" style="width: 45%; display: inline-block;">

### Основные траты
<img src="images/basic_expense_interval.jpg" style="width: 45%; display: inline-block; margin-right: 1%;">
<img src="images/basic_expense.jpg" style="width: 45%; display: inline-block;">

### Диаграммы

#### Столбчатая диаграмма (общая статистика)
<img src="images/full_statistics.jpg" width="45%">

#### Круговая диаграмма (основные траты)
<img src="images/full_basic_expense.jpg" width="45%">

### 🚀 Как запустить

1. Клонируй проект:
```bash git clone https://github.com/твой-профиль/your-bot.git ```
2. Установи зависимости: pip install -r requirements.txt
3. Создай .env файл и добавь в него свой Telegram токен : BOT_TOKEN=your_token_here
4. Запусти бота: python main.py

import matplotlib
matplotlib.use('Agg') # Установка бэкенда Matplotlib перед импортом pyplot
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from math import ceil
import os
import tempfile


def generate_expense_charts(data: dict, save_dir: str = 'temp_charts') -> list[str]:
    """
    Генерирует столбчатые диаграммы расходов по категориям, разбивая их на несколько графиков,
    если категорий слишком много. Диаграммы сохраняются во временные файлы.

    Args:
        data (dict): Словарь с данными для построения графика. Ожидаемый формат:
                     {
                         'expenses_by_category': [
                             {'name': 'Категория1', 'amount': 1000.0, 'is_deleted': False},
                             {'name': 'Категория2', 'amount': 500.0, 'is_deleted': True},
                             ...
                         ],
                         'total_expenses': 1500.0
                     }
        save_dir (str): Директория для сохранения временных файлов графиков. По умолчанию 'temp_charts'.

    Returns:
        list[str]: Список путей к сгенерированным PNG-файлам диаграмм.
    """
    # Настройка шрифтов для Matplotlib, чтобы обеспечить корректное отображение кириллицы
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans']
    # Отключение использования минуса в Unicode, чтобы избежать проблем с отображением
    plt.rcParams['axes.unicode_minus'] = False

    # Создание директории для сохранения графиков, если она еще не существует
    os.makedirs(save_dir, exist_ok=True)

    category_items = []
    # Подготовка данных для построения графика
    for item in data['expenses_by_category']:
        name = item['name']
        amount = float(item['amount'])
        is_deleted = item.get('is_deleted', False) # Получаем статус удаления, по умолчанию False

        # Формирование названия категории для отображения на графике
        # Если категория удалена, добавляем пометку "(Удалено)"
        label = f"{name}\n(Удалено)" if is_deleted else name
        # Определение цвета столбика: красный для удаленных, синий для активных
        color = '#e74c3c' if is_deleted else '#5dade2'

        category_items.append((label, amount, color))

    # Сортировка категорий по сумме трат для лучшей визуализации
    category_items.sort(key=lambda x: x[1])
    # Распаковка отсортированных данных на отдельные списки
    categories, values, colors = zip(*category_items)

    total_amount = data['total_expenses']

    # Параметры для разбиения графика на несколько частей
    min_per_chart = 4  # Минимальное количество столбцов на одном графике
    max_per_chart = 7  # Максимальное количество столбцов на одном графике
    total = len(categories) # Общее количество категорий

    # Расчет количества графиков, чтобы уместить все категории
    num_charts = ceil(total / max_per_chart)
    # Корректировка количества графиков, чтобы избежать слишком малого числа столбцов на графике
    while num_charts > 1 and total / num_charts < min_per_chart:
        num_charts -= 1

    # Расчет размера "куска" (количество категорий) для каждого графика
    chunk_size = ceil(total / num_charts)
    dark_bg = '#1e1f26' # Темный фон для графиков
    chart_paths = [] # Список для хранения путей к сгенерированным файлам

    # Цикл по количеству необходимых графиков
    for i in range(num_charts):
        start = i * chunk_size
        end = start + chunk_size
        # Выделение подмножества данных для текущего графика
        cat_part = categories[start:end]
        val_part = values[start:end]
        color_part = colors[start:end]

        # Настройка размера фигуры в зависимости от количества столбцов
        fig_width = max(8, round(len(cat_part) * 1.2))
        fig, ax = plt.subplots(figsize=(fig_width, 5))
        # Установка цвета фона фигуры и осей
        fig.patch.set_facecolor(dark_bg)
        ax.set_facecolor(dark_bg)

        # Построение столбчатой диаграммы
        bars = ax.bar(cat_part, val_part, color=color_part, width=0.6)
        max_val = max(val_part) # Максимальное значение на текущем графике
        padding = max_val * 0.05 # Отступ для текста над столбцами

        # Добавление числовых значений над каждым столбцом
        for bar in bars:
            yval = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2, # Позиция по X (центр столбца)
                yval + padding, # Позиция по Y (над столбцом с отступом)
                f'{int(yval):,} ₽'.replace(',', ' '), # Форматирование значения (с пробелами для тысяч)
                ha='center', va='bottom', # Горизонтальное и вертикальное выравнивание
                color='white' # Цвет текста
            )

        # Установка заголовка графика
        title = 'Статистика расходов' if num_charts == 1 else f'Статистика расходов ({i + 1}/{num_charts})'
        ax.set_title(title, color='white', fontsize=14)

        # Добавление общей суммы расходов на первый график
        if i == 0:
            ax.text(
                0.01, 0.95, # Координаты в относительном пространстве осей
                f'Всего: {int(total_amount):,} ₽'.replace(',', ' '),
                transform=ax.transAxes, # Использование относительных координат
                ha='left', va='top', # Выравнивание
                fontsize=12,
                color='white'
            )

        # Настройка цвета меток осей и границ графиков
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')

        # Настройка сетки по оси Y
        ax.yaxis.grid(True, linestyle='--', color='white', alpha=0.2)
        # Форматирование меток на оси Y (добавление пробелов для тысяч и знака рубля)
        ax.yaxis.set_major_formatter(
            FuncFormatter(lambda x, _: f"{int(x):,}".replace(',', ' ') if x >= 1000 else str(int(x)))
        )

        # Установка пределов оси Y
        plt.ylim(0, max_val + padding * 4)
        # Автоматическая настройка отступов для плотного размещения элементов
        plt.tight_layout(rect=(0.0, 0.1, 1, 1))  # Увеличен нижний отступ для подписей, если они длинные

        # Сохранение графика во временный файл
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png', prefix=f'chart_{i + 1}_', dir='temp_charts')
        plt.savefig(temp_file.name, dpi=200, bbox_inches='tight') # Сохранение с высоким разрешением
        plt.close() # Закрытие фигуры для освобождения памяти
        chart_paths.append(temp_file.name) # Добавление пути к файлу в список

    return chart_paths

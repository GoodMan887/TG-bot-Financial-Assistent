import matplotlib.pyplot as plt
from itertools import cycle, islice
import tempfile


def generate_top_categories_pie(data: dict) -> str:
    """
    Генерирует круговую диаграмму (pie chart) для визуализации основных категорий расходов.
    Включает сегмент 'Остальное', если сумма мелких трат не равна нулю.
    График сохраняется в PNG файл.

    Args:
        data (dict): Словарь с данными для построения круговой диаграммы. Ожидаемый формат:
                     {
                         'top_categories': [
                             {'name': 'Категория1', 'amount': 15000.0},
                             {'name': 'Категория2', 'amount': 8000.0},
                             ...
                         ],
                         'other_sum': 3000.0
                     }

    Returns:
        str: Путь к сгенерированному PNG-файлу круговой диаграммы.
    """
    # Извлечение названий категорий и их сумм из входных данных
    categories = [item['name'] for item in data['top_categories']]
    amounts = [item['amount'] for item in data['top_categories']]
    other_sum = data['other_sum']  # Сумма расходов, не вошедших в топ категорий

    # Если сумма "Остального" не равна нулю, добавляем ее как отдельный сегмент
    if other_sum != 0.0:
        categories.append('Остальное')
        amounts.append(other_sum)

    # Базовая палитра цветов для сегментов диаграммы
    # Эти цвета будут циклически повторяться, если категорий больше, чем цветов
    base_colors = ['#5dade2', '#a569bd', '#48c9b0', '#58d68d']
    # Создание списка цветов, достаточного для всех категорий, с использованием цикла
    colors = list(islice(cycle(base_colors), len(categories)))
    dark_bg = '#1e1f26'  # Цвет фона для графика (темный, для лучшего контраста с белым текстом)

    # Настройка стиля Matplotlib для корректного отображения шрифтов (особенно кириллицы)
    plt.rcParams['font.family'] = 'DejaVu Sans'
    # Отключение обработки символа минуса в Unicode, чтобы избежать проблем с отображением
    plt.rcParams['axes.unicode_minus'] = False

    # Создание фигуры (окна графика) и осей (области рисования)
    fig, ax = plt.subplots(figsize=(8, 6))
    # Установка цвета фона для всей фигуры и для области рисования осей
    fig.patch.set_facecolor(dark_bg)
    ax.set_facecolor(dark_bg)

    # Вспомогательная функция для форматирования текста внутри сегментов круговой диаграммы.
    # Она будет показывать процент от общего количества и абсолютное значение в рублях.
    def make_autopct(values):
        def autopct(pct):
            # Вычисляем абсолютное значение расхода для текущего сегмента
            val = int(round(pct / 100. * sum(values)))
            # Форматируем строку: процент, новая строка, сумма с разделителями тысяч и знаком рубля
            return f'{pct:.1f}%\n{val:,} ₽'.replace(',', ' ')

        return autopct

    # Построение круговой диаграммы
    wedges, texts, autotexts = ax.pie(
        amounts,  # Данные для размеров сегментов
        labels=categories,  # Метки для каждого сегмента (названия категорий)
        colors=colors,  # Цвета для каждого сегмента
        startangle=90,  # Угол, с которого начинается первый сегмент (сверху)
        counterclock=False,  # Направление построения сегментов (по часовой стрелке)
        autopct=make_autopct(amounts),  # Функция для форматирования текста внутри сегментов
        wedgeprops={'edgecolor': 'white'},  # Свойства границ между сегментами (белый цвет)
        textprops={'color': 'white', 'fontsize': 11},  # Свойства текста меток категорий
    )

    # Дополнительная настройка размера шрифта для подписей процентов/сумм и названий категорий
    for autotext in autotexts:
        autotext.set_fontsize(11)  # Размер шрифта для процентов/сумм
    for text in texts:
        text.set_fontsize(12)  # Размер шрифта для названий категорий

    total = sum(amounts)  # Общая сумма всех расходов (для заголовка)

    # Установка заголовка графика
    ax.set_title(
        'Основные траты\n' +  # Основной заголовок
        f'Общая сумма: {int(total):,} ₽'.replace(',', ' '),  # Подзаголовок с общей суммой, форматирование
        color='white',  # Цвет заголовка
        fontsize=14,  # Размер шрифта заголовка
        weight='bold',  # Жирный шрифт
        loc='center'  # Выравнивание заголовка по центру
    )

    # Автоматическая корректировка отступов, чтобы все элементы поместились на фигуре
    plt.tight_layout()

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    chart_path = tmp_file.name
    tmp_file.close()  # Закрываем, чтобы Matplotlib мог записать файл по пути

    # Сохранение фигуры в PNG файл с высоким разрешением и без лишних полей
    plt.savefig(chart_path, dpi=200, bbox_inches='tight')
    # Закрытие фигуры для освобождения памяти, это важно, особенно при генерации множества графиков
    plt.close(fig)

    return chart_path

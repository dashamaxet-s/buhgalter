"""
Модуль visualizer.py
Содержит класс FinanceVisualizer.
Отвечает исключительно за построение круговых диаграмм (pie charts)
на основе переданных данных. Инкапсулирует логику визуализации,
соответствует принципу единственной ответственности (SRP).
Названия классов — CamelCase, методов — snake_case (PEP 8).
"""

import matplotlib.pyplot as plt
from typing import List, Tuple


class FinanceVisualizer:
    """
    Класс FinanceVisualizer строит круговые диаграммы расходов и доходов
    по категориям, используя библиотеку matplotlib.
    """

    @staticmethod
    def plot_pie_chart(
        data: List[Tuple[str, float]],
        title: str = "Расходы по категориям",
        save_path: str = "",
    ) -> None:
        """
        Строит круговую диаграмму на основе переданного списка данных.
        Параметры:
            data (List[Tuple[str, float]]): Список кортежей (категория, сумма).
            title (str): Заголовок диаграммы.
            save_path (str): Если указан, сохраняет диаграмму в файл.
                             Иначе отображает в интерактивном окне.
        Если data пуст, выводится сообщение, диаграмма не строится.
        """
        if not data:
            print("Нет данных для построения диаграммы.")
            return

        labels = [item[0] for item in data]
        sizes = [item[1] for item in data]

        # Настройка визуального стиля
        plt.figure(figsize=(7, 7))
        colors = plt.cm.Paired.colors[: len(labels)] if len(labels) <= 12 else None

        # Построение круговой диаграммы
        wedges, texts, autotexts = plt.pie(
            sizes,
            labels=None,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
            pctdistance=0.85,
        )

        # Легенда
        legend_labels = [
            f"{label} ({size:.2f} руб.)" for label, size in zip(labels, sizes)
        ]
        plt.legend(
            wedges,
            legend_labels,
            title="Категории",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
        )

        plt.title(title, fontsize=14, fontweight="bold")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Диаграмма сохранена: {save_path}")
        else:
            plt.show()
        plt.close()


if __name__ == "__main__":
    # Тестовый пример
    test_data = [("Еда", 5000), ("Транспорт", 3000), ("Развлечения", 2000)]
    visualizer = FinanceVisualizer()
    visualizer.plot_pie_chart(test_data, "Тестовая диаграмма расходов")
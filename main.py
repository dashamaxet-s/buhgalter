"""
Модуль main.py
Главный модуль приложения «Персональный бухгалтер».
Содержит класс PersonalAccountantApp — графический интерфейс на tkinter.
Обеспечивает взаимодействие пользователя с FinanceManager и FinanceVisualizer.
Архитектура: GUI вызывает методы моделей и визуализатора,
не вмешиваясь в их внутреннюю логику (SRP).
Стиль: имена классов — CamelCase, имена методов и переменных — snake_case (PEP 8).
Максимальная длина строки ограничена 79 символами.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
from typing import Optional

from models import FinanceManager, Transaction
from visualizer import FinanceVisualizer


class PersonalAccountantApp:
    """
    Основной класс GUI-приложения.
    Создаёт окно, виджеты ввода, таблицу записей, кнопки управления,
    а также отображает сводную информацию (баланс, итоги).
    """

    def __init__(self, root: tk.Tk):
        """
        Инициализация главного окна.
        Параметры:
            root (tk.Tk): Корневой объект окна tkinter.
        """
        self.root = root
        self.root.title("Персональный бухгалтер")
        self.root.geometry("1100x700")
        self.root.minsize(950, 600)
        self.root.resizable(True, True)

        # Инициализация менеджера финансов и визуализатора
        self.manager = FinanceManager()
        self.visualizer = FinanceVisualizer()

        # Переменные для формы ввода
        self.type_var = tk.StringVar(value="expense")
        self.category_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.date_var = None  # Будет привязан к DateEntry

        # Переменная для хранения ID редактируемой записи
        self.editing_id: Optional[int] = None

        # Построение интерфейса
        self._create_widgets()

        # Загрузка данных в таблицу
        self._refresh_table()

        # Обновление сводки
        self._update_summary()

    def _create_widgets(self) -> None:
        """
        Создаёт и размещает все виджеты GUI:
        - Фрейм ввода данных
        - Фрейм с кнопками управления
        - Таблицу (Treeview) для отображения записей
        - Фрейм сводной информации
        """
        # Настройка стиля
        style = ttk.Style()
        style.theme_use("clam")

        # === Фрейм ввода данных ===
        input_frame = ttk.LabelFrame(self.root, text="Добавление / редактирование записи", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        # Тип операции
        ttk.Label(input_frame, text="Тип:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        type_frame = ttk.Frame(input_frame)
        type_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(type_frame, text="Расход", variable=self.type_var,
                        value="expense", command=self._on_type_change).pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="Доход", variable=self.type_var,
                        value="income", command=self._on_type_change).pack(side=tk.LEFT, padx=10)

        # Категория
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var,
                                           state="readonly", width=20)
        self.category_combo.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

        # Сумма
        ttk.Label(input_frame, text="Сумма (руб.):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=22)
        amount_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        # Дата
        ttk.Label(input_frame, text="Дата:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.date_entry = DateEntry(input_frame, width=20, background='darkblue',
                                     foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        self.date_entry.set_date(date.today())

        # Описание
        ttk.Label(input_frame, text="Описание:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        desc_entry = ttk.Entry(input_frame, textvariable=self.description_var, width=60)
        desc_entry.grid(row=2, column=1, columnspan=3, sticky=tk.W + tk.E, padx=5, pady=2)

        # === Фрейм кнопок (адаптивный) ===
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        for i in range(7):
            button_frame.columnconfigure(i, weight=1)

        buttons_data = [
            ("Добавить запись", self._add_transaction),
            ("Сохранить изменения", self._save_edit),
            ("Отменить", self._cancel_edit),
            ("Удалить запись", self._delete_transaction),
            ("Диаграмма расходов", self._show_expense_chart),
            ("Диаграмма доходов", self._show_income_chart),
            ("Обновить", self._refresh_all),
        ]

        for i, (text, command) in enumerate(buttons_data):
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.grid(row=0, column=i, padx=2, pady=2, sticky=tk.E + tk.W)

        # === Таблица записей ===
        table_frame = ttk.LabelFrame(self.root, text="Список записей", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Создание Treeview с колонками
        columns = ("id", "type", "category", "amount", "date", "description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Заголовки колонок
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="Тип")
        self.tree.heading("category", text="Категория")
        self.tree.heading("amount", text="Сумма (руб.)")
        self.tree.heading("date", text="Дата")
        self.tree.heading("description", text="Описание")

        # Ширина колонок
                # Фиксированная ширина колонок + запрет растягивания
        self.tree.column("id", width=40, minwidth=40, stretch=False, anchor=tk.CENTER)
        self.tree.column("type", width=70, minwidth=70, stretch=False, anchor=tk.CENTER)
        self.tree.column("category", width=110, minwidth=110, stretch=False, anchor=tk.CENTER)
        self.tree.column("amount", width=100, minwidth=100, stretch=False, anchor=tk.CENTER)
        self.tree.column("date", width=90, minwidth=90, stretch=False, anchor=tk.CENTER)
        self.tree.column("description", width=200, minwidth=100, stretch=True, anchor=tk.W)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Привязка двойного клика к редактированию
        self.tree.bind("<Double-1>", self._on_row_double_click)

        # === Фрейм сводной информации ===
        summary_frame = ttk.LabelFrame(self.root, text="Сводка", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)

        self.summary_income_label = ttk.Label(summary_frame, text="Доходы: 0.00 руб.",
                                              font=("Arial", 10))
        self.summary_income_label.pack(side=tk.LEFT, padx=15)

        self.summary_expense_label = ttk.Label(summary_frame, text="Расходы: 0.00 руб.",
                                               font=("Arial", 10))
        self.summary_expense_label.pack(side=tk.LEFT, padx=15)

        self.summary_balance_label = ttk.Label(summary_frame, text="Баланс: 0.00 руб.",
                                               font=("Arial", 10, "bold"))
        self.summary_balance_label.pack(side=tk.LEFT, padx=15)

        # Инициализация категорий
        self._on_type_change()

    def _on_type_change(self) -> None:
        """
        Обработчик смены типа операции (доход/расход).
        Обновляет список доступных категорий в выпадающем списке.
        """
        if self.type_var.get() == "expense":
            categories = self.manager.PREdefined_CATEGORIES_EXPENSE
        else:
            categories = self.manager.PREdefined_CATEGORIES_INCOME
        self.category_combo["values"] = categories
        if categories:
            self.category_var.set(categories[0])

    def _add_transaction(self) -> None:
        """
        Добавляет новую запись в БД на основе данных из формы.
        Выполняет валидацию ввода (сумма должна быть положительным числом).
        После добавления очищает форму и обновляет таблицу и сводку.
        """
        # Валидация суммы
        try:
            amount = float(self.amount_var.get().strip())
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной.")
        except ValueError:
            messagebox.showerror("Ошибка ввода",
                                 "Введите корректную положительную сумму.")
            return

        category = self.category_var.get().strip()
        trans_date = self.date_entry.get()
        trans_type = self.type_var.get()
        description = self.description_var.get().strip()

        transaction = Transaction(
            amount=amount,
            category=category,
            trans_date=trans_date,
            trans_type=trans_type,
            description=description,
        )

        self.manager.add_transaction(transaction)
        self._clear_form()
        self._refresh_table()
        self._update_summary()
        messagebox.showinfo("Успех", "Запись добавлена.")

    def _refresh_table(self, filter_type: Optional[str] = None) -> None:
        """
        Обновляет содержимое таблицы Treeview.
        Параметры:
            filter_type (str или None): Фильтр по типу ('income', 'expense', None — все).
        """
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        transactions = self.manager.get_all_transactions(filter_type)
        for t in transactions:
            type_display = "Доход" if t.trans_type == "income" else "Расход"
            self.tree.insert(
                "",
                tk.END,
                values=(t.id, type_display, t.category, f"{t.amount:.2f}",
                        t.date, t.description),
            )

    def _update_summary(self) -> None:
        """Обновляет сводную информацию (доходы, расходы, баланс)."""
        total_income = self.manager.get_total_by_type("income")
        total_expense = self.manager.get_total_by_type("expense")
        balance = self.manager.get_balance()

        self.summary_income_label.config(text=f"Доходы: {total_income:.2f} руб.")
        self.summary_expense_label.config(text=f"Расходы: {total_expense:.2f} руб.")
        self.summary_balance_label.config(text=f"Баланс: {balance:.2f} руб.")

        # Проверка бюджета (каждые 5 вызовов)
        if not hasattr(self, '_budget_check_count'):
            self._budget_check_count = 0
        self._budget_check_count += 1
        if self._budget_check_count >= 5:
            self._show_category_status()

        # Цветовая индикация баланса
        if balance >= 0:
            self.summary_balance_label.config(foreground="green")
        else:
            self.summary_balance_label.config(foreground="red")

    def _clear_form(self) -> None:
        """
        Очищает поля формы ввода и сбрасывает режим редактирования.
        """
        self.amount_var.set("")
        self.description_var.set("")
        self.date_entry.set_date(date.today())
        self.editing_id = None
        self._on_type_change()

    def _on_row_double_click(self, event: tk.Event) -> None:
        """
        Обработчик двойного клика по строке таблицы.
        Загружает данные выбранной записи в форму для редактирования.
        Параметры:
            event (tk.Event): Событие клика.
        """
        selected_item = self.tree.selection()
        if not selected_item:
            return
        values = self.tree.item(selected_item[0])["values"]
        trans_id = values[0]
        transaction = self.manager.get_transaction_by_id(trans_id)
        if transaction:
            self.editing_id = transaction.id
            self.type_var.set(transaction.trans_type)
            self._on_type_change()
            self.category_var.set(transaction.category)
            self.amount_var.set(str(transaction.amount))
            self.date_entry.set_date(transaction.date)
            self.description_var.set(transaction.description)

    def _save_edit(self) -> None:
        """
        Сохраняет изменения отредактированной записи в БД.
        Если запись не выбрана для редактирования, выводит предупреждение.
        """
        if self.editing_id is None:
            messagebox.showwarning("Редактирование",
                                   "Сначала выберите запись двойным кликом.")
            return

        try:
            amount = float(self.amount_var.get().strip())
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной.")
        except ValueError:
            messagebox.showerror("Ошибка ввода",
                                 "Введите корректную положительную сумму.")
            return

        transaction = Transaction(
            trans_id=self.editing_id,
            amount=amount,
            category=self.category_var.get().strip(),
            trans_date=self.date_entry.get(),
            trans_type=self.type_var.get(),
            description=self.description_var.get().strip(),
        )

        self.manager.update_transaction(transaction)
        self._clear_form()
        self._refresh_table()
        self._update_summary()
        messagebox.showinfo("Успех", "Запись обновлена.")

    def _cancel_edit(self) -> None:
        """
        Отменяет режим редактирования и очищает форму.
        """
        self._clear_form()
        messagebox.showinfo("Отмена", "Редактирование отменено.")

    def _delete_transaction(self) -> None:
        """
        Удаляет выбранную запись из БД после подтверждения.
        Если ничего не выбрано, выводит предупреждение.
        """
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Удаление",
                                   "Выберите запись для удаления.")
            return

        values = self.tree.item(selected_item[0])["values"]
        trans_id = values[0]

        if messagebox.askyesno("Подтверждение",
                               f"Удалить запись ID={trans_id}?"):
            self.manager.delete_transaction(trans_id)
            self._clear_form()
            self._refresh_table()
            self._update_summary()
            messagebox.showinfo("Успех", "Запись удалена.")

    def _show_expense_chart(self) -> None:
        """
        Строит и показывает круговую диаграмму расходов по категориям.
        """
        data = self.manager.get_expenses_by_category()
        if not data:
            messagebox.showinfo("Диаграмма", "Нет данных о расходах.")
            return
        self.visualizer.plot_pie_chart(data, "Расходы по категориям")

    def _show_income_chart(self) -> None:
        """
        Строит и показывает круговую диаграмму доходов по категориям.
        """
        data = self.manager.get_income_by_category()
        if not data:
            messagebox.showinfo("Диаграмма", "Нет данных о доходах.")
            return
        self.visualizer.plot_pie_chart(data, "Доходы по категориям")

    def _refresh_all(self) -> None:
        """
        Полное обновление: таблица, сводка, сброс формы.
        """
        self._refresh_table()
        self._update_summary()
        self._clear_form()

    def _show_category_status(self) -> None:
        """
        Показывает статус расходов по категориям.
        Демонстрирует полиморфизм.
        """
        from models import ExpenseCategory

        expenses = self.manager.get_expenses_by_category()
        
        # Отладка — покажем, что вообще происходит
        print(f"[DEBUG] Расходы по категориям: {expenses}")
        
        if not expenses:
            messagebox.showinfo(
                "Статус расходов",
                "Нет данных о расходах.\nДобавьте хотя бы одну запись с типом «Расход»."
            )
            return

        status_lines = []
        for category_name, total in expenses:
            cat = ExpenseCategory(category_name)
            status = cat.get_status(total)
            status_lines.append(
                f"• {category_name}: {total:.2f} руб. — {status}"
            )

        messagebox.showinfo(
            "Статус расходов",
            "Текущий статус по категориям:\n\n" + "\n".join(status_lines)
        )
  
def main():
    """Точка входа в приложение."""
    root = tk.Tk()
    app = PersonalAccountantApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
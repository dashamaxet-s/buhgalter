"""
Модуль main.py
Главный модуль приложения «ЗаяцСчетовод».
Содержит класс PersonalAccountantApp — графический интерфейс на tkinter.
Дизайн: тёмная тема, логотип ЗС, стиль современного банковского приложения.
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
    Основной класс GUI-приложения в тёмной теме.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ЗаяцСчетовод")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)
        self.root.configure(bg="#1a1a2e")

        # Инициализация менеджера финансов и визуализатора
        self.manager = FinanceManager()
        self.visualizer = FinanceVisualizer()

        # Переменные для формы ввода
        self.type_var = tk.StringVar(value="expense")
        self.category_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.description_var = tk.StringVar()

        self.editing_id: Optional[int] = None

        self._create_widgets()
        self._refresh_table()
        self._update_summary()

    def _create_widgets(self) -> None:
        """Создаёт интерфейс в тёмной теме в стиле современного банковского приложения."""

        # Настройка стилей
        style = ttk.Style()
        style.theme_use("clam")

        # Цвета тёмной темы
        accent_green = "#00c853"
        accent_red = "#ff3b30"
        accent_orange = "#ff9500"
        accent_purple = "#af52de"
        
        bg_dark = "#1a1a2e"
        bg_card = "#16213e"
        bg_input = "#0f3460"
        bg_header = "#0a0f1c"
        
        text_primary = "#e0e0e0"
        text_secondary = "#8a8a9e"
        text_muted = "#5a5a6e"
        
        border_color = "#2a2a3e"

        # Настройка стилей ttk
        style.configure("TLabel", background=bg_dark, foreground=text_primary, font=("SF Pro Text", 10))
        style.configure("TLabelframe", background=bg_dark, foreground=text_primary)
        style.configure("TLabelframe.Label", background=bg_dark, foreground=text_primary, font=("SF Pro Text", 10, "bold"))
        
        # Стиль для Combobox
        style.configure("TCombobox", font=("SF Pro Text", 10), fieldbackground=bg_input, foreground=text_primary, background=bg_input, selectbackground=accent_green)
        style.map("TCombobox", fieldbackground=[("readonly", bg_input)], selectbackground=[("readonly", accent_green)])
        
        # Стиль для Entry
        style.configure("TEntry", font=("SF Pro Text", 10), padding=8, fieldbackground=bg_input, foreground=text_primary)
        style.map("TEntry", fieldbackground=[("focus", bg_input)])
        
        # Стиль для Treeview
        style.configure("Treeview", font=("SF Pro Text", 9), rowheight=32, background=bg_card, fieldbackground=bg_card, foreground=text_primary)
        style.configure("Treeview.Heading", font=("SF Pro Text", 10, "bold"), background=bg_header, foreground=text_primary)
        style.map("Treeview.Heading", background=[("active", bg_input)])
        
        # Стиль для Scrollbar
        style.configure("Vertical.TScrollbar", background=bg_input, troughcolor=bg_dark, arrowcolor=text_secondary)

        # === Шапка приложения ===
        header_frame = tk.Frame(self.root, bg=bg_header, height=65)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Логотип и название
        logo_frame = tk.Frame(header_frame, bg=bg_header)
        logo_frame.pack(side=tk.LEFT, padx=25, pady=10)
        
        # Логотип ЗС
        logo_canvas = tk.Canvas(logo_frame, width=40, height=40, bg=bg_header, highlightthickness=0)
        logo_canvas.pack(side=tk.LEFT)
        logo_canvas.create_oval(5, 5, 35, 35, fill=accent_green, outline="")
        logo_canvas.create_text(20, 20, text="ЗС", font=("SF Pro Text", 14, "bold"), fill=bg_header)
        
        tk.Label(logo_frame, text="ЗаяцСчетовод", font=("SF Pro Text", 18, "bold"), bg=bg_header, fg=text_primary).pack(side=tk.LEFT, padx=12)

        # Дата в шапке
        date_label = tk.Label(header_frame, text=date.today().strftime("%d %B %Y"), 
                              font=("SF Pro Text", 11), bg=bg_header, fg=text_secondary)
        date_label.pack(side=tk.RIGHT, padx=25)

        # === Карточки со сводкой ===
        cards_frame = tk.Frame(self.root, bg=bg_dark)
        cards_frame.pack(fill=tk.X, padx=20, pady=(20, 15))

        # Стиль для карточек
        card_cfg = {"bg": bg_card, "relief": tk.FLAT, "bd": 0}

        # Карточка доходов
        income_card = tk.Frame(cards_frame, **card_cfg)
        income_card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6, pady=5)
        tk.Frame(income_card, bg=accent_green, height=3).pack(fill=tk.X)  # цветная полоска
        tk.Label(income_card, text="Доходы", font=("SF Pro Text", 12), bg=bg_card, fg=text_secondary).pack(pady=(14, 5))
        self.summary_income_label = tk.Label(income_card, text="0 ₽", font=("SF Pro Text", 22, "bold"), bg=bg_card, fg=accent_green)
        self.summary_income_label.pack(pady=(0, 14))

        # Карточка расходов
        expense_card = tk.Frame(cards_frame, **card_cfg)
        expense_card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6, pady=5)
        tk.Frame(expense_card, bg=accent_red, height=3).pack(fill=tk.X)
        tk.Label(expense_card, text="Расходы", font=("SF Pro Text", 12), bg=bg_card, fg=text_secondary).pack(pady=(14, 5))
        self.summary_expense_label = tk.Label(expense_card, text="0 ₽", font=("SF Pro Text", 22, "bold"), bg=bg_card, fg=accent_red)
        self.summary_expense_label.pack(pady=(0, 14))

        # Карточка баланса
        balance_card = tk.Frame(cards_frame, **card_cfg)
        balance_card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6, pady=5)
        tk.Frame(balance_card, bg=accent_orange, height=3).pack(fill=tk.X)
        tk.Label(balance_card, text="Баланс", font=("SF Pro Text", 12), bg=bg_card, fg=text_secondary).pack(pady=(14, 5))
        self.summary_balance_label = tk.Label(balance_card, text="0 ₽", font=("SF Pro Text", 22, "bold"), bg=bg_card, fg=accent_orange)
        self.summary_balance_label.pack(pady=(0, 14))

        # === Форма добавления записи ===
        form_container = tk.Frame(self.root, bg=bg_dark)
        form_container.pack(fill=tk.X, padx=20, pady=10)

        form_card = tk.Frame(form_container, bg=bg_card, relief=tk.FLAT, bd=0)
        form_card.pack(fill=tk.X, pady=5)
        
        # Внутренний контейнер
        inner_form = tk.Frame(form_card, bg=bg_card)
        inner_form.pack(fill=tk.BOTH, padx=25, pady=18)

        # Первая строка: Тип операции (переключатели)
        type_frame = tk.Frame(inner_form, bg=bg_card)
        type_frame.pack(fill=tk.X, pady=(0, 18))
        
        # Стилизованные переключатели
        btn_style = {"font": ("SF Pro Text", 11), "relief": tk.FLAT, "bd": 0, "padx": 30, "pady": 9, "cursor": "hand2"}
        
        self.expense_btn = tk.Button(type_frame, text="Расход", command=lambda: self._set_type("expense"),
                                     bg=accent_red if self.type_var.get() == "expense" else bg_input,
                                     fg="white" if self.type_var.get() == "expense" else text_secondary, **btn_style)
        self.expense_btn.pack(side=tk.LEFT, padx=(0, 12))
        
        self.income_btn = tk.Button(type_frame, text="Доход", command=lambda: self._set_type("income"),
                                    bg=accent_green if self.type_var.get() == "income" else bg_input,
                                    fg="white" if self.type_var.get() == "income" else text_secondary, **btn_style)
        self.income_btn.pack(side=tk.LEFT)

        # Вторая строка: Категория и Сумма
        row2 = tk.Frame(inner_form, bg=bg_card)
        row2.pack(fill=tk.X, pady=(0, 18))
        
        # Категория
        cat_frame = tk.Frame(row2, bg=bg_card)
        cat_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 12))
        tk.Label(cat_frame, text="Категория", font=("SF Pro Text", 10), bg=bg_card, fg=text_muted).pack(anchor=tk.W, pady=(0, 6))
        self.category_combo = ttk.Combobox(cat_frame, textvariable=self.category_var, state="readonly", font=("SF Pro Text", 11))
        self.category_combo.pack(fill=tk.X)
        
        # Сумма
        amount_frame = tk.Frame(row2, bg=bg_card)
        amount_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(12, 0))
        tk.Label(amount_frame, text="Сумма (₽)", font=("SF Pro Text", 10), bg=bg_card, fg=text_muted).pack(anchor=tk.W, pady=(0, 6))
        amount_entry = tk.Entry(amount_frame, textvariable=self.amount_var, font=("SF Pro Text", 11),
                                bg=bg_input, fg=text_primary, relief=tk.FLAT, bd=1, highlightthickness=1,
                                highlightcolor=accent_green, highlightbackground=border_color, insertbackground=text_primary)
        amount_entry.pack(fill=tk.X)

        # Третья строка: Дата и Описание
        row3 = tk.Frame(inner_form, bg=bg_card)
        row3.pack(fill=tk.X)
        
        # Дата
        date_frame = tk.Frame(row3, bg=bg_card)
        date_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 12))
        tk.Label(date_frame, text="Дата", font=("SF Pro Text", 10), bg=bg_card, fg=text_muted).pack(anchor=tk.W, pady=(0, 6))
        self.date_entry = DateEntry(date_frame, width=12, background=accent_green, foreground='white',
                                    borderwidth=0, date_pattern='yyyy-mm-dd', font=("SF Pro Text", 11),
                                    fieldbackground=bg_input, selectbackground=accent_green)
        self.date_entry.pack(fill=tk.X)
        self.date_entry.set_date(date.today())
        
        # Описание
        desc_frame = tk.Frame(row3, bg=bg_card)
        desc_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(12, 0))
        tk.Label(desc_frame, text="Описание (необязательно)", font=("SF Pro Text", 10), bg=bg_card, fg=text_muted).pack(anchor=tk.W, pady=(0, 6))
        desc_entry = tk.Entry(desc_frame, textvariable=self.description_var, font=("SF Pro Text", 11),
                              bg=bg_input, fg=text_primary, relief=tk.FLAT, bd=1, highlightthickness=1,
                              highlightcolor=accent_green, highlightbackground=border_color, insertbackground=text_primary)
        desc_entry.pack(fill=tk.X)

        # === Панель действий ===
        actions_frame = tk.Frame(inner_form, bg=bg_card)
        actions_frame.pack(fill=tk.X, pady=(22, 0))
        
        # Кнопки в тёмной теме
        btn_cfg = {"font": ("SF Pro Text", 10, "bold"), "relief": tk.FLAT, "bd": 0, "padx": 16, "pady": 10, "cursor": "hand2"}
        
        add_btn = tk.Button(actions_frame, text="➕ Добавить", command=self._add_transaction, 
                           bg=accent_green, fg="#1a1a2e", **btn_cfg)
        add_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        save_btn = tk.Button(actions_frame, text="💾 Сохранить", command=self._save_edit,
                            bg="#2196f3", fg="white", **btn_cfg)
        save_btn.pack(side=tk.LEFT, padx=4)
        
        cancel_btn = tk.Button(actions_frame, text="✖️ Отменить", command=self._cancel_edit,
                              bg="#ff9800", fg="#1a1a2e", **btn_cfg)
        cancel_btn.pack(side=tk.LEFT, padx=4)
        
        delete_btn = tk.Button(actions_frame, text="🗑️ Удалить", command=self._delete_transaction,
                              bg=accent_red, fg="white", **btn_cfg)
        delete_btn.pack(side=tk.LEFT, padx=4)
        
        chart_expense_btn = tk.Button(actions_frame, text="📊 Расходы", command=self._show_expense_chart,
                                      bg=accent_purple, fg="white", **btn_cfg)
        chart_expense_btn.pack(side=tk.LEFT, padx=4)
        
        chart_income_btn = tk.Button(actions_frame, text="📈 Доходы", command=self._show_income_chart,
                                     bg=accent_purple, fg="white", **btn_cfg)
        chart_income_btn.pack(side=tk.LEFT, padx=4)
        
        refresh_btn = tk.Button(actions_frame, text="🔄 Обновить", command=self._refresh_all,
                                bg="#607d8b", fg="white", **btn_cfg)
        refresh_btn.pack(side=tk.LEFT, padx=(8, 0))

        # === Таблица транзакций ===
        table_container = tk.Frame(self.root, bg=bg_dark)
        table_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        table_card = tk.Frame(table_container, bg=bg_card, relief=tk.FLAT, bd=0)
        table_card.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок таблицы
        tk.Label(table_card, text="История операций", font=("SF Pro Text", 14, "bold"), 
                bg=bg_card, fg=text_primary).pack(anchor=tk.W, padx=22, pady=(16, 12))
        
        # Treeview
        columns = ("id", "type", "category", "amount", "date", "description")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", height=14)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="Тип")
        self.tree.heading("category", text="Категория")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("date", text="Дата")
        self.tree.heading("description", text="Описание")
        
        self.tree.column("id", width=50, stretch=False, anchor=tk.CENTER)
        self.tree.column("type", width=80, stretch=False, anchor=tk.CENTER)
        self.tree.column("category", width=120, stretch=False, anchor=tk.CENTER)
        self.tree.column("amount", width=110, stretch=False, anchor=tk.CENTER)
        self.tree.column("date", width=100, stretch=False, anchor=tk.CENTER)
        self.tree.column("description", width=300, stretch=True, anchor=tk.W)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_card, orient=tk.VERTICAL, command=self.tree.yview, style="Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        tree_frame = tk.Frame(table_card, bg=bg_card)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=22, pady=(0, 18))
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<Double-1>", self._on_row_double_click)
        
        # Настройка цветов строк таблицы
        self.tree.tag_configure("income", background="#0a2e1a")
        self.tree.tag_configure("expense", background="#3d1a1a")
        
        # Инициализация категорий
        self._on_type_change()
    
    def _set_type(self, trans_type: str) -> None:
        """Устанавливает тип операции и обновляет стиль кнопок."""
        self.type_var.set(trans_type)
        accent_green = "#00c853"
        accent_red = "#ff3b30"
        bg_input = "#0f3460"
        text_secondary = "#8a8a9e"
        
        if trans_type == "expense":
            self.expense_btn.config(bg=accent_red, fg="white")
            self.income_btn.config(bg=bg_input, fg=text_secondary)
        else:
            self.income_btn.config(bg=accent_green, fg="#1a1a2e")
            self.expense_btn.config(bg=bg_input, fg=text_secondary)
        
        self._on_type_change()

    def _on_type_change(self) -> None:
        """Обновляет список категорий."""
        if self.type_var.get() == "expense":
            categories = self.manager.PREdefined_CATEGORIES_EXPENSE
        else:
            categories = self.manager.PREdefined_CATEGORIES_INCOME
        self.category_combo["values"] = categories
        if categories:
            self.category_var.set(categories[0])

    def _add_transaction(self) -> None:
        try:
            amount = float(self.amount_var.get().strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму")
            return

        transaction = Transaction(
            amount=amount,
            category=self.category_var.get().strip(),
            trans_date=self.date_entry.get(),
            trans_type=self.type_var.get(),
            description=self.description_var.get().strip(),
        )
        self.manager.add_transaction(transaction)
        self._clear_form()
        self._refresh_table()
        self._update_summary()
        messagebox.showinfo("Успех", "Операция добавлена")

    def _refresh_table(self, filter_type: Optional[str] = None) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        transactions = self.manager.get_all_transactions(filter_type)
        for t in transactions:
            type_display = "Доход" if t.trans_type == "income" else "Расход"
            tag = "income" if t.trans_type == "income" else "expense"
            amount_color = ""  # цвет определяется тегом строки
            self.tree.insert("", tk.END, values=(
                t.id, type_display, t.category, f"{t.amount:,.2f} ₽", t.date, t.description
            ), tags=(tag,))

    def _update_summary(self) -> None:
        total_income = self.manager.get_total_by_type("income")
        total_expense = self.manager.get_total_by_type("expense")
        balance = self.manager.get_balance()
        
        self.summary_income_label.config(text=f"{total_income:,.2f} ₽")
        self.summary_expense_label.config(text=f"{total_expense:,.2f} ₽")
        self.summary_balance_label.config(text=f"{balance:,.2f} ₽")
        
        if balance >= 0:
            self.summary_balance_label.config(fg="#ff9500")
        else:
            self.summary_balance_label.config(fg="#ff3b30")
        
        if not hasattr(self, '_budget_check_count'):
            self._budget_check_count = 0
        self._budget_check_count += 1
        if self._budget_check_count >= 5:
            self._show_category_status()
            self._budget_check_count = 0

    def _clear_form(self) -> None:
        self.amount_var.set("")
        self.description_var.set("")
        self.date_entry.set_date(date.today())
        self.editing_id = None
        self._on_type_change()

    def _on_row_double_click(self, event: tk.Event) -> None:
        selected_item = self.tree.selection()
        if not selected_item:
            return
        values = self.tree.item(selected_item[0])["values"]
        trans_id = values[0]
        transaction = self.manager.get_transaction_by_id(trans_id)
        if transaction:
            self.editing_id = transaction.id
            self.type_var.set(transaction.trans_type)
            self._set_type(transaction.trans_type)
            self.category_var.set(transaction.category)
            self.amount_var.set(str(transaction.amount))
            self.date_entry.set_date(transaction.date)
            self.description_var.set(transaction.description)

    def _save_edit(self) -> None:
        if self.editing_id is None:
            messagebox.showwarning("Внимание", "Выберите запись для редактирования")
            return
        try:
            amount = float(self.amount_var.get().strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму")
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
        messagebox.showinfo("Успех", "Запись обновлена")

    def _cancel_edit(self) -> None:
        self._clear_form()
        messagebox.showinfo("Отмена", "Редактирование отменено")

    def _delete_transaction(self) -> None:
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return
        values = self.tree.item(selected_item[0])["values"]
        trans_id = values[0]
        if messagebox.askyesno("Подтверждение", f"Удалить запись №{trans_id}?"):
            self.manager.delete_transaction(trans_id)
            self._clear_form()
            self._refresh_table()
            self._update_summary()
            messagebox.showinfo("Успех", "Запись удалена")

    def _show_expense_chart(self) -> None:
        data = self.manager.get_expenses_by_category()
        if not data:
            messagebox.showinfo("Диаграмма", "Нет данных о расходах")
            return
        self.visualizer.plot_pie_chart(data, "Расходы по категориям")

    def _show_income_chart(self) -> None:
        data = self.manager.get_income_by_category()
        if not data:
            messagebox.showinfo("Диаграмма", "Нет данных о доходах")
            return
        self.visualizer.plot_pie_chart(data, "Доходы по категориям")

    def _refresh_all(self) -> None:
        self._refresh_table()
        self._update_summary()
        self._clear_form()

    def _show_category_status(self) -> None:
        from models import ExpenseCategory
        expenses = self.manager.get_expenses_by_category()
        if not expenses:
            return
        status_lines = []
        for category_name, total in expenses:
            cat = ExpenseCategory(category_name)
            status = cat.get_status(total)
            status_lines.append(f"• {category_name}: {total:.2f} ₽ — {status}")
        messagebox.showinfo("Аналитика расходов", "\n".join(status_lines))


def main():
    root = tk.Tk()
    app = PersonalAccountantApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
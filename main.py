"""
Модуль main.py
Главный модуль приложения «ЗаяцСчетовод».
Содержит класс PersonalAccountantApp — графический интерфейс на tkinter.
Дизайн: современная тёмная тема с градиентами и улучшенной типографикой.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
from typing import Optional
import math

from models import FinanceManager, Transaction
from visualizer import FinanceVisualizer


class PersonalAccountantApp:
    """
    Основной класс GUI-приложения в современной тёмной теме.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ЗаяцСчетовод")
        self.root.geometry("1400x850")
        self.root.minsize(1100, 700)
        self.root.configure(bg="#0a0a0f")

        # Инициализация менеджера финансов и визуализатора
        self.manager = FinanceManager()
        self.visualizer = FinanceVisualizer()

        # Переменные для формы ввода
        self.type_var = tk.StringVar(value="expense")
        self.category_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.description_var = tk.StringVar()

        self.editing_id: Optional[int] = None

        # Анимационные переменные
        self._animation_phase = 0
        self._glow_alpha = 0
        self._glow_direction = 1

        self._create_styles()
        self._create_widgets()
        self._refresh_table()
        self._update_summary()
        self._start_animations()

    def _create_styles(self):
        """Создаёт кастомные стили для современного дизайна."""
        style = ttk.Style()
        style.theme_use("clam")

        # Цветовая палитра (только HEX без альфа-канала)
        # Базовый зеленый: rgb(24, 99, 5) = #186305
        base_green = "#0D3F00"
        light_green = "#166700"  # rgb(24, 99, 5) осветленный
        dark_green = "#072100"   # rgb(24, 99, 5) затемненный
        
        self.colors = {
            'bg_dark': '#0a0a0f',
            'bg_primary': "#002204",
            'bg_secondary': '#1a1a24',
            'bg_card': "#104902",        # Зеленый фон для карточек
            'bg_card_light': "#0d5a00",  # Чуть светлее зеленый
            'bg_hover': "#032500",
            
            'bg_input': '#1a1a28',
            'accent_green': '#00e676',
            'accent_green_dark': "#00c853",
            'accent_red': '#ff5252',
            'accent_red_dark': '#ff1744',
            'accent_blue': '#448aff',
            'accent_blue_dark': '#2979ff',
            'accent_purple': '#b388ff',
            'accent_purple_dark': '#7c4dff',
            'accent_orange': '#ff9100',
            'accent_orange_dark': '#ff6d00',
            'text_primary': '#f5f5f7',
            'text_secondary': '#c8e6c9',  # Светло-зеленый для текста
            'text_muted': '#a5d6a7',      # Приглушенный зеленый
            'border': '#2a5a15',
            'border_light': '#3a7a25',
            'income_bg': '#0a3d0a',       # Тёмно-зелёный для доходов
            'expense_bg': '#3d1a1a',      # Тёмно-красный для расходов
        }

        # Настройка стилей ttk
        style.configure("Treeview", 
                       background=self.colors['bg_card'],
                       fieldbackground=self.colors['bg_card'],
                       foreground=self.colors['text_primary'],
                       rowheight=35,
                       font=("Segoe UI", 10),
                       borderwidth=0)
        
        style.configure("Treeview.Heading",
                       background='#124a03',
                       foreground=self.colors['text_secondary'],
                       font=("Segoe UI", 10, "bold"),
                       padding=(10, 8),
                       borderwidth=0)
        
        style.map("Treeview.Heading",
                 background=[("active", '#1a6b08')],
                 foreground=[("active", self.colors['text_primary'])])

        style.configure("Vertical.TScrollbar",
                       background=self.colors['bg_input'],
                       troughcolor=self.colors['bg_dark'],
                       arrowcolor=self.colors['text_secondary'],
                       borderwidth=0,
                       arrowsize=14)

        style.configure("TCombobox",
                       font=("Segoe UI", 10),
                       fieldbackground=self.colors['bg_input'],
                       foreground=self.colors['text_primary'],
                       background=self.colors['bg_input'],
                       arrowcolor=self.colors['text_secondary'],
                       borderwidth=1)

    def _draw_bunny(self, canvas, x, y, size):
        """Рисует зайца на canvas."""
        # Константы для рисования
        OUTLINE_COLOR = '#1a1a1a'
        EYE_COLOR = '#ffffff'
        PUPIL_COLOR = '#1a1a1a'
        MOUTH_COLOR = '#1a1a1a'
        
        outline_width = max(1, size // 20)
        head_size = size
        ear_width = max(5, size // 4)
        ear_height = size
        head_x = x
        head_y = y
        ear_y = y - ear_height // 1.5
        
        # Основной цвет зайца
        body_color = '#e0e0e0'
        
        # Левое ухо
        left_ear_x = x - head_size // 4
        canvas.create_oval(
            int(left_ear_x - ear_width // 2), int(ear_y - ear_height // 2),
            int(left_ear_x + ear_width // 2), int(ear_y + ear_height // 2),
            fill=body_color, outline=OUTLINE_COLOR, width=outline_width
        )
        
        # Правое ухо
        right_ear_x = x + head_size // 4
        canvas.create_oval(
            int(right_ear_x - ear_width // 2), int(ear_y - ear_height // 2),
            int(right_ear_x + ear_width // 2), int(ear_y + ear_height // 2),
            fill=body_color, outline=OUTLINE_COLOR, width=outline_width
        )
        
        # Голова
        canvas.create_oval(
            int(head_x - head_size // 2), int(head_y - head_size // 2),
            int(head_x + head_size // 2), int(head_y + head_size // 2),
            fill=body_color, outline=OUTLINE_COLOR, width=outline_width
        )
        
        # Глаза
        eye_radius = max(2, head_size // 8)
        left_eye_x = head_x - head_size // 4
        right_eye_x = head_x + head_size // 4
        eye_y = head_y - head_size // 8
        
        for eye_x in [left_eye_x, right_eye_x]:
            # Белая часть глаза
            canvas.create_oval(
                int(eye_x - eye_radius), int(eye_y - eye_radius),
                int(eye_x + eye_radius), int(eye_y + eye_radius),
                fill=EYE_COLOR, outline=OUTLINE_COLOR, width=outline_width
            )
            # Зрачок
            pupil_radius = max(1, eye_radius // 2)
            canvas.create_oval(
                int(eye_x - pupil_radius), int(eye_y - pupil_radius),
                int(eye_x + pupil_radius), int(eye_y + pupil_radius),
                fill=PUPIL_COLOR
            )
        
        # Рот (только если размер достаточный)
        if size > 30:
            mouth_width = head_size // 2
            mouth_height = head_size // 8
            mouth_y = head_y + head_size // 6
            canvas.create_arc(
                head_x - mouth_width // 2, mouth_y - mouth_height // 2,
                head_x + mouth_width // 2, mouth_y + mouth_height // 2,
                start=0, extent=-180, fill=MOUTH_COLOR, width=outline_width
            )

    def _create_widgets(self) -> None:
        """Создаёт интерфейс в современном стиле."""
        
        # === Шапка с логотипом (увеличенная) ===
        header = tk.Frame(self.root, height=90, bg=self.colors['bg_primary'])
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Логотип с зайцем
        logo_frame = tk.Frame(header, bg=self.colors['bg_primary'])
        logo_frame.pack(side=tk.LEFT, padx=30, pady=10)
        
        # Canvas для зайца
        bunny_canvas = tk.Canvas(logo_frame, width=70, height=70, 
                                bg=self.colors['bg_primary'], highlightthickness=0)
        bunny_canvas.pack(side=tk.LEFT)
        
        # Рисуем зайца
        self._draw_bunny(bunny_canvas, 35, 42, 50)
        
        # Название приложения
        title_frame = tk.Frame(logo_frame, bg=self.colors['bg_primary'])
        title_frame.pack(side=tk.LEFT, padx=15)
        
        tk.Label(title_frame, text="ЗаяцСчетовод", 
                font=("Segoe UI", 24, "bold"), 
                bg=self.colors['bg_primary'], 
                fg=self.colors['text_primary']).pack()
        
        tk.Label(title_frame, text="Персональный финансовый помощник", 
                font=("Segoe UI", 9), 
                bg=self.colors['bg_primary'], 
                fg=self.colors['text_secondary']).pack()
        
        # Дата и статус
        status_frame = tk.Frame(header, bg=self.colors['bg_primary'])
        status_frame.pack(side=tk.RIGHT, padx=30)
        
        today = date.today()
        months = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня',
                 'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря']
        date_str = f"{today.day} {months[today.month - 1]} {today.year}"
        
        tk.Label(status_frame, text="🟢 Онлайн", 
                font=("Segoe UI", 9), 
                bg=self.colors['bg_primary'], 
                fg=self.colors['accent_green']).pack(anchor=tk.E, pady=(15, 0))
        
        tk.Label(status_frame, text=date_str, 
                font=("Segoe UI", 11), 
                bg=self.colors['bg_primary'], 
                fg=self.colors['text_secondary']).pack(anchor=tk.E)

        # === Карточки со сводкой (с зеленым фоном) ===
        cards_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        cards_container.pack(fill=tk.X, padx=25, pady=(20, 15))

        # Только 3 карточки: Доходы, Расходы, Баланс (увеличенный)
        cards_data = [
            ("💰 Доходы", self.colors['accent_green'], "summary_income_label", 1),
            ("📉 Расходы", self.colors['accent_red'], "summary_expense_label", 1),
            ("📊 Баланс", self.colors['accent_orange'], "summary_balance_label", 2),  # Баланс в 2 раза шире
        ]

        for i, (title, color, attr_name, width_multiplier) in enumerate(cards_data):
            # Карточка с зеленым фоном
            card = tk.Frame(cards_container, bg=self.colors['bg_card'], 
                          relief=tk.FLAT, bd=0, padx=20, pady=20)
            # Баланс занимает в 2 раза больше места
            if width_multiplier == 2:
                card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=8)
                # Делаем баланс выше
                card.configure(padx=25, pady=25)
            else:
                card.pack(side=tk.LEFT, fill=tk.BOTH, padx=8, ipadx=10)
            
            # Более светлая полоска сверху
            tk.Frame(card, bg=self.colors['bg_card_light'], height=3).pack(fill=tk.X, pady=(0, 15))
            
            # Заголовок
            tk.Label(card, text=title, 
                    font=("Segoe UI", 12 if width_multiplier == 2 else 11), 
                    bg=self.colors['bg_card'], 
                    fg=self.colors['text_secondary']).pack(anchor=tk.W)
            
            # Значение
            font_size = 28 if width_multiplier == 2 else 24
            setattr(self, attr_name, 
                   tk.Label(card, text="0 ₽", 
                           font=("Segoe UI", font_size, "bold"), 
                           bg=self.colors['bg_card'], 
                           fg=color))
            getattr(self, attr_name).pack(anchor=tk.W, pady=(10, 0))

        # === Форма добавления записи (с зеленым фоном) ===
        form_container = tk.Frame(self.root, bg=self.colors['bg_card'], 
                                 relief=tk.FLAT, bd=0)
        form_container.pack(fill=tk.X, padx=25, pady=(0, 15))
        
        inner_form = tk.Frame(form_container, bg=self.colors['bg_card'])
        inner_form.pack(fill=tk.BOTH, padx=25, pady=20)

        # Тип операции
        type_frame = tk.Frame(inner_form, bg=self.colors['bg_card'])
        type_frame.pack(fill=tk.X, pady=(0, 15))
        
        btn_style = {"font": ("Segoe UI", 10, "bold"), "relief": tk.FLAT, 
                    "bd": 0, "padx": 25, "pady": 8, "cursor": "hand2"}
        
        self.expense_btn = tk.Button(type_frame, text="🔴 Расход", 
                                     command=lambda: self._set_type("expense"),
                                     bg=self.colors['accent_red'], fg="white", **btn_style)
        self.expense_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.income_btn = tk.Button(type_frame, text="🟢 Доход", 
                                     command=lambda: self._set_type("income"),
                                     bg=self.colors['bg_input'], 
                                     fg=self.colors['text_secondary'], **btn_style)
        self.income_btn.pack(side=tk.LEFT)

        # Поля ввода
        fields_row = tk.Frame(inner_form, bg=self.colors['bg_card'])
        fields_row.pack(fill=tk.X, pady=(0, 15))
        
        # Стиль для меток на зеленом фоне
        label_style = {"font": ("Segoe UI", 9), "bg": self.colors['bg_card'], 
                      "fg": self.colors['text_secondary']}
        
        # Категория с темным фоном
        cat_frame = tk.Frame(fields_row, bg=self.colors['bg_card'])
        cat_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))
        tk.Label(cat_frame, text="Категория", **label_style).pack(anchor=tk.W, pady=(0, 5))
        # Создаем кастомный combobox с темным фоном
        self.category_combo = ttk.Combobox(cat_frame, textvariable=self.category_var, 
                                          state="readonly", font=("Segoe UI", 10))
        self.category_combo.pack(fill=tk.X, ipady=3)
        # Применяем темный фон через конфигурацию стиля
        style = ttk.Style()
        style.configure("Dark.TCombobox", 
                       fieldbackground=self.colors['bg_input'],
                       background=self.colors['bg_input'])
        self.category_combo.configure(style="Dark.TCombobox")
        
        # Сумма
        amount_frame = tk.Frame(fields_row, bg=self.colors['bg_card'])
        amount_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=8)
        tk.Label(amount_frame, text="Сумма (₽)", **label_style).pack(anchor=tk.W, pady=(0, 5))
        amount_entry = tk.Entry(amount_frame, textvariable=self.amount_var, font=("Segoe UI", 10),
                               bg=self.colors['bg_input'], fg=self.colors['text_primary'],
                               relief=tk.FLAT, insertbackground=self.colors['text_primary'],
                               highlightthickness=1, highlightbackground=self.colors['border'],
                               highlightcolor=self.colors['accent_green'])
        amount_entry.pack(fill=tk.X, ipady=5)
        
        # Дата
        date_frame = tk.Frame(fields_row, bg=self.colors['bg_card'])
        date_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=8)
        tk.Label(date_frame, text="Дата", **label_style).pack(anchor=tk.W, pady=(0, 5))
        self.date_entry = DateEntry(date_frame, width=12, background=self.colors['accent_green'],
                                   foreground='white', borderwidth=0, date_pattern='yyyy-mm-dd',
                                   font=("Segoe UI", 10), fieldbackground=self.colors['bg_input'],
                                   selectbackground=self.colors['accent_green'])
        self.date_entry.pack(fill=tk.X, ipady=5)
        self.date_entry.set_date(date.today())
        
        # Описание
        desc_frame = tk.Frame(fields_row, bg=self.colors['bg_card'])
        desc_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(8, 0))
        tk.Label(desc_frame, text="Описание", **label_style).pack(anchor=tk.W, pady=(0, 5))
        desc_entry = tk.Entry(desc_frame, textvariable=self.description_var, font=("Segoe UI", 10),
                             bg=self.colors['bg_input'], fg=self.colors['text_primary'],
                             relief=tk.FLAT, insertbackground=self.colors['text_primary'],
                             highlightthickness=1, highlightbackground=self.colors['border'],
                             highlightcolor=self.colors['accent_green'])
        desc_entry.pack(fill=tk.X, ipady=5)

        # === Панель действий ===
        actions_frame = tk.Frame(inner_form, bg=self.colors['bg_card'])
        actions_frame.pack(fill=tk.X)
        
        buttons_config = [
            ("➕ Добавить", self._add_transaction, self.colors['accent_green'], self.colors['bg_dark']),
            ("💾 Сохранить", self._save_edit, self.colors['accent_blue'], 'white'),
            ("✖️ Отменить", self._cancel_edit, self.colors['accent_orange'], self.colors['bg_dark']),
            ("🗑️ Удалить", self._delete_transaction, self.colors['accent_red'], 'white'),
            ("📊 График расходов", self._show_expense_chart, self.colors['accent_purple'], 'white'),
            ("📈 График доходов", self._show_income_chart, self.colors['accent_purple'], 'white'),
            ("🔄 Обновить", self._refresh_all, '#607d8b', 'white')
        ]
        
        btn_cfg = {"font": ("Segoe UI", 9, "bold"), "relief": tk.FLAT, "bd": 0, 
                  "padx": 12, "pady": 8, "cursor": "hand2"}
        
        for text, command, bg_color, fg_color in buttons_config:
            btn = tk.Button(actions_frame, text=text, command=command,
                          bg=bg_color, fg=fg_color, **btn_cfg)
            btn.pack(side=tk.LEFT, padx=3)

        # === Таблица транзакций (с зеленым фоном) ===
        table_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        table_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 15))

        table_card = tk.Frame(table_container, bg=self.colors['bg_card'])
        table_card.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок таблицы
        tk.Label(table_card, text="📋 История операций", 
                font=("Segoe UI", 14, "bold"), 
                bg=self.colors['bg_card'], 
                fg=self.colors['text_primary']).pack(anchor=tk.W, padx=25, pady=(18, 12))
        
        columns = ("id", "type", "category", "amount", "date", "description")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", height=12)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="Тип")
        self.tree.heading("category", text="Категория")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("date", text="Дата")
        self.tree.heading("description", text="Описание")
        
        self.tree.column("id", width=60, stretch=False, anchor=tk.CENTER)
        self.tree.column("type", width=100, stretch=False, anchor=tk.CENTER)
        self.tree.column("category", width=130, stretch=False, anchor=tk.CENTER)
        self.tree.column("amount", width=120, stretch=False, anchor=tk.CENTER)
        self.tree.column("date", width=100, stretch=False, anchor=tk.CENTER)
        self.tree.column("description", width=300, stretch=True, anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(table_card, orient=tk.VERTICAL, 
                                 command=self.tree.yview, style="Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        tree_frame = tk.Frame(table_card, bg=self.colors['bg_card'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 18))
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<Double-1>", self._on_row_double_click)
        
        # Теги с правильными цветами
        self.tree.tag_configure("income", background='#0a3d0a', 
                               foreground=self.colors['text_primary'])
        self.tree.tag_configure("expense", background='#3d1a1a', 
                               foreground=self.colors['text_primary'])
        
        self._on_type_change()

    def _start_animations(self):
        """Запускает анимации (заглушка, чтобы не усложнять)."""
        pass

    def _set_type(self, trans_type: str) -> None:
        """Устанавливает тип операции и обновляет стиль кнопок."""
        self.type_var.set(trans_type)
        
        if trans_type == "expense":
            self.expense_btn.config(bg=self.colors['accent_red'], fg="white")
            self.income_btn.config(bg=self.colors['bg_input'], fg=self.colors['text_secondary'])
        else:
            self.income_btn.config(bg=self.colors['accent_green'], fg=self.colors['bg_dark'])
            self.expense_btn.config(bg=self.colors['bg_input'], fg=self.colors['text_secondary'])
        
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
            type_display = "📈 Доход" if t.trans_type == "income" else "📉 Расход"
            tag = "income" if t.trans_type == "income" else "expense"
            self.tree.insert("", tk.END, values=(
                f"#{t.id}", type_display, t.category, 
                f"{t.amount:,.2f} ₽", t.date, t.description
            ), tags=(tag,))

    def _update_summary(self) -> None:
        total_income = self.manager.get_total_by_type("income")
        total_expense = self.manager.get_total_by_type("expense")
        balance = self.manager.get_balance()
        
        self.summary_income_label.config(text=f"{total_income:,.2f} ₽")
        self.summary_expense_label.config(text=f"{total_expense:,.2f} ₽")
        self.summary_balance_label.config(text=f"{balance:,.2f} ₽")
        
        if balance >= 0:
            self.summary_balance_label.config(fg=self.colors['accent_orange'])
        else:
            self.summary_balance_label.config(fg=self.colors['accent_red'])
        
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
        trans_id = int(values[0].replace('#', ''))
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
        trans_id = int(values[0].replace('#', ''))
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
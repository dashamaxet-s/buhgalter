"""
Модуль models.py
Содержит классы Transaction и FinanceManager.
Отвечает за хранение и управление данными о доходах и расходах.
Архитектура соответствует принципу единственной ответственности (SRP):
данный модуль занимается только данными и их взаимодействием с SQLite.
"""

import sqlite3
from datetime import date
from typing import List, Tuple, Optional


class Transaction:
    """
    Класс Transaction отвечает за хранение данных об одной финансовой записи.
    Поля: id, сумма, категория, дата, тип (доход/расход), описание.
    Атрибуты:
        id (int): Уникальный идентификатор записи в БД.
        amount (float): Сумма операции.
        category (str): Категория дохода или расхода.
        date (str): Дата операции в формате YYYY-MM-DD.
        trans_type (str): Тип операции: "income" или "expense".
        description (str): Дополнительное описание (опционально).
    Название класса записано в стиле CamelCase согласно PEP 8.
    """

    def __init__(
        self,
        amount: float,
        category: str,
        trans_date: str,
        trans_type: str,
        description: str = "",
        trans_id: Optional[int] = None,
    ):
        self.id = trans_id
        self.amount = amount
        self.category = category
        self.date = trans_date
        self.trans_type = trans_type
        self.description = description

    def __repr__(self) -> str:
        return (
            f"Transaction(id={self.id}, amount={self.amount}, "
            f"category='{self.category}', date='{self.date}', "
            f"type='{self.trans_type}')"
        )

    def to_tuple(self) -> Tuple[float, str, str, str, str]:
        """Возвращает кортеж значений для вставки в БД (без id)."""
        return (self.amount, self.category, self.date, self.trans_type, self.description)


class FinanceManager:
    """
    Класс FinanceManager управляет всеми финансовыми записями.
    Инкапсулирует логику работы с базой данных SQLite:
    создание таблиц, добавление, редактирование, удаление записей,
    а также получение статистики по доходам и расходам.
    Именование класса — CamelCase, методов — snake_case (PEP 8).
    """

    PREdefined_CATEGORIES_EXPENSE = [
        "Еда",
        "Транспорт",
        "Жильё",
        "Развлечения",
        "Здоровье",
        "Одежда",
        "Связь",
        "Образование",
        "Прочее",
    ]

    PREdefined_CATEGORIES_INCOME = [
        "Зарплата",
        "Подработка",
        "Инвестиции",
        "Подарки",
        "Прочее",
    ]

    def __init__(self, db_path: str = "finance.db"):
        """
        Инициализация менеджера финансов.
        Параметры:
            db_path (str): Путь к файлу базы данных SQLite.
        """
        self.db_path = db_path
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Создаёт и возвращает соединение с базой данных."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_database(self) -> None:
        """
        Создаёт таблицу transactions, если она ещё не существует.
        Поля таблицы:
            id           - первичный ключ, автоинкремент
            amount       - сумма операции (REAL)
            category     - категория (TEXT)
            date         - дата (TEXT в формате YYYY-MM-DD)
            trans_type   - тип операции: income или expense (TEXT)
            description  - описание (TEXT, опционально)
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            trans_type TEXT NOT NULL CHECK(trans_type IN ('income', 'expense')),
            description TEXT DEFAULT ''
        );
        """
        with self._get_connection() as conn:
            conn.execute(create_table_sql)
            conn.commit()

    def add_transaction(self, transaction: Transaction) -> int:
        """
        Добавляет новую запись в базу данных.
        Параметры:
            transaction (Transaction): Объект записи для добавления.
        Возвращает:
            int: Идентификатор добавленной записи.
        """
        sql = """
        INSERT INTO transactions (amount, category, date, trans_type, description)
        VALUES (?, ?, ?, ?, ?);
        """
        with self._get_connection() as conn:
            cursor = conn.execute(sql, transaction.to_tuple())
            conn.commit()
            return cursor.lastrowid

    def get_all_transactions(
        self, trans_type: Optional[str] = None
    ) -> List[Transaction]:
        """
        Возвращает все записи, опционально фильтруя по типу.
        Параметры:
            trans_type (str или None): 'income', 'expense' или None (все).
        Возвращает:
            List[Transaction]: Список объектов Transaction.
        """
        if trans_type:
            sql = "SELECT * FROM transactions WHERE trans_type = ? ORDER BY date DESC;"
            params = (trans_type,)
        else:
            sql = "SELECT * FROM transactions ORDER BY date DESC;"
            params = ()
        with self._get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [self._row_to_transaction(row) for row in rows]

    def get_transaction_by_id(self, trans_id: int) -> Optional[Transaction]:
        """
        Находит запись по идентификатору.
        Параметры:
            trans_id (int): ID записи.
        Возвращает:
            Transaction или None, если запись не найдена.
        """
        sql = "SELECT * FROM transactions WHERE id = ?;"
        with self._get_connection() as conn:
            row = conn.execute(sql, (trans_id,)).fetchone()
        if row:
            return self._row_to_transaction(row)
        return None

    def update_transaction(self, transaction: Transaction) -> bool:
        """
        Обновляет существующую запись в БД.
        Параметры:
            transaction (Transaction): Объект с обновлёнными данными (должен иметь id).
        Возвращает:
            bool: True, если обновление успешно.
        """
        sql = """
        UPDATE transactions
        SET amount = ?, category = ?, date = ?, trans_type = ?, description = ?
        WHERE id = ?;
        """
        params = transaction.to_tuple() + (transaction.id,)
        with self._get_connection() as conn:
            conn.execute(sql, params)
            conn.commit()
        return True

    def delete_transaction(self, trans_id: int) -> bool:
        """
        Удаляет запись по идентификатору.
        Параметры:
            trans_id (int): ID удаляемой записи.
        Возвращает:
            bool: True, если удаление успешно.
        """
        sql = "DELETE FROM transactions WHERE id = ?;"
        with self._get_connection() as conn:
            conn.execute(sql, (trans_id,))
            conn.commit()
        return True

    def get_total_by_type(self, trans_type: str) -> float:
        """
        Вычисляет общую сумму по заданному типу операций.
        Параметры:
            trans_type (str): 'income' или 'expense'.
        Возвращает:
            float: Общая сумма операций данного типа.
        """
        sql = "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE trans_type = ?;"
        with self._get_connection() as conn:
            result = conn.execute(sql, (trans_type,)).fetchone()
        return result["total"]

    def get_expenses_by_category(self) -> List[Tuple[str, float]]:
        """
        Группирует расходы по категориям и возвращает сумму по каждой.
        Возвращает:
            List[Tuple[str, float]]: Список кортежей (категория, сумма).
        """
        sql = """
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE trans_type = 'expense'
        GROUP BY category
        ORDER BY total DESC;
        """
        with self._get_connection() as conn:
            rows = conn.execute(sql).fetchall()
        return [(row["category"], row["total"]) for row in rows]

    def get_income_by_category(self) -> List[Tuple[str, float]]:
        """
        Группирует доходы по категориям и возвращает сумму по каждой.
        Возвращает:
            List[Tuple[str, float]]: Список кортежей (категория, сумма).
        """
        sql = """
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE trans_type = 'income'
        GROUP BY category
        ORDER BY total DESC;
        """
        with self._get_connection() as conn:
            rows = conn.execute(sql).fetchall()
        return [(row["category"], row["total"]) for row in rows]

    def get_balance(self) -> float:
        """
        Рассчитывает текущий баланс (доходы минус расходы).
        Возвращает:
            float: Разница между общими доходами и расходами.
        """
        total_income = self.get_total_by_type("income")
        total_expense = self.get_total_by_type("expense")
        return total_income - total_expense

    @staticmethod
    def _row_to_transaction(row: sqlite3.Row) -> Transaction:
        """
        Преобразует строку результата запроса SQLite в объект Transaction.
        Параметры:
            row (sqlite3.Row): Строка из БД.
        Возвращает:
            Transaction: Объект записи.
        """
        return Transaction(
            trans_id=row["id"],
            amount=row["amount"],
            category=row["category"],
            trans_date=row["date"],
            trans_type=row["trans_type"],
            description=row["description"],
        )


if __name__ == "__main__":
    # Простой тест работы модуля
    manager = FinanceManager(":memory:")  # база в памяти для теста
    test_transaction = Transaction(
        amount=1500.00,
        category="Еда",
        trans_date=str(date.today()),
        trans_type="expense",
        description="Продукты на неделю",
    )
    new_id = manager.add_transaction(test_transaction)
    print(f"Добавлена запись с id={new_id}")
    all_records = manager.get_all_transactions()
    print("Все записи:", all_records)
    print(f"Баланс: {manager.get_balance():.2f} руб.")
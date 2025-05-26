import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkinter.font import Font

class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учет финансов")
        self.root.geometry("800x700")
        self.root.configure(bg="#f0f0f0")

        # Шрифты
        self.title_font = Font(family="Arial", size=14, weight="bold")
        self.label_font = Font(family="Arial", size=12)
        self.entry_font = Font(family="Arial", size=12)
        self.button_font = Font(family="Arial", size=12, weight="bold")
        self.amount_font = Font(family="Arial", size=16, weight="bold")

        # Инициализация БД
        self.init_db()

        # Основной интерфейс
        self.create_widgets()

        # Загрузка данных
        self.update_display()

    def init_db(self):
        self.conn = sqlite3.connect('finances.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                type TEXT CHECK (type IN ('Доход', 'Расход')),
                description TEXT,
                date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance (
                total_balance REAL DEFAULT 0
            )
        ''')
        # Инициализация баланса
        self.cursor.execute("SELECT COUNT(*) FROM balance")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO balance (total_balance) VALUES (0)")
        self.conn.commit()

    def create_widgets(self):
        # Основной контейнер
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Верхняя часть (фильтр и статистика)
        top_frame = tk.Frame(main_frame, bg="#f0f0f0")
        top_frame.pack(fill=tk.X, pady=(0, 20))

        # Левая часть (фильтр и ввод данных)
        left_top_frame = tk.Frame(top_frame, bg="#f0f0f0")
        left_top_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        # Правая часть (статистика)
        right_top_frame = tk.Frame(top_frame, bg="#f0f0f0", width=300)
        right_top_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Поля ввода (левая верхняя часть)
        input_frame = tk.Frame(left_top_frame, bg="#f0f0f0")
        input_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(input_frame, text="Сумма:", bg="#f0f0f0", font=self.label_font).pack(anchor=tk.W)
        self.amount_entry = tk.Entry(input_frame, font=self.entry_font, bd=2, relief=tk.GROOVE)
        self.amount_entry.pack(fill=tk.X, pady=(0, 10), ipady=5)

        tk.Label(input_frame, text="Комментарий:", bg="#f0f0f0", font=self.label_font).pack(anchor=tk.W)
        self.comment_entry = tk.Entry(input_frame, font=self.entry_font, bd=2, relief=tk.GROOVE)
        self.comment_entry.pack(fill=tk.X, ipady=5)

        # Кнопки операций (левая верхняя часть)
        btn_frame = tk.Frame(left_top_frame, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, pady=(0, 15))

        self.income_btn = tk.Button(
            btn_frame, text="Доход (+)",
            font=self.button_font, bg="#4CAF50", fg="white",
            bd=0, padx=20, pady=10,
            command=lambda: self.add_transaction("Доход")
        )
        self.income_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.expense_btn = tk.Button(
            btn_frame, text="Расход (-)",
            font=self.button_font, bg="#F44336", fg="white",
            bd=0, padx=20, pady=10,
            command=lambda: self.add_transaction("Расход")
        )
        self.expense_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        # Фильтрация (левая верхняя часть)
        filter_frame = tk.LabelFrame(
            left_top_frame, text=" Фильтр операций ",
            font=self.title_font, bg="#f0f0f0", bd=2, relief=tk.GROOVE
        )
        filter_frame.pack(fill=tk.X, pady=(0, 0), ipady=5)

        # Поля фильтрации
        tk.Label(filter_frame, text="Сумма:", bg="#f0f0f0", font=self.label_font).pack(anchor=tk.W, pady=(5, 0))

        range_frame = tk.Frame(filter_frame, bg="#f0f0f0")
        range_frame.pack(fill=tk.X, pady=5)

        tk.Label(range_frame, text="От:", bg="#f0f0f0", font=self.label_font).pack(side=tk.LEFT, padx=(0, 5))
        self.min_amount_entry = tk.Entry(range_frame, font=self.entry_font, width=10)
        self.min_amount_entry.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(range_frame, text="До:", bg="#f0f0f0", font=self.label_font).pack(side=tk.LEFT, padx=(0, 5))
        self.max_amount_entry = tk.Entry(range_frame, font=self.entry_font, width=10)
        self.max_amount_entry.pack(side=tk.LEFT)

        # Кнопки фильтрации
        btn_filter_frame = tk.Frame(filter_frame, bg="#f0f0f0")
        btn_filter_frame.pack(fill=tk.X, pady=(5, 5))

        self.filter_btn = tk.Button(
            btn_filter_frame, text="Применить",
            font=self.button_font, bg="#2196F3", fg="white",
            command=self.apply_filters
        )
        self.filter_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.reset_filter_btn = tk.Button(
            btn_filter_frame, text="Сбросить",
            font=self.button_font, bg="#9E9E9E", fg="white",
            command=self.reset_filters
        )
        self.reset_filter_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        # Статистика (правая верхняя часть)
        stats_frame = tk.LabelFrame(
            right_top_frame, text=" Статистика ",
            font=self.title_font, bg="#f0f0f0", bd=2, relief=tk.GROOVE
        )
        stats_frame.pack(fill=tk.BOTH, expand=True)

        # Текущий баланс
        balance_frame = tk.Frame(stats_frame, bg="#f0f0f0")
        balance_frame.pack(fill=tk.X, pady=(10, 15))

        tk.Label(balance_frame, text="Текущий баланс:", bg="#f0f0f0", font=self.label_font).pack(anchor=tk.W)
        self.balance_label = tk.Label(
            balance_frame, text="0.00 руб.",
            bg="#f0f0f0", font=self.amount_font, fg="#2196F3"
        )
        self.balance_label.pack(anchor=tk.W, pady=(5, 0))

        # Дополнительная статистика
        self.stats_text = tk.Text(
            stats_frame, height=10, width=30,
            font=self.entry_font, bd=2, relief=tk.GROOVE,
            state=tk.DISABLED
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # История операций (нижняя часть на всю ширину)
        history_frame = tk.LabelFrame(
            main_frame, text=" История операций ",
            font=self.title_font, bg="#f0f0f0", bd=2, relief=tk.GROOVE
        )
        history_frame.pack(fill=tk.BOTH, expand=True)

        self.history_text = tk.Text(
            history_frame, height=20,
            font=self.entry_font, bd=2, relief=tk.GROOVE,
            state=tk.DISABLED
        )
        self.history_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def add_transaction(self, transaction_type):
        try:
            amount = float(self.amount_entry.get())
            description = self.comment_entry.get() or f"Операция: {transaction_type}"

            if transaction_type == "Расход":
                amount = -abs(amount)
            else:
                amount = abs(amount)

            # Добавляем транзакцию
            self.cursor.execute('''
                INSERT INTO transactions (amount, type, description)
                VALUES (?, ?, ?)
            ''', (abs(amount), transaction_type, description))

            # Обновляем баланс
            self.cursor.execute("UPDATE balance SET total_balance = total_balance + ?", (amount,))

            self.conn.commit()

            # Очищаем поля ввода
            self.amount_entry.delete(0, tk.END)
            self.comment_entry.delete(0, tk.END)

            # Обновляем отображение
            self.update_display()

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму")

    def apply_filters(self):
        min_amount = self.min_amount_entry.get()
        max_amount = self.max_amount_entry.get()

        try:
            min_amount = float(min_amount) if min_amount else None
            max_amount = float(max_amount) if max_amount else None
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные значения для фильтрации")
            return

        self.update_display(min_amount, max_amount)

    def reset_filters(self):
        self.min_amount_entry.delete(0, tk.END)
        self.max_amount_entry.delete(0, tk.END)
        self.update_display()

    def update_display(self, min_amount=None, max_amount=None):
        # Получаем текущий баланс
        self.cursor.execute("SELECT total_balance FROM balance")
        balance = self.cursor.fetchone()[0]
        self.balance_label.config(text=f"{balance:.2f} руб.")

        # Формируем запрос с учетом фильтров
        query = '''
            SELECT date, type, amount, description
            FROM transactions
        '''
        params = []

        # Добавляем условия фильтрации
        conditions = []
        if min_amount is not None:
            conditions.append("amount >= ?")
            params.append(min_amount)
        if max_amount is not None:
            conditions.append("amount <= ?")
            params.append(max_amount)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY date DESC LIMIT 200"

        # Выполняем запрос
        if params:
            self.cursor.execute(query, tuple(params))
        else:
            self.cursor.execute(query)

        transactions = self.cursor.fetchall()

        # Обновляем статистику
        self.update_stats(transactions)

        # Обновляем историю операций
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)

        if not transactions:
            self.history_text.insert(tk.END, "Нет операций, соответствующих фильтру\n", "black")
        else:
            for trans in transactions:
                self.format_transaction(self.history_text, trans)
        self.history_text.config(state=tk.DISABLED)

    def format_transaction(self, text_widget, transaction):
        date = transaction[0][:10]
        trans_type = transaction[1]
        amount = transaction[2]
        description = transaction[3][:40]  # Обрезаем длинные описания

        color = "green" if trans_type == "Доход" else "red"
        amount_text = f"+{amount:.2f}" if trans_type == "Доход" else f"-{amount:.2f}"

        text_widget.insert(tk.END, f"{date}: ", "black")
        text_widget.insert(tk.END, f"{amount_text} руб.", color)
        text_widget.insert(tk.END, f" - {description}\n", "black")

    def update_stats(self, transactions):
        # Обновляем статистику
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)

        # Общая статистика
        self.cursor.execute("SELECT COUNT(*) FROM transactions WHERE type = 'Доход'")
        income_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM transactions WHERE type = 'Расход'")
        expense_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Доход'")
        total_income = self.cursor.fetchone()[0] or 0

        self.cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Расход'")
        total_expense = self.cursor.fetchone()[0] or 0

        # Статистика по фильтру
        filtered_income = sum(1 for t in transactions if t[1] == 'Доход')
        filtered_expense = sum(1 for t in transactions if t[1] == 'Расход')
        filtered_income_sum = sum(t[2] for t in transactions if t[1] == 'Доход')
        filtered_expense_sum = sum(t[2] for t in transactions if t[1] == 'Расход')

        self.stats_text.insert(tk.END, "Общая статистика:\n", "bold")
        self.stats_text.insert(tk.END, f"Доходы: {income_count} (+{total_income:.2f} руб.)\n", "green")
        self.stats_text.insert(tk.END, f"Расходы: {expense_count} (-{abs(total_expense):.2f} руб.)\n\n", "red")

        self.stats_text.insert(tk.END, "По текущему фильтру:\n", "bold")
        self.stats_text.insert(tk.END, f"Доходы: {filtered_income} (+{filtered_income_sum:.2f} руб.)\n", "green")
        self.stats_text.insert(tk.END, f"Расходы: {filtered_expense} (-{abs(filtered_expense_sum):.2f} руб.)\n", "red")

        self.stats_text.config(state=tk.DISABLED)

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()

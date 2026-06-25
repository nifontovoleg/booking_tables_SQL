import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from backend import (
    create_tables,
    create_user, update_user, delete_user, get_all_users,
    create_table, update_table, delete_table, get_all_tables,
    create_booking, update_booking, delete_booking, get_all_bookings,
)


class DataEntryWindow:
    """Всплывающее окно для добавления/редактирования данных"""
    def __init__(self, parent, title, fields, edit_data=None):
        self.result = None
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("400x500")
        self.window.transient(parent)
        self.window.grab_set()

        self.fields = fields
        self.entries = {}
        self.datetime_vars = {}

        # Поле ID для редактирования
        self.edit_id = None
        if edit_data and "id" in edit_data:
            self.edit_id = edit_data["id"]

        # Заголовок
        tk.Label(self.window, text=title, font=("Arial", 14, "bold")).pack(pady=10)

        # Поля ввода
        frame = tk.Frame(self.window)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        for i, (name, ftype) in enumerate(fields):
            if name == "id" and edit_data:
                continue

            tk.Label(frame, text=f"{name}:", font=("Arial", 10)).grid(
                row=i, column=0, sticky="e", padx=5, pady=5
            )

            if ftype == "bool":
                var = tk.BooleanVar(value=edit_data.get(name, False) if edit_data else False)
                self.entries[name] = var
                ttk.Checkbutton(frame, variable=var).grid(row=i, column=1, sticky="w", padx=5, pady=5)
            elif ftype == "datetime":
                date_var = tk.StringVar(value=self._get_edit_date(edit_data, name))
                time_var = tk.StringVar(value=self._get_edit_time(edit_data, name))
                self.datetime_vars[name] = {"date": date_var, "time": time_var}

                date_entry = ttk.Entry(frame, textvariable=date_var, width=12)
                date_entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
                time_entry = ttk.Entry(frame, textvariable=time_var, width=8)
                time_entry.grid(row=i, column=2, sticky="w", padx=(0, 5), pady=5)
                tk.Label(frame, text="дд.мм.гггг чч:мм", font=("Arial", 7), fg="gray").grid(row=i, column=3, sticky="w")

                self.entries[name] = {"date": date_var, "time": time_var}
            else:
                var = tk.StringVar(value=str(edit_data.get(name, "")) if edit_data else "")
                self.entries[name] = var
                ttk.Entry(frame, textvariable=var, width=30).grid(row=i, column=1, sticky="w", padx=5, pady=5)

        # Кнопки
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill="x", padx=20, pady=10)

        ttk.Button(btn_frame, text="Сохранить", command=self.save, width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.cancel, width=15).pack(side="right", padx=5)

    def _get_edit_date(self, edit_data, key):
        val = edit_data.get(key) if edit_data else None
        if isinstance(val, datetime):
            return val.strftime("%d.%m.%Y")
        if isinstance(val, str):
            try:
                dt = datetime.strptime(val.split()[0] if " " in val else val, "%d.%m.%Y")
                return dt.strftime("%d.%m.%Y")
            except:
                pass
        return ""

    def _get_edit_time(self, edit_data, key):
        val = edit_data.get(key) if edit_data else None
        if isinstance(val, datetime):
            return val.strftime("%H:%M")
        if isinstance(val, str) and " " in val:
            return val.split()[1]
        return ""

    def save(self):
        data = {"id": self.edit_id} if self.edit_id else {}
        for name, var in self.entries.items():
            if isinstance(var, tk.BooleanVar):
                data[name] = var.get()
            elif isinstance(var, dict) and "date" in var and "time" in var:
                # datetime поля
                date_val = var["date"].get().strip()
                time_val = var["time"].get().strip()
                if date_val and time_val:
                    data[name] = f"{date_val} {time_val}"
                elif date_val:
                    data[name] = f"{date_val} 00:00"
                else:
                    data[name] = None
            else:
                val = var.get().strip()
                data[name] = val if val else None
        self.result = data
        self.window.destroy()

    def cancel(self):
        self.result = None
        self.window.destroy()


class UsersTab:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Левая часть - таблица
        left_frame = tk.Frame(self.parent)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Заголовок и кнопки
        header_frame = tk.Frame(left_frame)
        header_frame.pack(fill="x", pady=(0, 10))

        tk.Label(header_frame, text="👥 Пользователи", font=("Arial", 14, "bold")).pack(side="left")

        btn_frame = tk.Frame(header_frame)
        btn_frame.pack(side="right")

        ttk.Button(btn_frame, text="➕ Добавить", command=self.add_user).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✏️ Редактировать", command=self.edit_user).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑 Удалить", command=self.delete_user).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_data).pack(side="left", padx=5)

        # Таблица
        tree_frame = tk.Frame(left_frame)
        tree_frame.pack(fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(tree_frame)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(tree_frame, columns=("id", "name", "email", "phone", "age", "is_active"),
                                  show="headings",
                                  yscrollcommand=scrollbar_y.set,
                                  xscrollcommand=scrollbar_x.set)

        columns_config = [
            ("ID", 50), ("Имя", 120), ("Email", 150),
            ("Телефон", 120), ("Возраст", 70), ("Статус", 70)
        ]
        for (name, width), col_name in zip(columns_config, self.tree["columns"]):
            self.tree.heading(col_name, text=name)
            self.tree.column(col_name, width=width, minwidth=50)

        self.tree.pack(fill="both", expand=True)
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", lambda e: self.edit_user())

        # Правая часть - инфо о выбранной записи
        info_frame = tk.LabelFrame(self.parent, text="📋 Информация о пользователе", padx=10, pady=10)
        info_frame.pack(side="right", fill="y", padx=(10, 10), pady=10)
        info_frame.configure(width=280)
        info_frame.pack_propagate(False)

        self.info_labels = {}
        info_fields = [("ID:", "id"), ("Имя:", "name"), ("Email:", "email"),
                       ("Телефон:", "phone"), ("Возраст:", "age"), ("Активен:", "is_active")]

        for i, (text, key) in enumerate(info_fields):
            row = i // 2
            col = (i % 2) * 2
            tk.Label(info_frame, text=text, font=("Arial", 9, "bold")).grid(
                row=row, column=col, sticky="e", padx=5, pady=3
            )
            lbl = tk.Label(info_frame, text="", font=("Arial", 9), wraplength=250)
            lbl.grid(row=row, column=col + 1, sticky="w", padx=5, pady=3)
            self.info_labels[key] = lbl

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            users = get_all_users()
            if not users:
                return
            for u in users:
                self.tree.insert("", "end", values=(
                    u.get("id", ""),
                    u.get("name", ""),
                    u.get("email", ""),
                    u.get("phone", ""),
                    u.get("age", ""),
                    "✅" if u.get("is_active") else "❌"
                ), tags=(u.get("id"),))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей:\n{e}")

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        values = item["values"]
        keys = ["id", "name", "email", "phone", "age", "is_active"]
        for i, key in enumerate(keys):
            if i < len(values):
                val = values[i]
                if key == "is_active":
                    val = "✅ Да" if val else "❌ Нет"
                self.info_labels[key].config(text=str(val) if val else "-")

    def add_user(self):
        fields = [("Имя", "str"), ("Email", "str"), ("Телефон", "str"), ("Возраст", "int")]
        window = DataEntryWindow(self.parent, "➕ Добавить пользователя", fields)
        self.parent.wait_window(window.window)

        if window.result is None:
            return

        try:
            name = window.result.get("Имя")
            if not name:
                messagebox.showwarning("Предупреждение", "Поле 'Имя' обязательно!")
                return

            user_id = create_user(
                name=name,
                email=window.result.get("Email"),
                phone=window.result.get("Телефон"),
                age=int(window.result["Возраст"]) if window.result.get("Возраст") else None
            )
            messagebox.showinfo("Успех", f"Пользователь успешно создан!\nID: {user_id}")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить пользователя:\n{e}")

    def edit_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для редактирования!")
            return

        item = self.tree.item(selected[0])
        values = item["values"]
        record_id = values[0]

        if not record_id:
            messagebox.showwarning("Предупреждение", "Не удалось определить ID пользователя!")
            return

        # Получаем полные данные пользователя
        try:
            from backend import get_user
            user = get_user(record_id)
            if not user:
                messagebox.showwarning("Предупреждение", "Пользователь не найден!")
                return

            fields = [("Имя", "str"), ("Email", "str"), ("Телефон", "str"), ("Возраст", "int")]
            window = DataEntryWindow(self.parent, "✏️ Редактировать пользователя", fields, edit_data=user)
            self.parent.wait_window(window.window)

            if window.result is None:
                return

            update_user(
                record_id,
                name=window.result.get("Имя"),
                email=window.result.get("Email"),
                phone=window.result.get("Телефон"),
                age=int(window.result["Возраст"]) if window.result.get("Возраст") else None
            )
            messagebox.showinfo("Успех", "Пользователь успешно обновлён!")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить пользователя:\n{e}")

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления!")
            return

        item = self.tree.item(selected[0])
        record_id = item["values"][0]
        name = item["values"][1]

        if not messagebox.askyesno("Подтверждение", f"Удалить пользователя '{name}' (ID: {record_id})?"):
            return

        try:
            success = delete_user(record_id)
            if success:
                messagebox.showinfo("Успех", "Пользователь удалён!")
                self.load_data()
            else:
                messagebox.showwarning("Предупреждение", "Не удалось удалить пользователя")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить пользователя:\n{e}")


class TablesTab:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        left_frame = tk.Frame(self.parent)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        header_frame = tk.Frame(left_frame)
        header_frame.pack(fill="x", pady=(0, 10))

        tk.Label(header_frame, text="🪑 Столы", font=("Arial", 14, "bold")).pack(side="left")

        btn_frame = tk.Frame(header_frame)
        btn_frame.pack(side="right")

        ttk.Button(btn_frame, text="➕ Добавить", command=self.add_table).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✏️ Редактировать", command=self.edit_table).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑 Удалить", command=self.delete_table).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_data).pack(side="left", padx=5)

        tree_frame = tk.Frame(left_frame)
        tree_frame.pack(fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(tree_frame)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(tree_frame, columns=("id", "number", "capacity", "location", "is_outdoor", "is_reserved"),
                                  show="headings",
                                  yscrollcommand=scrollbar_y.set,
                                  xscrollcommand=scrollbar_x.set)

        columns_config = [
            ("ID", 50), ("Номер", 80), ("Вместимость", 100),
            ("Расположение", 120), ("Уличный", 80), ("Забронирован", 100)
        ]
        for (name, width), col_name in zip(columns_config, self.tree["columns"]):
            self.tree.heading(col_name, text=name)
            self.tree.column(col_name, width=width, minwidth=50)

        self.tree.pack(fill="both", expand=True)
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", lambda e: self.edit_table())

        info_frame = tk.LabelFrame(self.parent, text="📋 Информация о столе", padx=10, pady=10)
        info_frame.pack(side="right", fill="y", padx=(10, 10), pady=10)
        info_frame.configure(width=280)
        info_frame.pack_propagate(False)

        self.info_labels = {}
        info_fields = [("ID:", "id"), ("Номер:", "number"), ("Вместимость:", "capacity"),
                       ("Расположение:", "location"), ("Уличный:", "is_outdoor"), ("Забронирован:", "is_reserved")]

        for i, (text, key) in enumerate(info_fields):
            row = i // 2
            col = (i % 2) * 2
            tk.Label(info_frame, text=text, font=("Arial", 9, "bold")).grid(
                row=row, column=col, sticky="e", padx=5, pady=3
            )
            lbl = tk.Label(info_frame, text="", font=("Arial", 9), wraplength=250)
            lbl.grid(row=row, column=col + 1, sticky="w", padx=5, pady=3)
            self.info_labels[key] = lbl

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            tables = get_all_tables()
            if not tables:
                return
            for t in tables:
                self.tree.insert("", "end", values=(
                    t.get("id", ""),
                    t.get("number", ""),
                    t.get("capacity", ""),
                    t.get("location", ""),
                    "✅" if t.get("is_outdoor") else "❌",
                    "✅" if t.get("is_reserved") else "❌"
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить столы:\n{e}")

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        values = item["values"]
        keys = ["id", "number", "capacity", "location", "is_outdoor", "is_reserved"]
        for i, key in enumerate(keys):
            if i < len(values):
                val = values[i]
                if key in ("is_outdoor", "is_reserved"):
                    val = "✅ Да" if val else "❌ Нет"
                self.info_labels[key].config(text=str(val) if val else "-")

    def add_table(self):
        fields = [("Номер", "int"), ("Вместимость", "int"), ("Расположение", "str")]
        window = DataEntryWindow(self.parent, "➕ Добавить стол", fields)
        self.parent.wait_window(window.window)

        if window.result is None:
            return

        try:
            number = window.result.get("Номер")
            if not number:
                messagebox.showwarning("Предупреждение", "Поле 'Номер' обязательно!")
                return

            table_id = create_table(
                number=int(number),
                capacity=int(window.result["Вместимость"]) if window.result.get("Вместимость") else None,
                location=window.result.get("Расположение")
            )
            messagebox.showinfo("Успех", f"Стол успешно создан!\nID: {table_id}")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить стол:\n{e}")

    def edit_table(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите стол для редактирования!")
            return

        item = self.tree.item(selected[0])
        record_id = item["values"][0]

        if not record_id:
            messagebox.showwarning("Предупреждение", "Не удалось определить ID стола!")
            return

        try:
            from backend import get_table
            table = get_table(record_id)
            if not table:
                messagebox.showwarning("Предупреждение", "Стол не найден!")
                return

            fields = [("Номер", "int"), ("Вместимость", "int"), ("Расположение", "str")]
            window = DataEntryWindow(self.parent, "✏️ Редактировать стол", fields, edit_data=table)
            self.parent.wait_window(window.window)

            if window.result is None:
                return

            update_table(
                record_id,
                number=int(window.result["Номер"]) if window.result.get("Номер") else None,
                capacity=int(window.result["Вместимость"]) if window.result.get("Вместимость") else None,
                location=window.result.get("Расположение")
            )
            messagebox.showinfo("Успех", "Стол успешно обновлён!")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить стол:\n{e}")

    def delete_table(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите стол для удаления!")
            return

        item = self.tree.item(selected[0])
        record_id = item["values"][0]
        number = item["values"][1]

        if not messagebox.askyesno("Подтверждение", f"Удалить стол №{number} (ID: {record_id})?"):
            return

        try:
            success = delete_table(record_id)
            if success:
                messagebox.showinfo("Успех", "Стол удалён!")
                self.load_data()
            else:
                messagebox.showwarning("Предупреждение", "Не удалось удалить стол")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить стол:\n{e}")


class BookingsTab:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        left_frame = tk.Frame(self.parent)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        header_frame = tk.Frame(left_frame)
        header_frame.pack(fill="x", pady=(0, 10))

        tk.Label(header_frame, text="📅 Бронирования", font=("Arial", 14, "bold")).pack(side="left")

        btn_frame = tk.Frame(header_frame)
        btn_frame.pack(side="right")

        ttk.Button(btn_frame, text="➕ Добавить", command=self.add_booking).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✏️ Редактировать", command=self.edit_booking).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑 Удалить", command=self.delete_booking).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_data).pack(side="left", padx=5)

        tree_frame = tk.Frame(left_frame)
        tree_frame.pack(fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(tree_frame)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(tree_frame, columns=("id", "user_id", "table_id", "start", "end", "guests", "status"),
                                  show="headings",
                                  yscrollcommand=scrollbar_y.set,
                                  xscrollcommand=scrollbar_x.set)

        columns_config = [
            ("ID", 50), ("ID пользователя", 100), ("ID стола", 80),
            ("Начало", 140), ("Окончание", 140), ("Гостей", 70), ("Статус", 100)
        ]
        for (name, width), col_name in zip(columns_config, self.tree["columns"]):
            self.tree.heading(col_name, text=name)
            self.tree.column(col_name, width=width, minwidth=50)

        self.tree.pack(fill="both", expand=True)
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", lambda e: self.edit_booking())

        info_frame = tk.LabelFrame(self.parent, text="📋 Информация о бронировании", padx=10, pady=10)
        info_frame.pack(side="right", fill="y", padx=(10, 10), pady=10)
        info_frame.configure(width=280)
        info_frame.pack_propagate(False)

        self.info_labels = {}
        info_fields = [("ID:", "id"), ("ID пользователя:", "user_id"), ("ID стола:", "table_id"),
                       ("Начало:", "start_time"), ("Окончание:", "end_time"), ("Гостей:", "guests"), ("Статус:", "status")]

        for i, (text, key) in enumerate(info_fields):
            row = i // 2
            col = (i % 2) * 2
            tk.Label(info_frame, text=text, font=("Arial", 9, "bold")).grid(
                row=row, column=col, sticky="e", padx=5, pady=3
            )
            lbl = tk.Label(info_frame, text="", font=("Arial", 9), wraplength=250)
            lbl.grid(row=row, column=col + 1, sticky="w", padx=5, pady=3)
            self.info_labels[key] = lbl

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            bookings = get_all_bookings()
            if not bookings:
                return
            for b in bookings:
                start = b.get("start_time").strftime("%d.%m.%Y %H:%M") if b.get("start_time") else ""
                end = b.get("end_time").strftime("%d.%m.%Y %H:%M") if b.get("end_time") else ""
                status_text = {"pending": "⏳ Ожидание", "confirmed": "✅ Подтверждено",
                               "cancelled": "❌ Отменено", "completed": "📋 Завершено"}
                self.tree.insert("", "end", values=(
                    b.get("id", ""),
                    b.get("user_id", ""),
                    b.get("table_id", ""),
                    start, end,
                    b.get("guests", ""),
                    status_text.get(b.get("status", ""), b.get("status", ""))
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить бронирования:\n{e}")

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        values = item["values"]
        keys = ["id", "user_id", "table_id", "start_time", "end_time", "guests", "status"]
        status_map = {"pending": "Ожидание", "confirmed": "Подтверждено",
                      "cancelled": "Отменено", "completed": "Завершено"}
        for i, key in enumerate(keys):
            if i < len(values):
                val = values[i]
                if key == "status":
                    val = status_map.get(val, val) if val else "-"
                self.info_labels[key].config(text=str(val) if val else "-")

    def add_booking(self):
        fields = [("ID пользователя", "int"), ("ID стола", "int"), ("Начало", "datetime"),
                  ("Окончание", "datetime"), ("Гостей", "int"), ("Статус", "str")]
        window = DataEntryWindow(self.parent, "➕ Добавить бронирование", fields)
        self.parent.wait_window(window.window)

        if window.result is None:
            return

        try:
            user_id = window.result.get("ID пользователя")
            table_id = window.result.get("ID стола")
            if not user_id or not table_id:
                messagebox.showwarning("Предупреждение", "Укажите ID пользователя и стола!")
                return

            def parse_datetime(val):
                if not val:
                    return None
                try:
                    return datetime.strptime(val, "%d.%m.%Y %H:%M")
                except:
                    try:
                        return datetime.strptime(val, "%Y-%m-%d %H:%M")
                    except:
                        return None

            booking_id = create_booking(
                user_id=int(user_id),
                table_id=int(table_id),
                start_time=parse_datetime(window.result.get("Начало")),
                end_time=parse_datetime(window.result.get("Окончание")),
                guests=int(window.result["Гостей"]) if window.result.get("Гостей") else None,
                status=window.result.get("Статус", "pending") or "pending"
            )
            messagebox.showinfo("Успех", f"Бронирование создано!\nID: {booking_id}")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить бронирование:\n{e}")

    def edit_booking(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите бронирование для редактирования!")
            return

        item = self.tree.item(selected[0])
        record_id = item["values"][0]

        if not record_id:
            messagebox.showwarning("Предупреждение", "Не удалось определить ID бронирования!")
            return

        try:
            from backend import get_booking
            booking = get_booking(record_id)
            if not booking:
                messagebox.showwarning("Предупреждение", "Бронирование не найдено!")
                return

            fields = [("ID пользователя", "int"), ("ID стола", "int"), ("Начало", "datetime"),
                      ("Окончание", "datetime"), ("Гостей", "int"), ("Статус", "str")]
            window = DataEntryWindow(self.parent, "✏️ Редактировать бронирование", fields, edit_data=booking)
            self.parent.wait_window(window.window)

            if window.result is None:
                return

            def parse_datetime(val):
                if not val:
                    return None
                try:
                    return datetime.strptime(val, "%d.%m.%Y %H:%M")
                except:
                    return None

            update_booking(
                record_id,
                user_id=int(window.result["ID пользователя"]) if window.result.get("ID пользователя") else None,
                table_id=int(window.result["ID стола"]) if window.result.get("ID стола") else None,
                start_time=parse_datetime(window.result.get("Начало")),
                end_time=parse_datetime(window.result.get("Окончание")),
                guests=int(window.result["Гостей"]) if window.result.get("Гостей") else None,
                status=window.result.get("Статус") or None
            )
            messagebox.showinfo("Успех", "Бронирование обновлено!")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить бронирование:\n{e}")

    def delete_booking(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите бронирование для удаления!")
            return

        item = self.tree.item(selected[0])
        record_id = item["values"][0]

        if not messagebox.askyesno("Подтверждение", f"Удалить бронирование ID {record_id}?"):
            return

        try:
            success = delete_booking(record_id)
            if success:
                messagebox.showinfo("Успех", "Бронирование удалено!")
                self.load_data()
            else:
                messagebox.showwarning("Предупреждение", "Не удалось удалить бронирование")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить бронирование:\n{e}")


class BookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🍽 Система бронирования столов")
        self.root.geometry("1200x700")
        self.root.minsize(900, 500)

        self.init_db()
        self.setup_ui()

    def init_db(self):
        try:
            create_tables()
        except Exception as e:
            messagebox.showwarning("Внимание", f"Не удалось создать таблицы:\n{e}\n\nПроверьте подключение к БД.")

    def setup_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        users_tab = tk.Frame(notebook)
        notebook.add(users_tab, text="👥 Пользователи")
        UsersTab(users_tab)

        tables_tab = tk.Frame(notebook)
        notebook.add(tables_tab, text="🪑 Столы")
        TablesTab(tables_tab)

        bookings_tab = tk.Frame(notebook)
        notebook.add(bookings_tab, text="📅 Бронирования")
        BookingsTab(bookings_tab)


def main():
    root = tk.Tk()
    app = BookingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

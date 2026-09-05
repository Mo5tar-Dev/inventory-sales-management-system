
from datetime import datetime
import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False



def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


# USERS SYSTEM


class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role


class Admin(User):
    def __init__(self, username, password):
        super().__init__(username, password, "admin")

    def canManageInventory(self):
        return True


class Employee(User):
    def __init__(self, username, password):
        super().__init__(username, password, "employee")

    def canManageInventory(self):
        return False


class LoginManager:
    def __init__(self):
        self.users = []
        self.load_users()

    def add_user(self, user):
        if self.search_user(user.username):
            return False
        self.users.append(user)
        self.save_users()
        return True

    def search_user(self, username):
        username = username.strip().lower()
        for user in self.users:
            if user.username.lower() == username:
                return user
        return None

    def remove_user(self, username):
        username = username.strip()
        if username.lower() == "admin":
            return False
        user = self.search_user(username)
        if user:
            self.users.remove(user)
            self.save_users()
            return True
        return False

    def login(self, username, password):
        username = username.strip()
        password = password.strip()
        for user in self.users:
            if user.username == username and user.password == password:
                return user
        return None

    def save_users(self):
        data = []
        for user in self.users:
            data.append({
                "username": user.username,
                "password": user.password,
                "role": user.role
            })
        with open("users.json", "w") as file:
            json.dump(data, file, indent=4)

    def load_users(self):
        try:
            with open("users.json", "r") as file:
                data = json.load(file)
                for item in data:
                    username = item.get("username", "").strip()
                    password = item.get("password", "").strip()
                    role = item.get("role", "employee")

                    if not username or not password:
                        continue

                    user = Admin(username, password) if role == "admin" else Employee(username, password)
                    if not self.search_user(user.username):
                        self.users.append(user)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(e)


#  MAIN CLASSES


class Entity:
    def __init__(self, id, name):
        self.id = id
        self.name = name.lower()


class Product(Entity):
    def __init__(self, id, name, price, quantity, category):
        super().__init__(id, name)
        self.price = price
        self.__quantity = quantity
        self.category = category

    def add_stock(self, amount):
        if amount > 0:
            self.__quantity += amount

    def reduce_stock(self, amount):
        if amount > 0 and amount <= self.__quantity:
            self.__quantity -= amount
            return True
        return False

    def update_price(self, new_price):
        if new_price > 0:
            self.price = new_price
            return True
        return False

    def get_quantity(self):
        return self.__quantity

    def set_quantity(self, new_quantity):
        if new_quantity >= 0:
            self.__quantity = new_quantity
            return True
        return False

    def display(self):
        return (
            f"ID:{self.id} | Name:{self.name} | Price:{self.price} | "
            f"Quantity:{self.__quantity} | Category:{self.category}"
        )

class Customer(Entity):
    def __init__(self, id, name, phone):
        super().__init__(id, name)
        self.phone = phone

    def display_customer(self):
        return f"Customer_ID:{self.id} | Name:{self.name} | Phone:{self.phone}"


class CustomerManager:
    def __init__(self):
        self.customers = []
        self.load_customers()

    def list_customers(self):
        return self.customers

    def search_customer(self, id):
        for customer in self.customers:
            if customer.id == id:
                return customer
        return None

    def search_by_name(self, name):
        name = name.lower().strip()
        return [c for c in self.customers if name in c.name]

    def add_customer(self, customer):
        if customer.id <= 0:
            return "Invalid ID"
        if not customer.name.strip():
            return "Invalid Name"
        if self.search_customer(customer.id):
            return "Duplicate ID"
        self.customers.append(customer)
        self.save_customers()
        return "Success"

    def remove_customer(self, id):
        customer = self.search_customer(id)
        if customer:
            self.customers.remove(customer)
            self.save_customers()
            return True
        return False

    def save_customers(self):
        data = []
        for customer in self.customers:
            data.append({
                "id": customer.id,
                "name": customer.name,
                "phone": customer.phone
            })
        with open("customers.json", "w") as file:
            json.dump(data, file, indent=4)

    def load_customers(self):
        try:
            with open("customers.json", "r") as file:
                data = json.load(file)
                for item in data:
                    customer = Customer(item["id"], item["name"], item["phone"])
                    if not self.search_customer(customer.id):
                        self.customers.append(customer)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(e)

class Order:
    def __init__(self, order_id, customer, product, quantity):
        self.order_id = order_id
        self.customer = customer
        self.product = product
        self.quantity = quantity
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.time = datetime.now().strftime("%H:%M:%S")

    def calc_total(self):
        return self.product.price * self.quantity

    def display_order(self):
        return (
            f"Order_ID:{self.order_id} | Customer:{self.customer.name} | "
            f"Product:{self.product.name} | Quantity:{self.quantity} | Total:{self.calc_total()}"
        )

class InventoryManager:
    def __init__(self):
        self.products = []

    def list_products(self):
        return self.products

    def search_product(self, id):
        for product in self.products:
            if product.id == id:
                return product
        return None

    def search_products(self, query):
        query = query.lower().strip()
        results = []
        for product in self.products:
            if (
                query == str(product.id)
                or query in product.name.lower()
                or query in product.category.lower()
            ):
                results.append(product)
        return results

    def add_product(self, product):
        if product.id <= 0:
            return "Invalid ID"
        if not product.name.strip():
            return "Invalid Name"
        if self.search_product(product.id):
            return "Duplicate ID"
        if product.price <= 0:
            return "Invalid Price"
        if product.get_quantity() < 0:
            return "Invalid Quantity"
        if not product.category.strip():
            return "Invalid Category"
        
        self.products.append(product)
        return "Success"

    def remove_product(self, id):
        product = self.search_product(id)
        if product:
            self.products.remove(product)
            return True
        return False

    def update(self, id, new_name=None, new_price=None, new_quantity=None, new_category=None):
        product = self.search_product(id)
        if not product:
            return "Product Not Found"

        if new_name is not None and not new_name.strip():
            return "Invalid Name"
        if new_price is not None and new_price <= 0:
            return "Invalid Price"
        if new_quantity is not None and new_quantity < 0:
            return "Invalid Quantity"
        if new_category is not None and not new_category.strip():
            return "Invalid Category"

        if new_name is not None:
            product.name = new_name.lower()
        if new_price is not None:
            product.price = new_price
        if new_quantity is not None:
            product.set_quantity(new_quantity)
        if new_category is not None:
            product.category = new_category
        return "Success"

    def save_products(self):
        data = []
        for product in self.products:
            data.append({
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": product.get_quantity(),
                "category": product.category
            })
        with open("products.json", "w") as file:
            json.dump(data, file, indent=4)

    def load_products(self):
        try:
            with open("products.json", "r") as file:
                data = json.load(file)
                for item in data:
                    p = Product(
                        int(item["id"]),
                        item["name"],
                        float(item["price"]),
                        int(item["quantity"]),
                        item["category"]
                    )
                    if p.id > 0 and p.price > 0 and p.get_quantity() >= 0 and not self.search_product(p.id):
                        self.products.append(p)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(e)

class Bill:
    def __init__(self, product_name, quantity, unit_price, customer_name="Unknown"):
        self.product_name = product_name
        self.quantity = quantity
        self.unit_price = unit_price
        self.customer_name = customer_name
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.time = datetime.now().strftime("%H:%M:%S")

    def calc_total_price(self):
        return self.quantity * self.unit_price

    def display(self):
        return (
            f"Customer:{self.customer_name} | Product:{self.product_name} | "
            f"Quantity:{self.quantity} | Unit Price:{self.unit_price} | "
            f"Total:{self.calc_total_price()} | Date:{self.date} | Time:{self.time}"
        )


class SalesManager:
    def __init__(self, inventory):
        self.inventory = inventory
        self.sales_his = []
        self.orders = []
        self.load_sales()

    def sell_product(self, id, quantity, customer=None):
        product = self.inventory.search_product(id)
        if not product:
            return "Product Not Found"
        if quantity <= 0:
            return "Invalid Quantity"
        if quantity > product.get_quantity():
            return "Not enough stock"

        product.reduce_stock(quantity)
        self.inventory.save_products()

        customer_name = customer.name if customer else "Unknown"
        bill = Bill(product.name, quantity, product.price, customer_name)
        self.sales_his.append(bill)

        if customer:
            order = Order(len(self.orders) + 1, customer, product, quantity)
            self.orders.append(order)

        self.save_sales()
        return bill

    def sales_history(self):
        return self.sales_his

    def total_profit(self):
        total = 0
        for bill in self.sales_his:
            total += bill.calc_total_price()
        return total

    def reset_sales(self):
        self.sales_his.clear()
        self.orders.clear()
        self.save_sales()

    def save_sales(self):
        data = []
        for bill in self.sales_his:
            data.append({
                "product_name": bill.product_name,
                "quantity": bill.quantity,
                "unit_price": bill.unit_price,
                "customer_name": bill.customer_name,
                "date": bill.date,
                "time": bill.time
            })
        with open("sales.json", "w") as file:
            json.dump(data, file, indent=4)

    def load_sales(self):
        try:
            with open("sales.json", "r") as file:
                data = json.load(file)
                for item in data:
                    bill = Bill(
                        item["product_name"],
                        int(item["quantity"]),
                        float(item["unit_price"]),
                        item.get("customer_name", "Unknown")
                    )
                    bill.date = item["date"]
                    bill.time = item["time"]
                    self.sales_his.append(bill)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(e)


class SystemController:
    def __init__(self, inventory, sales_manager, customer_manager):
        self.inventory = inventory
        self.sales_manager = sales_manager
        self.customer_manager = customer_manager
        self.current_user = None

    def login(self, user):
        self.current_user = user

    def logout(self):
        self.current_user = None

    def is_admin(self):
        return self.current_user and self.current_user.role == "admin"

    def add_product(self, product):
        if not self.is_admin():
            return "Access Denied"
        result = self.inventory.add_product(product)
        if result == "Success":
            self.inventory.save_products()
        return result

    def remove_product(self, id):
        if not self.is_admin():
            return False
        result = self.inventory.remove_product(id)
        if result:
            self.inventory.save_products()
        return result

    def update_product(self, id, new_name=None, new_price=None, new_quantity=None, new_category=None):
        if not self.is_admin():
            return "Access Denied"
        result = self.inventory.update(id, new_name, new_price, new_quantity, new_category)
        if result == "Success":
            self.inventory.save_products()
        return result

    def add_customer(self, customer):
        if not self.current_user:
            return "Please Login First"
        return self.customer_manager.add_customer(customer)

    def sell_product(self, product_id, quantity, customer_id):
        if not self.current_user:
            return "Please Login First"
        customer = self.customer_manager.search_customer(customer_id)
        if not customer:
            return "Customer Not Found"
        return self.sales_manager.sell_product(product_id, quantity, customer)



# GUI


class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory & Sales Management System")
        self.geometry("1150x700")
        self.minsize(980, 620)
        self.configure(bg="#0f172a")

        self.inventory = InventoryManager()
        self.inventory.load_products()
        self.customers = CustomerManager()
        self.sales = SalesManager(self.inventory)
        self.system = SystemController(self.inventory, self.sales, self.customers)
        self.login_system = LoginManager()
        self.login_system.add_user(Admin("admin", "123"))
        self.login_system.add_user(Employee("emp", "123"))

        self.colors = {
            "bg": "#0f172a",
            "side": "#111827",
            "card": "#1e293b",
            "text": "#f8fafc",
            "muted": "#94a3b8",
            "accent": "#38bdf8",
            "danger": "#ef4444",
            "success": "#22c55e",
            "entry": "#e5e7eb"
        }
        self.setup_styles()
        self.show_login()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Arial", 11), rowheight=30, background="#f8fafc", fieldbackground="#f8fafc")
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#bae6fd", foreground="#0f172a")
        style.configure("TCombobox", padding=5)

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def make_entry(self, parent, show=None):
        return tk.Entry(parent, font=("Arial", 13), bg=self.colors["entry"], fg="#111827", relief="flat", show=show)

    def make_button(self, parent, text, command, bg=None):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 12, "bold"),
            bg=bg or self.colors["accent"],
            fg="#0f172a",
            activebackground="#7dd3fc",
            activeforeground="#0f172a",
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=9
        )

    def show_result_message(self, result, success_text):
        if result == "Success":
            messagebox.showinfo("Success", success_text)
        elif result == "Duplicate ID":
            messagebox.showerror("Error", "ID already exists")
        elif result == "Invalid ID":
            messagebox.showerror("Error", "ID must be greater than 0")
        elif result == "Invalid Name":
            messagebox.showerror("Error", "Name is required")
        elif result == "Invalid Price":
            messagebox.showerror("Error", "Price must be greater than 0")
        elif result == "Invalid Quantity":
            messagebox.showerror("Error", "Quantity cannot be negative")
        elif result == "Invalid Category":
            messagebox.showerror("Error", "Category is required")
        elif result == "Access Denied":
            messagebox.showerror("Error", "Only admin can do this action")
        elif result == "Product Not Found":
            messagebox.showerror("Error", "Product not found")
        else:
            messagebox.showerror("Error", str(result))

    def show_login(self):
        self.clear_window()

        wrapper = tk.Frame(self, bg=self.colors["bg"])
        wrapper.pack(expand=True, fill="both")

        # ==================== LOGIN WALLPAPER ====================
        bg_path = resource_path("invetory.png")
        self.login_bg_label = tk.Label(wrapper, bg=self.colors["bg"], bd=0)
        self.login_bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        if os.path.exists(bg_path):
            if PIL_AVAILABLE:
                # Keep the image sharp and make it fill the window even after resizing.
                self.login_bg_original = Image.open(bg_path).convert("RGB")

                def resize_login_background(event):
                    width = max(event.width, 2)
                    height = max(event.height, 2)

                    img_w, img_h = self.login_bg_original.size
                    scale = max(width / img_w, height / img_h)
                    new_w = max(int(img_w * scale), 2)
                    new_h = max(int(img_h * scale), 2)

                    resized = self.login_bg_original.resize((new_w, new_h), Image.LANCZOS)

                    left = max((new_w - width) // 2, 0)
                    top = max((new_h - height) // 2, 0)
                    cropped = resized.crop((left, top, left + width, top + height))

                    self.login_bg_photo = ImageTk.PhotoImage(cropped)
                    self.login_bg_label.config(image=self.login_bg_photo)

                wrapper.bind("<Configure>", resize_login_background)
            else:
                try:
                    self.login_bg_photo = tk.PhotoImage(file=bg_path)
                    self.login_bg_label.config(image=self.login_bg_photo)
                except tk.TclError:
                    pass

        card = tk.Frame(
            wrapper,
            bg=self.colors["card"],
            padx=40,
            pady=35,
            highlightbackground="#334155",
            highlightthickness=1
        )
        card.place(relx=0.5, rely=0.5, anchor="center", width=430, height=390)

        tk.Label(
            card,
            text="Inventory System",
            font=("Arial", 24, "bold"),
            bg=self.colors["card"],
            fg=self.colors["text"]
        ).pack(pady=(0, 8))

        tk.Label(
            card,
            text="Login to continue",
            font=("Arial", 12),
            bg=self.colors["card"],
            fg=self.colors["muted"]
        ).pack(pady=(0, 25))

        tk.Label(
            card,
            text="Username",
            font=("Arial", 12, "bold"),
            bg=self.colors["card"],
            fg=self.colors["text"]
        ).pack(anchor="w")

        username_entry = tk.Entry(
            card,
            font=("Arial", 13),
            bg=self.colors["entry"],
            fg="#111827",
            relief="flat"
        )
        username_entry.pack(fill="x", ipady=8, pady=(5, 15))

        tk.Label(
            card,
            text="Password",
            font=("Arial", 12, "bold"),
            bg=self.colors["card"],
            fg=self.colors["text"]
        ).pack(anchor="w")

        password_entry = tk.Entry(
            card,
            font=("Arial", 13),
            bg=self.colors["entry"],
            fg="#111827",
            relief="flat",
            show="*"
        )
        password_entry.pack(fill="x", ipady=8, pady=(5, 20))

        def do_login(event=None):
            user = self.login_system.login(
                username_entry.get().strip(),
                password_entry.get().strip()
            )

            if user:
                self.system.login(user)
                self.show_main_layout()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")

        btn = self.make_button(card, "Login", do_login)
        btn.pack(fill="x")

        password_entry.bind("<Return>", do_login)
        username_entry.focus()

        hint = tk.Label(
            card,
            text="Admin: admin / 123    Employee: emp / 123",
            font=("Arial", 10),
            bg=self.colors["card"],
            fg=self.colors["muted"]
        )
        hint.pack(pady=(18, 0))

    def show_main_layout(self):
        self.clear_window()
        self.sidebar = tk.Frame(self, bg=self.colors["side"], width=235)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(self, bg=self.colors["bg"])
        self.content.pack(side="right", expand=True, fill="both")

        user = self.system.current_user
        tk.Label(self.sidebar, text="MENU", font=("Arial", 20, "bold"), bg=self.colors["side"], fg=self.colors["accent"]).pack(pady=(25, 5))
        tk.Label(self.sidebar, text=f"{user.username} ({user.role})", font=("Arial", 11), bg=self.colors["side"], fg=self.colors["muted"]).pack(pady=(0, 25))

        self.add_sidebar_button("Dashboard", self.show_dashboard)
        self.add_sidebar_button("View Products", self.show_view_products)
        self.add_sidebar_button("Customers", self.show_customers_page)
        self.add_sidebar_button("Sell Product", self.show_sell_product)
        self.add_sidebar_button("Sales History", self.show_sales_history)
        self.add_sidebar_button("Total Profit", self.show_total_profit)

        if self.system.is_admin():
            tk.Label(self.sidebar, text="ADMIN TOOLS", font=("Arial", 10, "bold"), bg=self.colors["side"], fg=self.colors["muted"]).pack(pady=(18, 5))
            self.add_sidebar_button("Add Product", self.show_add_product)
            self.add_sidebar_button("Update Product", self.show_update_product)
            self.add_sidebar_button("Remove Product", self.show_remove_product)
            self.add_sidebar_button("Users", self.show_users_page)

        tk.Frame(self.sidebar, bg=self.colors["side"]).pack(expand=True, fill="both")
        self.add_sidebar_button("Logout", self.logout, bg=self.colors["danger"])
        self.show_dashboard()

    def add_sidebar_button(self, text, command, bg=None):
        btn = tk.Button(
            self.sidebar,
            text=text,
            command=command,
            font=("Arial", 12, "bold"),
            bg=bg or self.colors["card"],
            fg=self.colors["text"],
            activebackground=self.colors["accent"],
            activeforeground="#0f172a",
            relief="flat",
            cursor="hand2",
            anchor="w",
            padx=18,
            pady=10
        )
        btn.pack(fill="x", padx=12, pady=4)

    def clear_content(self, title):
        for widget in self.content.winfo_children():
            widget.destroy()
        tk.Label(self.content, text=title, font=("Arial", 24, "bold"), bg=self.colors["bg"], fg=self.colors["text"]).pack(anchor="w", padx=30, pady=(25, 15))
        body = tk.Frame(self.content, bg=self.colors["bg"])
        body.pack(expand=True, fill="both", padx=30, pady=10)
        return body

    def make_card(self, parent, title, value):
        card = tk.Frame(parent, bg=self.colors["card"], padx=22, pady=18)
        tk.Label(card, text=title, font=("Arial", 12), bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w")
        tk.Label(card, text=value, font=("Arial", 24, "bold"), bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=(8, 0))
        return card

    def show_dashboard(self):
        body = self.clear_content("Dashboard")
        products = self.inventory.list_products()
        low_stock = len([p for p in products if p.get_quantity() <= 3])
        cards = tk.Frame(body, bg=self.colors["bg"])
        cards.pack(fill="x")
        self.make_card(cards, "Total Products", str(len(products))).pack(side="left", expand=True, fill="x", padx=8)
        self.make_card(cards, "Customers", str(len(self.customers.list_customers()))).pack(side="left", expand=True, fill="x", padx=8)
        self.make_card(cards, "Sales Count", str(len(self.sales.sales_history()))).pack(side="left", expand=True, fill="x", padx=8)
        self.make_card(cards, "Total Profit", f"{self.sales.total_profit():.2f}").pack(side="left", expand=True, fill="x", padx=8)
        self.make_card(cards, "Low Stock", str(low_stock)).pack(side="left", expand=True, fill="x", padx=8)

        tk.Label(body, text="Low Stock Products", font=("Arial", 16, "bold"), bg=self.colors["bg"], fg=self.colors["text"]).pack(anchor="w", pady=(35, 10))
        self.create_products_table(body, [p for p in products if p.get_quantity() <= 3])

    def create_products_table(self, parent, products=None):
        if products is None:
            products = self.inventory.list_products()
        frame = tk.Frame(parent, bg=self.colors["bg"])
        frame.pack(expand=True, fill="both")
        columns = ("ID", "Name", "Price", "Quantity", "Category")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=130)
        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=y_scroll.set)
        tree.pack(side="left", expand=True, fill="both")
        y_scroll.pack(side="right", fill="y")
        for p in products:
            tree.insert("", "end", values=(p.id, p.name, p.price, p.get_quantity(), p.category))
        return tree

    def create_customers_table(self, parent, customers=None):
        if customers is None:
            customers = self.customers.list_customers()
        frame = tk.Frame(parent, bg=self.colors["bg"])
        frame.pack(expand=True, fill="both")
        columns = ("ID", "Name", "Phone")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)
        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=y_scroll.set)
        tree.pack(side="left", expand=True, fill="both")
        y_scroll.pack(side="right", fill="y")
        for c in customers:
            tree.insert("", "end", values=(c.id, c.name, c.phone))
        return tree

    def show_view_products(self):
        body = self.clear_content("View Products")
        search_frame = tk.Frame(body, bg=self.colors["bg"])
        search_frame.pack(fill="x", pady=(0, 15))
        tk.Label(search_frame, text="Search by ID / name / category:", bg=self.colors["bg"], fg=self.colors["text"], font=("Arial", 12, "bold")).pack(side="left")
        search_entry = self.make_entry(search_frame)
        search_entry.pack(side="left", fill="x", expand=True, padx=10, ipady=7)
        table_holder = tk.Frame(body, bg=self.colors["bg"])
        table_holder.pack(expand=True, fill="both")

        def refresh(products=None):
            for w in table_holder.winfo_children():
                w.destroy()
            self.create_products_table(table_holder, products)

        def do_search():
            q = search_entry.get().strip()
            if not q:
                refresh()
                return
            refresh(self.inventory.search_products(q))

        self.make_button(search_frame, "Search", do_search).pack(side="left")
        self.make_button(search_frame, "Reset", lambda: refresh(), bg="#cbd5e1").pack(side="left", padx=8)
        refresh()

    def product_form(self, parent):
        fields = ["ID", "Name", "Price", "Quantity", "Category"]
        entries = {}
        for i, field in enumerate(fields):
            tk.Label(parent, text=field, bg=self.colors["card"], fg=self.colors["text"], font=("Arial", 12, "bold")).grid(row=i, column=0, sticky="w", pady=8, padx=(0, 15))
            entry = tk.Entry(parent, font=("Arial", 13), bg=self.colors["entry"], relief="flat")
            entry.grid(row=i, column=1, sticky="ew", ipady=7, pady=8)
            entries[field] = entry
        parent.columnconfigure(1, weight=1)
        return entries

    def show_add_product(self):
        body = self.clear_content("Add Product")
        form = tk.Frame(body, bg=self.colors["card"], padx=30, pady=25)
        form.pack(anchor="nw", fill="x")
        entries = self.product_form(form)

        def add():
            try:
                product = Product(
                    int(entries["ID"].get()),
                    entries["Name"].get().strip(),
                    float(entries["Price"].get()),
                    int(entries["Quantity"].get()),
                    entries["Category"].get().strip()
                )
                result = self.system.add_product(product)
                if result == "Success":
                    messagebox.showinfo("Success", "Product added successfully")
                    for entry in entries.values():
                        entry.delete(0, tk.END)
                    entries["ID"].focus()
                else:
                    self.show_result_message(result, "Product added successfully")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for ID, Price, and Quantity")

        self.make_button(form, "Add Product", add, self.colors["success"]).grid(row=5, column=1, sticky="ew", pady=15)

    def show_update_product(self):
        body = self.clear_content("Update Product")
        form = tk.Frame(body, bg=self.colors["card"], padx=30, pady=25)
        form.pack(anchor="nw", fill="x")
        entries = self.product_form(form)

        def load_product():
            try:
                product = self.inventory.search_product(int(entries["ID"].get()))
                if not product:
                    messagebox.showerror("Error", "Product not found")
                    return
                entries["Name"].delete(0, tk.END); entries["Name"].insert(0, product.name)
                entries["Price"].delete(0, tk.END); entries["Price"].insert(0, product.price)
                entries["Quantity"].delete(0, tk.END); entries["Quantity"].insert(0, product.get_quantity())
                entries["Category"].delete(0, tk.END); entries["Category"].insert(0, product.category)
            except ValueError:
                messagebox.showerror("Error", "Enter valid product ID")

        def update():
            try:
                result = self.system.update_product(
                    int(entries["ID"].get()),
                    entries["Name"].get().strip(),
                    float(entries["Price"].get()),
                    int(entries["Quantity"].get()),
                    entries["Category"].get().strip()
                )
                if result == "Success":
                    messagebox.showinfo("Success", "Product updated successfully")
                else:
                    self.show_result_message(result, "Product updated successfully")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")

        self.make_button(form, "Load Product", load_product).grid(row=5, column=0, sticky="ew", pady=15, padx=(0, 10))
        self.make_button(form, "Update Product", update, self.colors["success"]).grid(row=5, column=1, sticky="ew", pady=15)

    def show_remove_product(self):
        body = self.clear_content("Remove Product")
        form = tk.Frame(body, bg=self.colors["card"], padx=30, pady=25)
        form.pack(anchor="nw", fill="x")
        tk.Label(form, text="Product ID", bg=self.colors["card"], fg=self.colors["text"], font=("Arial", 12, "bold")).pack(anchor="w")
        id_entry = tk.Entry(form, font=("Arial", 13), bg=self.colors["entry"], relief="flat")
        id_entry.pack(fill="x", ipady=8, pady=(8, 15))

        def remove():
            try:
                product_id = int(id_entry.get())
                if product_id <= 0:
                    messagebox.showerror("Error", "ID must be greater than 0")
                    return
                if messagebox.askyesno("Confirm", "Are you sure you want to remove this product?"):
                    if self.system.remove_product(product_id):
                        messagebox.showinfo("Success", "Product removed")
                        id_entry.delete(0, tk.END)
                        self.show_remove_product()
                    else:
                        messagebox.showerror("Error", "Product not found or permission denied")
            except ValueError:
                messagebox.showerror("Error", "Enter valid product ID")

        self.make_button(form, "Remove Product", remove, self.colors["danger"]).pack(anchor="e")
        tk.Label(body, text="Current Products", font=("Arial", 16, "bold"), bg=self.colors["bg"], fg=self.colors["text"]).pack(anchor="w", pady=(25, 10))
        self.create_products_table(body)

    def show_customers_page(self):
        body = self.clear_content("Customers")
        form = tk.Frame(body, bg=self.colors["card"], padx=30, pady=25)
        form.pack(fill="x")

        tk.Label(form, text="Customer ID", bg=self.colors["card"], fg=self.colors["text"], font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", pady=8)
        id_entry = tk.Entry(form, font=("Arial", 13), bg=self.colors["entry"], relief="flat")
        id_entry.grid(row=0, column=1, sticky="ew", ipady=7, pady=8, padx=12)

        tk.Label(form, text="Name", bg=self.colors["card"], fg=self.colors["text"], font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w", pady=8)
        name_entry = tk.Entry(form, font=("Arial", 13), bg=self.colors["entry"], relief="flat")
        name_entry.grid(row=1, column=1, sticky="ew", ipady=7, pady=8, padx=12)

        tk.Label(form, text="Phone", bg=self.colors["card"], fg=self.colors["text"], font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", pady=8)
        phone_entry = tk.Entry(form, font=("Arial", 13), bg=self.colors["entry"], relief="flat")
        phone_entry.grid(row=2, column=1, sticky="ew", ipady=7, pady=8, padx=12)
        form.columnconfigure(1, weight=1)

        table_holder = tk.Frame(body, bg=self.colors["bg"])
        table_holder.pack(expand=True, fill="both", pady=(25, 0))

        def refresh():
            for w in table_holder.winfo_children():
                w.destroy()
            self.create_customers_table(table_holder)

        def add_customer():
            try:
                customer = Customer(int(id_entry.get()), name_entry.get().strip(), phone_entry.get().strip())
                result = self.system.add_customer(customer)
                if result == "Success":
                    messagebox.showinfo("Success", "Customer added successfully")
                    id_entry.delete(0, tk.END)
                    name_entry.delete(0, tk.END)
                    phone_entry.delete(0, tk.END)
                    refresh()
                elif result == "Duplicate ID":
                    messagebox.showerror("Error", "Customer ID already exists")
                elif result == "Invalid ID":
                    messagebox.showerror("Error", "ID must be greater than 0")
                else:
                    messagebox.showerror("Error", str(result))
            except ValueError:
                messagebox.showerror("Error", "Enter valid customer ID")

        def remove_customer():
            try:
                customer_id = int(id_entry.get())
                if self.customers.remove_customer(customer_id):
                    messagebox.showinfo("Success", "Customer removed")
                    refresh()
                else:
                    messagebox.showerror("Error", "Customer not found")
            except ValueError:
                messagebox.showerror("Error", "Enter valid customer ID")

        btns = tk.Frame(form, bg=self.colors["card"])
        btns.grid(row=3, column=1, sticky="e", pady=15)
        self.make_button(btns, "Add Customer", add_customer, self.colors["success"]).pack(side="left", padx=5)
        self.make_button(btns, "Remove Customer", remove_customer, self.colors["danger"]).pack(side="left", padx=5)
        refresh()

    def show_sell_product(self):
        body = self.clear_content("Sell Product")
        form = tk.Frame(body, bg=self.colors["card"], padx=30, pady=25)
        form.pack(anchor="nw", fill="x")

        labels = ["Customer ID", "Product ID", "Quantity"]
        entries = {}
        for i, label in enumerate(labels):
            tk.Label(form, text=label, bg=self.colors["card"], fg=self.colors["text"], font=("Arial", 12, "bold")).grid(row=i, column=0, sticky="w", pady=8)
            entry = tk.Entry(form, font=("Arial", 13), bg=self.colors["entry"], relief="flat")
            entry.grid(row=i, column=1, sticky="ew", ipady=7, pady=8, padx=12)
            entries[label] = entry
        form.columnconfigure(1, weight=1)

        result_label = tk.Label(form, text="", bg=self.colors["card"], fg=self.colors["text"], font=("Arial", 12), justify="left")
        result_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=15)

        def sell():
            try:
                customer_id = int(entries["Customer ID"].get())
                product_id = int(entries["Product ID"].get())
                qty = int(entries["Quantity"].get())
                result = self.system.sell_product(product_id, qty, customer_id)
                if isinstance(result, Bill):
                    result_label.config(text=result.display())
                    messagebox.showinfo("Sold", "Product sold successfully")
                    for entry in entries.values():
                        entry.delete(0, tk.END)
                    self.show_sell_product()
                else:
                    messagebox.showerror("Error", result)
            except ValueError:
                messagebox.showerror("Error", "Enter valid customer ID, product ID, and quantity")

        self.make_button(form, "Sell", sell, self.colors["success"]).grid(row=3, column=1, sticky="e", pady=15)

        tables = tk.Frame(body, bg=self.colors["bg"])
        tables.pack(expand=True, fill="both", pady=(25, 0))

        left = tk.Frame(tables, bg=self.colors["bg"])
        left.pack(side="left", expand=True, fill="both", padx=(0, 10))
        right = tk.Frame(tables, bg=self.colors["bg"])
        right.pack(side="left", expand=True, fill="both", padx=(10, 0))

        tk.Label(left, text="Available Products", font=("Arial", 16, "bold"), bg=self.colors["bg"], fg=self.colors["text"]).pack(anchor="w", pady=(0, 10))
        self.create_products_table(left)
        tk.Label(right, text="Customers", font=("Arial", 16, "bold"), bg=self.colors["bg"], fg=self.colors["text"]).pack(anchor="w", pady=(0, 10))
        self.create_customers_table(right)

    def show_sales_history(self):
        body = self.clear_content("Sales History")
        frame = tk.Frame(body, bg=self.colors["bg"])
        frame.pack(expand=True, fill="both")
        columns = ("Customer", "Product", "Quantity", "Unit Price", "Total", "Date", "Time")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)
        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=y_scroll.set)
        tree.pack(side="left", expand=True, fill="both")
        y_scroll.pack(side="right", fill="y")
        for bill in self.sales.sales_history():
            tree.insert("", "end", values=(bill.customer_name, bill.product_name, bill.quantity, bill.unit_price, bill.calc_total_price(), bill.date, bill.time))

    def show_total_profit(self):
        body = self.clear_content("Total Profit")
        card = self.make_card(body, "Total Profit From Sales", f"{self.sales.total_profit():.2f}")
        card.pack(anchor="nw", fill="x", pady=10)

        if self.system.is_admin():
            def reset_sales_data():
                if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all sales history and profit?"):
                    self.sales.reset_sales()
                    messagebox.showinfo("Success", "Sales history and profit reset successfully")
                    self.show_total_profit()

            self.make_button(body, "Reset Sales & Profit", reset_sales_data, self.colors["danger"]).pack(anchor="nw", pady=15)

    def show_users_page(self):
        body = self.clear_content("Users Management")
        form = tk.Frame(body, bg=self.colors["card"], padx=30, pady=25)
        form.pack(fill="x")
        tk.Label(form, text="Username", bg=self.colors["card"], fg=self.colors["text"], font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", pady=8)
        username = tk.Entry(form, font=("Arial", 13), bg=self.colors["entry"], relief="flat")
        username.grid(row=0, column=1, sticky="ew", ipady=7, pady=8, padx=12)
        tk.Label(form, text="Password", bg=self.colors["card"], fg=self.colors["text"], font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w", pady=8)
        password = tk.Entry(form, font=("Arial", 13), bg=self.colors["entry"], relief="flat")
        password.grid(row=1, column=1, sticky="ew", ipady=7, pady=8, padx=12)
        tk.Label(form, text="Role", bg=self.colors["card"], fg=self.colors["text"], font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", pady=8)
        role = ttk.Combobox(form, values=["admin", "employee"], state="readonly", font=("Arial", 12))
        role.current(1)
        role.grid(row=2, column=1, sticky="ew", ipady=5, pady=8, padx=12)
        form.columnconfigure(1, weight=1)

        table_holder = tk.Frame(body, bg=self.colors["bg"])
        table_holder.pack(expand=True, fill="both", pady=(25, 0))

        def refresh_users():
            for w in table_holder.winfo_children():
                w.destroy()
            columns = ("Username", "Role")
            tree = ttk.Treeview(table_holder, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor="center")
            tree.pack(expand=True, fill="both")
            for u in self.login_system.users:
                tree.insert("", "end", values=(u.username, u.role))

        def add_user():
            if not username.get().strip() or not password.get().strip():
                messagebox.showerror("Error", "Username and password are required")
                return
            new_user = Admin(username.get().strip(), password.get().strip()) if role.get() == "admin" else Employee(username.get().strip(), password.get().strip())
            if self.login_system.add_user(new_user):
                messagebox.showinfo("Success", "User added")
                username.delete(0, tk.END)
                password.delete(0, tk.END)
                refresh_users()
            else:
                messagebox.showerror("Error", "Username already exists")

        def delete_user():
            if self.login_system.remove_user(username.get().strip()):
                messagebox.showinfo("Success", "User removed")
                username.delete(0, tk.END)
                refresh_users()
            else:
                messagebox.showerror("Error", "Cannot remove user. Check username. Main admin cannot be removed")

        btns = tk.Frame(form, bg=self.colors["card"])
        btns.grid(row=3, column=1, sticky="e", pady=15)
        self.make_button(btns, "Add User", add_user, self.colors["success"]).pack(side="left", padx=5)
        self.make_button(btns, "Delete User", delete_user, self.colors["danger"]).pack(side="left", padx=5)
        refresh_users()

    def logout(self):
        self.system.logout()
        self.show_login()


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()

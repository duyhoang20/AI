import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QTextEdit, 
    QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QTableWidget, QTableWidgetItem
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class KnapsackApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bài Toán Knapsack - Siêu Thị")
        self.setGeometry(200, 200, 1200, 800)
        self.products = []

        layout = QVBoxLayout()

        # Nhập trọng lượng tối đa
        self.weight_label = QLabel("Nhập trọng lượng tối đa của Máy bay:")
        self.weight_input = QLineEdit()
        layout.addWidget(self.weight_label)
        layout.addWidget(self.weight_input)

        # Nút chọn file
        self.file_button = QPushButton("Chọn file danh sách món đồ")
        self.file_button.clicked.connect(self.select_file)
        layout.addWidget(self.file_button)

        # Tìm kiếm sản phẩm
        self.search_label = QLabel("Tìm kiếm sản phẩm:")
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.search_products)
        layout.addWidget(self.search_label)
        layout.addWidget(self.search_input)

        # Bảng sản phẩm
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["Tên", "Giá trị", "Trọng lượng", "Hình ảnh"])
        layout.addWidget(self.products_table)

        # Nút tính toán
        self.calculate_button = QPushButton("Tính toán")
        self.calculate_button.clicked.connect(self.solve_knapsack)
        layout.addWidget(self.calculate_button)

        # Kết quả
        self.result_label = QLabel("Kết quả:")
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_label)
        layout.addWidget(self.result_text)

        # Layout cho biểu đồ
        chart_layout = QHBoxLayout()
        
        # Biểu đồ cột
        self.figure = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)

        # Biểu đồ tròn
        self.figure_pie = Figure(figsize=(6, 4))
        self.canvas_pie = FigureCanvas(self.figure_pie)
        chart_layout.addWidget(self.canvas_pie)

        # Thêm layout biểu đồ vào layout chính
        layout.addLayout(chart_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn file danh sách món đồ", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            self.load_products(file_name)

    def load_products(self, file_name):
        self.products = []
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) == 4:
                        name, value, weight, image = parts
                        self.products.append((name, int(value), int(weight), image))
        except Exception as e:
            self.result_text.append(f"Lỗi đọc file: {e}")
        self.update_product_table(self.products)

    def update_product_table(self, products):
        self.products_table.setRowCount(len(products))
        for row, product in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(product[0]))
            self.products_table.setItem(row, 1, QTableWidgetItem(str(product[1])))
            self.products_table.setItem(row, 2, QTableWidgetItem(str(product[2])))

            # Xử lý hình ảnh an toàn
            image_path = product[3]
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                # Sử dụng ảnh mặc định nếu không tải được
                pixmap = QPixmap(os.path.join(os.path.dirname(__file__), 'default_image.png'))
            
            item = QLabel()
            item.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.products_table.setCellWidget(row, 3, item)

    def search_products(self):
        query = self.search_input.text().lower()
        filtered = [p for p in self.products if query in p[0].lower()]
        self.update_product_table(filtered)

    def solve_knapsack(self):
        try:
            max_weight = int(self.weight_input.text())
            total_value, selected_items = self.knapsack_backtracking(self.products, max_weight)

            total_selected_weight = sum(item[2] for item in selected_items)
            fill_percentage = (total_selected_weight / max_weight) * 100

            self.result_text.clear()
            self.result_text.append(f"Phần trăm túi đã lấp được: {fill_percentage:.2f}% ({total_selected_weight}/{max_weight})")
            self.result_text.append(f"Giá trị tối đa túi có thể mang: ${total_value}")
            self.result_text.append("\nDanh sách món đồ được chọn:")
            for item in selected_items:
                self.result_text.append(f"- {item[0]}: Giá trị ${item[1]}, Trọng lượng {item[2]}")

            names = [item[0] for item in selected_items]
            weights = [item[2] for item in selected_items]
            values = [item[1] for item in selected_items]
            
            self.plot_bar_chart(names, weights, values)
            self.plot_weight_pie_chart(total_selected_weight, max_weight)

        except Exception as e:
            self.result_text.append(f"Lỗi: {e}")

    def knapsack_backtracking(self, items, max_weight):
        n = len(items)
        max_value = [0]
        best_combination = [[]]

        def backtrack(index, current_weight, current_value, selected_items):
            if index == n:
                if current_value > max_value[0]:
                    max_value[0] = current_value
                    best_combination[0] = selected_items[:]
                return

            backtrack(index + 1, current_weight, current_value, selected_items)

            name, value, weight, _ = items[index]
            if current_weight + weight <= max_weight:
                selected_items.append(items[index])
                backtrack(index + 1, current_weight + weight, current_value + value, selected_items)
                selected_items.pop()

        backtrack(0, 0, 0, [])
        return max_value[0], best_combination[0]

    def plot_bar_chart(self, names, weights, values):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        bars = ax.bar(names, weights, color='skyblue')
        ax.set_title("Trọng lượng các sản phẩm được chọn")
        ax.set_ylabel("Trọng lượng")
        ax.set_xticklabels(names, rotation=45, ha='right')

        # Thêm giá trị của từng sản phẩm trên đỉnh cột
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'${value}', ha='center', va='bottom')

        self.figure.tight_layout()
        self.canvas.draw()

    def plot_weight_pie_chart(self, total_selected_weight, max_weight):
        remaining_weight = max_weight - total_selected_weight
        
        self.figure_pie.clear()
        ax = self.figure_pie.add_subplot(111)
        
        # Vẽ biểu đồ tròn
        weights = [total_selected_weight, remaining_weight]
        labels = ['Đã lấp đầy', 'Còn trống']
        colors = ['green', 'lightgray']
        
        ax.pie(weights, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title("Phần trọng lượng túi")
        
        self.canvas_pie.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KnapsackApp()
    window.show()
    sys.exit(app.exec_())
import itertools

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QListWidgetItem, QVBoxLayout, QPushButton, QListWidget, QWidget, \
    QLabel, QHBoxLayout, QLineEdit

MAX_ELEMENTS_C = 9


# true if it is a float
def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


# get number if float else 0.0
def get_float_if_float(string):
    try:
        return float(string)
    except ValueError:
        return 0.0


# a layout to hold Total bet and Total earnings labels
class TotalBetTotalEarnings(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.total_bet_label = QLabel()
        self.total_earnings_label = QLabel()
        self.addWidget(self.total_bet_label)
        self.addWidget(self.total_earnings_label)
        self.setAlignment(Qt.AlignmentFlag.AlignTop)

    def set_data(self, total_bet, total_earnings):
        self.total_bet_label.setText(total_bet)
        self.total_earnings_label.setText(total_earnings)


# a layout to hold combinations, bet per combination, const of combination and earnings of combination
class CombinationInformation(QHBoxLayout):
    def __init__(self, line_title, parent):
        super().__init__()
        self.label = QLabel(line_title)  # combination ID
        self.line_edit = QLineEdit()  # bet for that combination
        self.result = QLabel('-')  # cost and earnings of combination

        self.addWidget(self.label, 10)
        self.addWidget(self.line_edit, 10)
        self.addWidget(self.result, 80)

        self.line_edit.textChanged.connect(self.on_line_edit_change)

        self.the_parent = parent

    def on_line_edit_change(self):
        if hasattr(self.the_parent, 'on_calculate_click'):
            self.the_parent.on_calculate_click()

    def get_bet_str(self):
        return self.line_edit.text()

    def set_result_text(self, value):
        self.result.setText(str(value))

    def get_bet_float(self):
        return get_float_if_float(self.get_bet_str())

    def destroy(self):
        self.removeWidget(self.label)
        self.removeWidget(self.line_edit)
        self.removeWidget(self.result)
        self.label = None
        self.line_edit = None
        self.result = None


# a BetItem holds the check state and the rate
# check state Checked means that the current match is won
class BetItem(QListWidgetItem):
    def __init__(self, text):
        super().__init__()
        self.setFlags(self.flags() or Qt.ItemFlag.ItemIsEditable)
        self.setCheckState(Qt.CheckState.Checked)
        self.setText(text)


class BetCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('BetCalculator')
        self.betting_list = QListWidget()
        self.betting_list.doubleClicked.connect(self.on_double_click)
        self.betting_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.betting_list.itemDoubleClicked.connect(self.on_double_click)
        self.betting_list.itemChanged.connect(self.on_bet_change)
        self.betting_list.setSelectionMode(self.betting_list.selectionMode().ExtendedSelection)
        self.betting_list.setMinimumHeight(200)

        self.calculate_button = QPushButton('Calculate')
        self.calculate_button.clicked.connect(self.on_calculate_click)

        self.add_button = QPushButton('Add')
        self.add_button.clicked.connect(self.on_add_click)
        self.add_button.setEnabled(False)

        self.rate_input = QLineEdit()
        self.rate_input.textChanged.connect(self.on_rate_input_change)
        self.rate_input.returnPressed.connect(self.on_rate_input_return)

        self.delete_button = QPushButton('Delete')
        self.delete_button.clicked.connect(self.on_delete_click)
        self.delete_button.setEnabled(False)

        self.combinations_info = []
        self.combinations_layout = QVBoxLayout()
        self.combinations_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.total_information = TotalBetTotalEarnings()

        self.menu_layout = QHBoxLayout()
        self.menu_layout.addWidget(self.add_button)
        self.menu_layout.addWidget(self.rate_input)
        self.menu_layout.addWidget(self.delete_button)

        self.win_layout = QVBoxLayout()
        self.win_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.win_layout.setDirection(QVBoxLayout.Direction.TopToBottom)
        self.win_layout.addLayout(self.menu_layout)
        self.win_layout.addWidget(self.betting_list)
        self.win_layout.addWidget(self.calculate_button)
        self.win_layout.addLayout(self.combinations_layout)
        self.win_layout.addLayout(self.total_information)
        self.setLayout(self.win_layout)

    def on_rate_input_return(self):
        if is_float(self.rate_input.text()):
            self.on_add_click()

    def on_delete_click(self):
        items_to_delete = self.betting_list.selectedItems()
        for item in items_to_delete:
            self.betting_list.takeItem(self.betting_list.row(item))
            self.combinations_info[-1].destroy()
            self.combinations_layout.removeItem(self.combinations_info[-1])
            del self.combinations_info[-1]
        self.rate_input.setEnabled(self.betting_list.count() < MAX_ELEMENTS_C)
        self.add_button.setEnabled(self.betting_list.count() < MAX_ELEMENTS_C)
        self.on_calculate_click()

    def on_add_click(self):
        self.rate_input.setEnabled(self.betting_list.count() < MAX_ELEMENTS_C)
        self.add_button.setEnabled(self.betting_list.count() < MAX_ELEMENTS_C)
        if self.add_button.isEnabled():
            self.betting_list.addItem(BetItem(self.rate_input.text()))
            self.rate_input.clear()
            self.combinations_info.append(CombinationInformation(f'Bet #{self.betting_list.count()}', self))
            self.combinations_layout.addLayout(self.combinations_info[-1])
        self.on_calculate_click()

    def on_bet_change(self):
        self.on_calculate_click()

    def on_rate_input_change(self):
        self.rate_input.setEnabled(self.betting_list.count() < MAX_ELEMENTS_C)
        self.add_button.setEnabled(self.betting_list.count() < MAX_ELEMENTS_C)
        if self.betting_list.count() < MAX_ELEMENTS_C:
            self.add_button.setEnabled(is_float(self.rate_input.text()))
        else:
            self.rate_input.clear()

    def on_calculate_click(self):
        indexes = range(self.betting_list.count())
        total_bet = 0.0
        total_earnings = 0.0
        for i in indexes:
            combinations = list(itertools.combinations(indexes, i + 1))
            number_of_combinations = len(combinations)
            bet = self.combinations_info[i].get_bet_float()
            combination_bet = bet * number_of_combinations
            combination_earnings = 0.0
            for combination in combinations:
                comb_coefficient = 1.0
                for match in combination:
                    if self.betting_list.item(match).checkState() == Qt.CheckState.Checked:
                        comb_coefficient *= get_float_if_float(self.betting_list.item(match).text())
                    else:
                        comb_coefficient = 0.0
                combination_earnings += bet * comb_coefficient
            total_earnings += combination_earnings
            total_bet += combination_bet
            self.combinations_info[i].set_result_text(f' x {number_of_combinations} = {combination_bet:.2f}'
                                                      f' | Earnings = {combination_earnings:.2f}')
        self.total_information.set_data(f'Total bet: {total_bet:.2f}', f'Total earnings: {total_earnings:.2f}')

    def on_selection_changed(self):
        self.delete_button.setEnabled(len(self.betting_list.selectedItems()) > 0)

    def on_double_click(self, item):
        if isinstance(item, BetItem):
            self.betting_list.editItem(item)


app = QApplication([])
window = BetCalculator()
window.show()
app.exec()

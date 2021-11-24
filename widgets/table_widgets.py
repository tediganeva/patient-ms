# UI library imports
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ehealthApp import *


def table_data_settings(table_widget):
    """ Adjust settings for a UI widget.

    Args:
        table_widget (class): UI widget component.
    """

    table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    table_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
    table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    table_widget.verticalHeader().setVisible(False)


def table_display_data(table_widget, query_result):
    """ Displays a specified resultset into a widget table.

    Args:
        table_widget (class): UI widget component.
        query_result (list): resultset list.
    """

    table_widget.setRowCount(0)

    for row_number, row_data in enumerate(query_result):
        table_widget.insertRow(row_number)

        for column_number, data in enumerate(row_data):
            table_widget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))


def table_row_select(table_widget, labels_list, **kwargs):
    """ Selects the table option that the user has clicked on.

    Args:
        table_widget (class): UI widget component.
        labels_list (list): resultset list.
    """

    cell_list = table_widget.selectionModel().selectedIndexes()
    cell = cell_list[0]
    row = cell.row()
    print('ROW:', row + 1)
    # table_widget.selectRow(row)
    curr_row = table_widget.currentRow()
    list_index = 0

    for column, value in kwargs.items():
        value_selection = table_widget.item(curr_row, value).text()
        print(column, table_widget.item(curr_row, value).text())
        labels_list[list_index].setText(str(column) + ': ' + str(value_selection))
        list_index += 1


def table_goes_blank(table_widget):
    """ Removes rows in a table so it presents no data. """

    table_widget.setRowCount(0)
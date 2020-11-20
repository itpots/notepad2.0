import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QFontDialog
from PyQt5.QtCore import Qt
import sqlite3
import datetime as dt
import os


class Notepad2(QMainWindow):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.idofnote = 0
        uic.loadUi('notepad.ui', self)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: white;")
        self.label_2.hide()
        self.lineEdit_2.hide()
        self.pushButton_4.hide()
        self.checkBox.stateChanged.connect(self.check)
        self.pushButton.clicked.connect(self.save)
        self.pushButton_2.clicked.connect(self.open)
        self.pushButton_4.clicked.connect(self.search)
        self.pushButton_5.clicked.connect(self.themes)
        self.pushButton_6.clicked.connect(self.font_change)
        self.pushButton_7.clicked.connect(self.delete_file)
        self.create()

    def create(self):
        self.con = sqlite3.connect("notes.db")
        create = self.con.cursor()
        create.execute("""CREATE TABLE IF NOT EXISTS Notes(
                       title TEXT NOT NULL,
                       id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                       date TEXT NOT NULL,
                       time TEXT NOT NULL);
                       """)
        self.con.commit()

    def save(self):
        text = self.textEdit.toPlainText()
        text = text.split("\n")
        self.title = self.lineEdit.text()
        if len(self.title) != 0:
            self.add_in_bd(self.title)
            file = open(f"{self.title}.txt", "w", encoding="utf-8")
            for line in text:
                print(line, file=file)
            QMessageBox.about(self, "Сохранение", f"Файл сохранён. Ему присвоен id {self.currentid}")
            file.close()

        else:
            self.title = "Безымянный"
            self.add_in_bd(self.title)
            file = open(f"{self.title}.txt", 'w', encoding="utf-8")
            for line in text:
                print(line, file=file)
            QMessageBox.about(self, "Сохранение", f"Файл сохранён. Ему присвоен id {self.currentid}")
            file.close()

    def add_in_bd(self, title, saving=False):
        self.title = title
        self.added_in_bd = False
        date = str(dt.datetime.now()).split()
        dat = date[0].split(":")
        dat = dat[0].split("-")
        dat = f"{dat[2]}-{dat[1]}-{dat[0]}"
        time = date[1]
        time = time.split(":")
        time = f"{time[0]}:{time[1]}"
        curs = self.con.cursor()
        curs2 = self.con.cursor()
        cursor = self.con.cursor()
        all_id = curs.execute("""SELECT id from Notes""").fetchall()
        titles = curs2.execute("""SELECT title from Notes""").fetchall()
        titles = [str(i[0]) for i in titles]
        all_id = [int(i[0]) for i in all_id]
        if all_id:
            self.idofnote = max(all_id)

        if all_id and self.title not in titles:
            self.idofnote += + 1
            self.currentid = self.idofnote
            cursor.execute("""INSERT INTO notes(title, date, time) 
                        VALUES (?, ?, ?)""", (self.title, dat, time))
            if saving:
                self.added_in_bd = True
            self.con.commit()

        elif all_id and self.title in titles and saving is False:
            rewrite = QMessageBox.question(self, "Перезапись", "Файл с таким названием найден. Перезаписать?",
                                           QMessageBox.Yes, QMessageBox.No)
            if rewrite == QMessageBox.Yes:
                new_id = self.idofnote + 1
                self.currentid = new_id
                cursor.execute("""UPDATE Notes
                            SET id = ?
                            WHERE title = ?""", (new_id, self.title))
                self.con.commit()

            elif rewrite == QMessageBox.No:
                curs4 = self.con.cursor()
                alltitles = curs4.execute("""SELECT title from Notes
                                       WHERE title like ?""", ('{}(_)'.format(self.title),)).fetchall()
                lentitles = len(alltitles)
                if lentitles == 0:
                    lentitles += 1
                self.idofnote += 1
                self.currentid = self.idofnote
                self.title = f"{self.title}({lentitles})"
                cursor.execute("""INSERT INTO notes(title, date, time) 
                                                    VALUES (?, ?, ?)""", (self.title, dat, time))
                self.con.commit()

        elif len(all_id) == 0:
            cursor.execute("""INSERT INTO notes(title, date, time) 
                                    VALUES (?, ?, ?)""", (self.title, dat, time))
            self.currentid = cursor.execute("""SELECT id from notes WHERE title = ?""", (self.title,)).fetchone()[0]
            if saving:
                self.added_in_bd = True
            self.con.commit()

    def open(self):
        self.textEdit.clear()
        filename = QFileDialog.getOpenFileName(
            self, 'Выбрать файл', '',
            'Текстовый файл (*.txt)')[0]
        if filename:
            file = open(filename, encoding="utf-8")
            lines = file.readlines()
            lines = [line.rstrip() for line in lines]
            self.lineEdit.setText("")
            path = filename.split("/")
            name = path[-1].split(".txt")
            name = name[0]
            self.lineEdit.setText(name)
            for line in lines:
                self.textEdit.append(line)
            file.close()
            self.add_in_bd(name, True)
            if self.added_in_bd:
                QMessageBox.about(self, "Загрузка", f"Файл загружен. Его id {self.currentid}")

    def check(self, state):
        if state == Qt.Checked:
            self.label_2.show()
            self.lineEdit_2.show()
            self.pushButton_4.show()

        else:
            self.label_2.hide()
            self.lineEdit_2.hide()
            self.pushButton_4.hide()
            self.lineEdit_2.setText("")

    def font_change(self):
        font, ok_pressed = QFontDialog.getFont()
        if ok_pressed:
            self.textEdit.setFont(font)
            self.lineEdit.setFont(font)
            self.lineEdit_2.setFont(font)

    def search(self):
        search_text = self.lineEdit_2.text()
        con = sqlite3.connect("notes.db")
        curs5 = con.cursor()
        if search_text.isdigit():
            result_of_search = curs5.execute("""SELECT title from Notes
                                          WHERE id = ?""", (search_text,)).fetchall()
            if result_of_search:
                result_of_search = result_of_search[0][0]
                request = QMessageBox.question(self, "Поиск", f"Файл с id {search_text} найден. Загрузить?",
                                               QMessageBox.Yes, QMessageBox.No)
                if request == QMessageBox.Yes:
                    self.load(result_of_search)
            else:
                QMessageBox.about(self, "Поиск",
                                  "Файл не найден. Возможно его нет в базе данных или введён неверный id.")
        elif len(search_text) != 0:
            result_of_search = curs5.execute("""SELECT title from Notes
                                          WHERE title = ?""", (search_text,)).fetchall()
            if result_of_search:
                request = QMessageBox.question(self, "Поиск",
                                               f'Файл с названием "{result_of_search[0][0]}" найден. Загрузить?',
                                               QMessageBox.Yes, QMessageBox.No)
                if request == QMessageBox.Yes:
                    self.load(search_text)
            else:
                QMessageBox.about(self, "Поиск",
                                  "Файл не найден. Возможно его нет в базе данных или введено неверное название.")
        elif len(search_text) == 0:
            QMessageBox.about(self, "Поиск", "Введён неверный запрос.")

    def load(self, title):
        self.textEdit.clear()
        file = open(f"{title}.txt", encoding="utf-8")
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        self.lineEdit.setText("")
        self.lineEdit.setText(title)
        for line in lines:
            self.textEdit.append(line)

    def themes(self):
        if self.count == 0:
            self.pushButton_5.setText(f"Светлая тема")
            self.setStyleSheet("background-color: black; color: white;")
            self.pushButton.setStyleSheet("background-color: grey")
            self.pushButton_2.setStyleSheet("background-color: grey")
            self.pushButton_4.setStyleSheet("background-color: grey")
            self.pushButton_5.setStyleSheet("background-color: grey")
            self.pushButton_6.setStyleSheet("background-color: grey")
            self.pushButton_7.setStyleSheet("background-color: grey")
            self.textEdit.setStyleSheet("background-color: rgb(190, 190, 190, 255)")
            self.lineEdit.setStyleSheet("background-color: rgb(190, 190, 190, 255)")
            self.lineEdit_2.setStyleSheet("background-color: rgb(190, 190, 190, 255)")
            self.count = 1

        else:
            self.pushButton_5.setText(f"Тёмная тема")
            self.setStyleSheet("background-color: white;")
            self.pushButton.setStyleSheet("background-color: white;")
            self.pushButton_2.setStyleSheet("background-color: white;")
            self.pushButton_4.setStyleSheet("background-color: white;")
            self.pushButton_5.setStyleSheet("background-color: white;")
            self.pushButton_6.setStyleSheet("background-color: white")
            self.pushButton_7.setStyleSheet("background-color: white")
            self.textEdit.setStyleSheet("background-color: white;")
            self.lineEdit.setStyleSheet("background-color: white")
            self.lineEdit_2.setStyleSheet("background-color: white")
            self.count = 0

    def delete_file(self):
        filename = QFileDialog.getOpenFileName(
            self, 'Выбрать файл для удаления', '',
            'Текстовый файл (*.txt)')[0]
        if filename:
            path = filename.split("/")
            name = path[-1].split(".txt")
            name = name[0]
            self.check_in_db(name)
            if self.check_in_db:
                delete_yes = QMessageBox.question(self, "Удаление",
                                               f'Удалить файл {name} ?',
                                               QMessageBox.Yes, QMessageBox.No)
                if delete_yes:
                    cursor = self.con.cursor()
                    cursor.execute("DELETE FROM notes WHERE title = ?", (name,))
                    self.con.commit()
                    os.remove(filename)
                    if self.lineEdit.text() == name:
                        self.lineEdit.setText("")
                        self.textEdit.clear()
                    QMessageBox.about(self, "Удаление", "Файл удалён.")
            else:
                delete_yes = QMessageBox.question(self, "Удаление",
                                                  f'Удалить файл {name} ?',
                                                  QMessageBox.Yes, QMessageBox.No)
                if delete_yes:
                    os.remove(filename)
                    if self.lineEdit.text() == name:
                        self.lineEdit.setText("")
                        self.textEdit.clear()
                    QMessageBox.about(self, "Удаление", "Файл удалён.")
        else:
            QMessageBox.about(self, "Удаление", "Файл не выбран.")

    def check_in_db(self, title):
        self.file_in_db = False
        cursor = self.con.cursor()
        titles = cursor.execute("""SELECT title from notes""")
        if title in titles:
            self.file_in_db = True


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Notepad2()
    ex.show()
    sys.exit(app.exec_())
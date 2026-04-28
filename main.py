import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFontDatabase, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


APP_ROOT = Path(__file__).resolve().parent
DB_PATH = APP_ROOT / "data" / "tera.db"
STYLE_PATH = APP_ROOT / "assets" / "tera.qss"
FONT_PATH = APP_ROOT / "assets" / "fonts" / "Angels.ttf"


class Database:
    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'Pendente',
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area TEXT NOT NULL,
                topic TEXT NOT NULL,
                note TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS command_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                output TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def add_task(self, area: str, title: str, description: str, status: str):
        self.conn.execute(
            "INSERT INTO tasks(area,title,description,status,created_at) VALUES(?,?,?,?,?)",
            (area, title, description, status, datetime.now().isoformat(timespec="seconds")),
        )
        self.conn.commit()

    def list_tasks(self):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, area, title, status, created_at FROM tasks ORDER BY id DESC"
        )
        return cur.fetchall()

    def add_learning(self, area: str, topic: str, note: str):
        self.conn.execute(
            "INSERT INTO learnings(area,topic,note,created_at) VALUES(?,?,?,?)",
            (area, topic, note, datetime.now().isoformat(timespec="seconds")),
        )
        self.conn.commit()

    def list_learnings(self):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, area, topic, created_at FROM learnings ORDER BY id DESC"
        )
        return cur.fetchall()

    def add_command_log(self, command: str, output: str):
        self.conn.execute(
            "INSERT INTO command_logs(command,output,created_at) VALUES(?,?,?)",
            (command, output, datetime.now().isoformat(timespec="seconds")),
        )
        self.conn.commit()

    def export_sqlite_file(self, destination: Path):
        destination.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(destination) as out_conn:
            self.conn.backup(out_conn)


class TeraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database(DB_PATH)
        self.setWindowTitle("TERA AI - Programação, Hardware, Mobile & iOS")
        self.setMinimumSize(1280, 760)
        self._build_ui()
        self.refresh_tables()

    def _build_ui(self):
        container = QWidget()
        root_layout = QVBoxLayout(container)

        header = QLabel("TERA")
        header.setObjectName("titleHero")
        subtitle = QLabel(
            "Assistente técnico para programação, hardware, mobile, iOS e informática"
        )
        subtitle.setObjectName("subtitleHero")

        root_layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignHCenter)
        root_layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignHCenter)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([520, 760])
        root_layout.addWidget(splitter)

        self.setCentralWidget(container)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Tera inicializada.")
        self._build_menu()

    def _build_menu(self):
        menu = self.menuBar().addMenu("Arquivo")

        export_action = QAction("Exportar Banco (SQLite)", self)
        export_action.triggered.connect(self.export_database)
        menu.addAction(export_action)

        github_action = QAction("Sincronizar com GitHub (git add/commit/push)", self)
        github_action.triggered.connect(self.sync_to_github)
        menu.addAction(github_action)

        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)

    def _build_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)

        tabs = QTabWidget()
        tabs.addTab(self._task_tab(), "Tarefas")
        tabs.addTab(self._learning_tab(), "Aprendizados")
        tabs.addTab(self._command_tab(), "Comandos")
        layout.addWidget(tabs)

        return panel

    def _build_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)

        self.tasks_table = QTableWidget(0, 5)
        self.tasks_table.setHorizontalHeaderLabels(
            ["ID", "Área", "Título", "Status", "Data"]
        )
        self.tasks_table.horizontalHeader().setStretchLastSection(True)

        self.learning_table = QTableWidget(0, 4)
        self.learning_table.setHorizontalHeaderLabels(
            ["ID", "Área", "Tópico", "Data"]
        )
        self.learning_table.horizontalHeader().setStretchLastSection(True)

        right_tabs = QTabWidget()
        right_tabs.addTab(self.tasks_table, "Painel de Tarefas")
        right_tabs.addTab(self.learning_table, "Painel de Aprendizado")
        layout.addWidget(right_tabs)
        return panel

    def _task_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.task_area = QComboBox()
        self.task_area.addItems(
            ["Programação", "Hardware", "Mobile", "iOS", "Informática"]
        )
        self.task_title = QLineEdit()
        self.task_desc = QTextEdit()
        self.task_status = QComboBox()
        self.task_status.addItems(["Pendente", "Em Progresso", "Concluída"])

        btn_row = QHBoxLayout()
        btn_save = QPushButton("Salvar Tarefa")
        btn_save.clicked.connect(self.save_task)
        btn_reload = QPushButton("Atualizar Tabela")
        btn_reload.clicked.connect(self.refresh_tables)
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_reload)

        layout.addRow("Área:", self.task_area)
        layout.addRow("Título:", self.task_title)
        layout.addRow("Descrição:", self.task_desc)
        layout.addRow("Status:", self.task_status)
        layout.addRow(btn_row)
        return tab

    def _learning_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.learn_area = QComboBox()
        self.learn_area.addItems(
            ["Programação", "Hardware", "Mobile", "iOS", "Informática"]
        )
        self.learn_topic = QLineEdit()
        self.learn_note = QTextEdit()

        btn_save = QPushButton("Salvar Aprendizado")
        btn_save.clicked.connect(self.save_learning)

        layout.addRow("Área:", self.learn_area)
        layout.addRow("Tópico:", self.learn_topic)
        layout.addRow("Anotação/Treinamento:", self.learn_note)
        layout.addRow(btn_save)
        return tab

    def _command_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText(
            "Ex.: python --version | adb devices | systeminfo"
        )
        run_btn = QPushButton("Executar Comando")
        run_btn.clicked.connect(self.run_command)
        self.command_output = QPlainTextEdit()
        self.command_output.setReadOnly(True)

        layout.addWidget(QLabel("Ferramentas rápidas para dev/hardware/mobile:"))
        layout.addWidget(self.command_input)
        layout.addWidget(run_btn)
        layout.addWidget(self.command_output)
        return tab

    def save_task(self):
        title = self.task_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Validação", "Informe um título da tarefa.")
            return
        self.db.add_task(
            self.task_area.currentText(),
            title,
            self.task_desc.toPlainText().strip(),
            self.task_status.currentText(),
        )
        self.task_title.clear()
        self.task_desc.clear()
        self.refresh_tables()
        self.statusBar().showMessage("Tarefa salva com sucesso.")

    def save_learning(self):
        topic = self.learn_topic.text().strip()
        note = self.learn_note.toPlainText().strip()
        if not topic or not note:
            QMessageBox.warning(self, "Validação", "Preencha tópico e anotação.")
            return
        self.db.add_learning(self.learn_area.currentText(), topic, note)
        self.learn_topic.clear()
        self.learn_note.clear()
        self.refresh_tables()
        self.statusBar().showMessage("Aprendizado salvo com sucesso.")

    def run_command(self):
        cmd = self.command_input.text().strip()
        if not cmd:
            return
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True,
                timeout=25,
            )
            output = (result.stdout + "\n" + result.stderr).strip()
        except Exception as exc:
            output = f"Erro ao executar: {exc}"

        self.db.add_command_log(cmd, output)
        self.command_output.setPlainText(output)
        self.command_output.moveCursor(QTextCursor.MoveOperation.End)
        self.statusBar().showMessage("Comando executado e salvo no banco.")

    def refresh_tables(self):
        tasks = self.db.list_tasks()
        self.tasks_table.setRowCount(len(tasks))
        for row, item in enumerate(tasks):
            for col, value in enumerate(item):
                self.tasks_table.setItem(row, col, QTableWidgetItem(str(value)))

        learns = self.db.list_learnings()
        self.learning_table.setRowCount(len(learns))
        for row, item in enumerate(learns):
            for col, value in enumerate(item):
                self.learning_table.setItem(row, col, QTableWidgetItem(str(value)))

    def export_database(self):
        target, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Banco SQLite",
            str(APP_ROOT / "exports" / "tera_export.db"),
            "SQLite (*.db)",
        )
        if not target:
            return
        self.db.export_sqlite_file(Path(target))
        self.statusBar().showMessage(f"Banco exportado para: {target}")

    def sync_to_github(self):
        try:
            subprocess.run("git add .", shell=True, check=True, cwd=APP_ROOT)
            msg = f'TERA auto-sync {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            subprocess.run(
                f'git commit -m "{msg}"', shell=True, check=False, cwd=APP_ROOT
            )
            push = subprocess.run(
                "git push",
                shell=True,
                capture_output=True,
                text=True,
                cwd=APP_ROOT,
                check=False,
            )
            if push.returncode == 0:
                QMessageBox.information(self, "GitHub", "Sincronização concluída.")
            else:
                QMessageBox.warning(
                    self, "GitHub", f"Push não concluído:\n{push.stdout}\n{push.stderr}"
                )
        except Exception as exc:
            QMessageBox.critical(self, "GitHub", f"Erro na sincronização: {exc}")


def load_style(app: QApplication):
    if STYLE_PATH.exists():
        app.setStyleSheet(STYLE_PATH.read_text(encoding="utf-8"))


def load_custom_font():
    if FONT_PATH.exists():
        QFontDatabase.addApplicationFont(str(FONT_PATH))


def main():
    os.makedirs(APP_ROOT / "data", exist_ok=True)
    os.makedirs(APP_ROOT / "exports", exist_ok=True)

    app = QApplication(sys.argv)
    load_custom_font()
    load_style(app)

    win = TeraWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

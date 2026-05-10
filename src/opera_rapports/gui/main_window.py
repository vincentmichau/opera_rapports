from __future__ import annotations

import tempfile
from datetime import date
from pathlib import Path

from PySide6.QtCore import QDate, QObject, QThread, Signal
from PySide6.QtGui import QAction, QDesktopServices, QIcon
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QStatusBar,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from opera_rapports.core.models import Gender, Guest, Language
from opera_rapports.core.settings import AppSettings
from opera_rapports.core.xml_importer import import_opera_xml
from opera_rapports.mvc.controllers import AppController
from opera_rapports.mvc.models import ArrivalTableViewModel

COLUMNS = [
    ("room_number", "Chambre"),
    ("last_name", "Nom"),
    ("first_name", "Prénom"),
    ("gender", "Civilité"),
    ("language", "Langue"),
    ("arrival_date", "Arrivée"),
    ("departure_date", "Départ"),
    ("room_type", "Type"),
    ("people_count", "Pers."),
]


class ImportWorker(QObject):
    progress = Signal(int, int)
    finished = Signal(list)
    failed = Signal(str)

    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path

    def run(self) -> None:
        try:
            guests = import_opera_xml(self.path, self.progress.emit)
        except Exception as exc:  # noqa: BLE001 - displayed to non-technical users
            self.failed.emit(str(exc))
        else:
            self.finished.emit(guests)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.controller = AppController()
        self.view_model = ArrivalTableViewModel()
        self.app_settings = self.controller.app_settings
        self.guests: list[Guest] = []
        self.setWindowTitle("Opera Rapports — Cartons de clés & Welcome letters")
        self.resize(1280, 760)
        self._build_actions()
        self._build_toolbar()
        self._build_content()
        self._build_statusbar()
        self.apply_theme(self.controller.theme())
        self.reload_table()

    def _build_actions(self) -> None:
        self.import_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton), "Importer XML", self)
        self.import_action.triggered.connect(self.import_xml)
        self.quit_action = QAction("Quitter", self)
        self.quit_action.triggered.connect(self.close)
        self.light_action = QAction("Thème clair", self)
        self.light_action.triggered.connect(lambda: self.apply_theme("light"))
        self.dark_action = QAction("Thème sombre", self)
        self.dark_action.triggered.connect(lambda: self.apply_theme("dark"))
        self.settings_action = QAction("Paramètres hôtel", self)
        self.settings_action.triggered.connect(self.edit_app_settings)
        self.export_xlsx_action = QAction("Exporter Excel (.xlsx)", self)
        self.export_xlsx_action.triggered.connect(lambda: self.export_arrivals("xlsx"))
        self.export_docx_action = QAction("Exporter Word (.docx)", self)
        self.export_docx_action.triggered.connect(lambda: self.export_arrivals("docx"))
        self.purge_action = QAction("Purger les données importées", self)
        self.purge_action.triggered.connect(self.purge_import)
        menu = self.menuBar().addMenu("Application")
        menu.addAction(self.light_action)
        menu.addAction(self.dark_action)
        menu.addSeparator()
        menu.addAction(self.settings_action)
        menu.addSeparator()
        menu.addAction(self.export_xlsx_action)
        menu.addAction(self.export_docx_action)
        menu.addSeparator()
        menu.addAction(self.purge_action)
        menu.addSeparator()
        menu.addAction(self.quit_action)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Ruban", self)
        toolbar.setMovable(False)
        toolbar.setIconSize(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView).actualSize(toolbar.iconSize()))
        self.addToolBar(toolbar)
        toolbar.addAction(self.import_action)
        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Date d'arrivée : "))
        self.date_filter = QDateEdit(QDate.currentDate().addDays(1))
        self.date_filter.setCalendarPopup(True)
        self.date_filter.dateChanged.connect(self.reload_table)
        toolbar.addWidget(self.date_filter)
        today_button = QPushButton("Aujourd'hui")
        today_button.clicked.connect(lambda: self.date_filter.setDate(QDate.currentDate()))
        tomorrow_button = QPushButton("Demain")
        tomorrow_button.clicked.connect(lambda: self.date_filter.setDate(QDate.currentDate().addDays(1)))
        toolbar.addWidget(today_button)
        toolbar.addWidget(tomorrow_button)
        columns_button = QPushButton("Colonnes")
        columns_button.clicked.connect(self.choose_columns)
        toolbar.addWidget(columns_button)
        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Modèle : "))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Carton de clé A6", "Welcome letter DL", "Liste des arrivées"])
        toolbar.addWidget(self.model_combo)
        print_button = QPushButton("Imprimer la sélection")
        print_button.clicked.connect(self.print_selection)
        print_all_cards = QPushButton("Tous les cartons")
        print_all_cards.clicked.connect(lambda: self.preview_or_print("key", self.guests, print_now=True))
        print_all_letters = QPushButton("Toutes les lettres")
        print_all_letters.clicked.connect(lambda: self.preview_or_print("letter", self.guests, print_now=True))
        preview_button = QPushButton("Aperçu")
        preview_button.clicked.connect(self.preview_selection)
        toolbar.addWidget(print_button)
        toolbar.addWidget(print_all_cards)
        toolbar.addWidget(print_all_letters)
        toolbar.addWidget(preview_button)
        spacer = QWidget()
        spacer.setMinimumWidth(20)
        toolbar.addWidget(spacer)
        toolbar.addWidget(QLabel(f"Date du jour : {date.today():%d/%m/%Y}"))

    def _build_content(self) -> None:
        central = QWidget(self)
        layout = QVBoxLayout(central)
        kpi_layout = QHBoxLayout()
        self.arrivals_kpi = QLabel("Arrivées : 0")
        self.people_kpi = QLabel("Personnes : 0")
        self.room_kpi = QLabel("Types chambres : —")
        for widget in (self.arrivals_kpi, self.people_kpi, self.room_kpi):
            widget.setObjectName("kpi")
            kpi_layout.addWidget(widget)
        layout.addLayout(kpi_layout)
        self.table = QTableWidget(0, len(COLUMNS), self)
        self.table.setHorizontalHeaderLabels([label for _, label in COLUMNS])
        self.table.setSortingEnabled(True)
        self.table.cellChanged.connect(self.persist_cell_change)
        layout.addWidget(self.table)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        self.setCentralWidget(central)

    def _build_statusbar(self) -> None:
        self.status = QStatusBar(self)
        self.rows_label = QLabel("0 ligne importée")
        self.status.addPermanentWidget(self.rows_label)
        self.setStatusBar(self.status)

    def selected_arrival_date(self) -> date:
        qdate = self.date_filter.date()
        return date(qdate.year(), qdate.month(), qdate.day())

    def reload_table(self) -> None:
        self.view_model = self.controller.load_arrivals(self.selected_arrival_date())
        self.guests = self.view_model.guests
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.guests))
        for row, guest in enumerate(self.guests):
            for col, (attr, _) in enumerate(COLUMNS):
                if attr == "gender":
                    combo = QComboBox()
                    combo.addItems([gender.value for gender in Gender])
                    combo.setCurrentText(guest.gender.value)
                    combo.currentTextChanged.connect(lambda _text, r=row: self.persist_combo_change(r))
                    self.table.setCellWidget(row, col, combo)
                elif attr == "language":
                    combo = QComboBox()
                    combo.addItems([language.value for language in Language])
                    combo.setCurrentText(guest.language.value)
                    combo.currentTextChanged.connect(lambda _text, r=row: self.persist_combo_change(r))
                    self.table.setCellWidget(row, col, combo)
                else:
                    value = getattr(guest, attr)
                    self.table.setItem(row, col, QTableWidgetItem(str(value or "")))
        self.table.blockSignals(False)
        self.apply_column_visibility()
        self.rows_label.setText(f"{len(self.guests)} ligne(s) importée(s)")
        self.update_kpis()

    def edit_app_settings(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Paramètres hôtel")
        form = QFormLayout(dialog)
        hotel_name = QLineEdit(self.app_settings.hotel_name)
        manager_name = QLineEdit(self.app_settings.manager_name)
        manager_role = QLineEdit(self.app_settings.manager_role_fr)
        default_printer = QLineEdit(self.app_settings.default_printer)
        logo_path = QLineEdit(self.app_settings.logo_path)
        retention_days = QSpinBox()
        retention_days.setRange(1, 365)
        retention_days.setValue(self.app_settings.retention_days)
        form.addRow("Nom de l'hôtel", hotel_name)
        form.addRow("Nom directrice/directeur", manager_name)
        form.addRow("Fonction FR", manager_role)
        form.addRow("Imprimante favorite", default_printer)
        form.addRow("Logo (chemin fichier)", logo_path)
        form.addRow("Conservation locale (jours)", retention_days)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.app_settings = AppSettings(
                hotel_name=hotel_name.text().strip() or "Votre Hôtel",
                manager_name=manager_name.text().strip() or "La Directrice",
                manager_role_fr=manager_role.text().strip() or "Directrice de l'hôtel",
                default_printer=default_printer.text().strip(),
                retention_days=retention_days.value(),
                logo_path=logo_path.text().strip(),
            )
            purged = self.controller.save_app_settings(self.app_settings)
            if purged:
                self.reload_table()
            QMessageBox.information(self, "Paramètres", "Paramètres enregistrés.")

    def apply_column_visibility(self) -> None:
        visible = self.controller.visible_columns()
        if not isinstance(visible, list):
            visible = [key for key, _label in COLUMNS]
        for index, (key, _label) in enumerate(COLUMNS):
            self.table.setColumnHidden(index, key not in visible)

    def choose_columns(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Colonnes affichées")
        layout = QGridLayout(dialog)
        visible = set(self.controller.visible_columns())
        checks: list[tuple[str, QCheckBox]] = []
        for row, (key, label) in enumerate(COLUMNS):
            check = QCheckBox(label)
            check.setChecked(key in visible)
            layout.addWidget(check, row // 2, row % 2)
            checks.append((key, check))
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons, (len(COLUMNS) + 1) // 2, 0, 1, 2)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = [key for key, check in checks if check.isChecked()]
            if not selected:
                QMessageBox.warning(self, "Colonnes", "Au moins une colonne doit rester visible.")
                return
            self.controller.save_visible_columns(selected)
            self.apply_column_visibility()

    def update_kpis(self) -> None:
        counts = self.view_model.room_type_counts
        self.arrivals_kpi.setText(f"Arrivées : {self.view_model.row_count}")
        self.people_kpi.setText(f"Personnes : {self.view_model.people_count}")
        self.room_kpi.setText("Types chambres : " + ", ".join(f"{k} {v}" for k, v in counts.items()))

    def import_xml(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Importer un XML Opera Cloud", "", "XML (*.xml)")
        if not path:
            return
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.thread = QThread(self)
        self.worker = ImportWorker(Path(path))
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_import_progress)
        self.worker.finished.connect(self.on_import_finished)
        self.worker.failed.connect(self.on_import_failed)
        self.thread.start()

    def on_import_progress(self, current: int, total: int) -> None:
        self.progress.setMaximum(max(total, 1))
        self.progress.setValue(current)

    def on_import_finished(self, guests: list[Guest]) -> None:
        count = self.controller.replace_import(guests)
        self.progress.setVisible(False)
        self.thread.quit()
        self.thread.wait()
        self.reload_table()
        QMessageBox.information(self, "Import terminé", f"{count} arrivée(s) importée(s).")

    def on_import_failed(self, message: str) -> None:
        self.progress.setVisible(False)
        self.thread.quit()
        self.thread.wait()
        QMessageBox.critical(self, "Import impossible", message)

    def row_guest(self, row: int) -> Guest | None:
        return self.guests[row] if 0 <= row < len(self.guests) else None

    def persist_combo_change(self, row: int) -> None:
        guest = self.row_guest(row)
        if not guest:
            return
        gender_widget = self.table.cellWidget(row, 3)
        language_widget = self.table.cellWidget(row, 4)
        if isinstance(gender_widget, QComboBox) and isinstance(language_widget, QComboBox):
            self.controller.update_guest_language_gender(
                guest.reservation_id,
                Language(language_widget.currentText()),
                Gender(gender_widget.currentText()),
            )
            self.reload_table()

    def persist_cell_change(self, _row: int, _column: int) -> None:
        # Editable reservation fields are persisted through dedicated combo boxes in this first release.
        return

    def current_selection(self) -> list[Guest]:
        rows = sorted({index.row() for index in self.table.selectedIndexes()})
        return [self.guests[row] for row in rows] or self.guests[:1]

    def export_arrivals(self, kind: str) -> None:
        if not self.guests:
            QMessageBox.information(self, "Export", "Aucune arrivée à exporter pour la date sélectionnée.")
            return
        extension = "xlsx" if kind == "xlsx" else "docx"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les arrivées",
            f"arrivees_{self.selected_arrival_date():%Y%m%d}.{extension}",
            f"Fichiers {extension.upper()} (*.{extension})",
        )
        if not path:
            return
        self.controller.export_arrivals(kind, self.guests, path)
        QMessageBox.information(self, "Export terminé", f"Fichier créé : {path}")

    def purge_import(self) -> None:
        if QMessageBox.question(
            self,
            "Purger les données",
            "Supprimer toutes les arrivées stockées localement ?",
        ) == QMessageBox.StandardButton.Yes:
            self.controller.clear_arrivals()
            self.reload_table()

    def preview_selection(self) -> None:
        model = self.model_combo.currentText()
        kind = "key" if "Carton" in model else "letter" if "Welcome" in model else "arrivals"
        self.preview_or_print(kind, self.current_selection(), print_now=False)

    def print_selection(self) -> None:
        model = self.model_combo.currentText()
        kind = "key" if "Carton" in model else "letter" if "Welcome" in model else "arrivals"
        self.preview_or_print(kind, self.current_selection(), print_now=True)

    def preview_or_print(self, kind: str, guests: list[Guest], print_now: bool) -> None:
        if not guests:
            QMessageBox.information(self, "Aucune arrivée", "Aucune ligne n'est disponible pour cette action.")
            return
        html = self.render(kind, guests)
        if print_now:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            dialog = QPrintDialog(printer, self)
            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                QMessageBox.information(self, "Impression", "Document préparé. Utilisez l'aperçu HTML pour contrôle qualité dans cette préversion.")
        target = Path(tempfile.gettempdir()) / f"opera_rapports_{kind}.html"
        target.write_text(html, encoding="utf-8")
        QDesktopServices.openUrl(target.as_uri())

    def render(self, kind: str, guests: list[Guest]) -> str:
        return self.controller.render_report(kind, guests)

    def apply_theme(self, theme: str) -> None:
        self.controller.save_theme(theme)
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow, QWidget { background: #151922; color: #f1f5f9; }
                QTableWidget { background: #1f2633; gridline-color: #394152; }
                QHeaderView::section, QToolBar, QMenuBar { background: #252d3b; color: #f1f5f9; }
                QLabel#kpi { padding: 12px; border-radius: 8px; background: #243047; font-weight: 700; }
            """)
        else:
            self.setStyleSheet("""
                QLabel#kpi { padding: 12px; border-radius: 8px; background: #eef4ff; color: #1e3a8a; font-weight: 700; }
            """)


def run(argv: list[str]) -> int:
    app = QApplication(argv)
    app.setApplicationName("Opera Rapports")
    app.setWindowIcon(QIcon())
    window = MainWindow()
    window.show()
    return app.exec()

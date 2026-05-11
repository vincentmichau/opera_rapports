from __future__ import annotations

import tempfile
from pathlib import Path

from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from opera_rapports.core.document_templates import DocumentTemplate, TemplateKind
from opera_rapports.core.template_rendering import AVAILABLE_FIELDS
from opera_rapports.mvc.controllers import AppController


class TemplateDesignerDialog(QDialog):
    """Simple designer for editable document templates.

    The dialog deliberately stays form-based instead of a complex graphic editor for now:
    it is easier for non-technical users to understand and provides a safe foundation for
    the future ruler/grid designer described in the roadmap.
    """

    def __init__(self, controller: AppController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller
        self.templates: list[DocumentTemplate] = []
        self.setWindowTitle("Concepteur de modèles")
        self.resize(900, 680)
        self._build_ui()
        self.refresh()

    @staticmethod
    def kind_label(kind: TemplateKind) -> str:
        labels = {
            TemplateKind.KEY_CARD: "Carton de clé",
            TemplateKind.WELCOME_LETTER: "Welcome letter",
            TemplateKind.ARRIVALS_PORTRAIT: "Liste arrivées portrait",
            TemplateKind.ARRIVALS_LANDSCAPE: "Liste arrivées paysage",
        }
        return labels[kind]

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        fields = ", ".join(f"{{{name}}}" for name in AVAILABLE_FIELDS)
        intro = QLabel(
            "Créez, modifiez, dupliquez ou supprimez vos modèles. "
            "Les modèles intégrés sont protégés : dupliquez-les pour les personnaliser. "
            f"Champs disponibles : {fields}"
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        selector_row = QHBoxLayout()
        self.template_combo = QComboBox()
        selector_row.addWidget(QLabel("Modèle :"))
        selector_row.addWidget(self.template_combo, 1)
        self.new_button = QPushButton("Nouveau")
        self.duplicate_button = QPushButton("Dupliquer")
        self.preview_button = QPushButton("Aperçu modèle")
        self.delete_button = QPushButton("Supprimer")
        selector_row.addWidget(self.new_button)
        selector_row.addWidget(self.duplicate_button)
        selector_row.addWidget(self.preview_button)
        selector_row.addWidget(self.delete_button)
        layout.addLayout(selector_row)

        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.kind_combo = QComboBox()
        for kind in TemplateKind:
            self.kind_combo.addItem(self.kind_label(kind), kind.value)
        self.description_edit = QLineEdit()
        self.content_edit = QTextEdit()
        self.css_edit = QTextEdit()
        self.content_edit.setPlaceholderText(
            "Texte du modèle avec variables : {nom}, {prenom}, {chambre}, {arrivee}, {depart}, {hotel}..."
        )
        self.css_edit.setPlaceholderText("CSS d'impression : @page, .sheet, polices, marges...")
        form.addRow("Nom", self.name_edit)
        form.addRow("Type", self.kind_combo)
        form.addRow("Description", self.description_edit)
        form.addRow("Contenu", self.content_edit)
        form.addRow("Style CSS", self.css_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Close)
        layout.addWidget(buttons)
        self.template_combo.currentIndexChanged.connect(self.load_current)
        self.new_button.clicked.connect(self.create_new)
        self.duplicate_button.clicked.connect(self.duplicate_current)
        self.preview_button.clicked.connect(self.preview_current)
        self.delete_button.clicked.connect(self.delete_current)
        buttons.accepted.connect(self.save_current)
        buttons.rejected.connect(self.reject)

    def refresh(self, selected_id: str | None = None) -> None:
        self.templates = self.controller.list_document_templates()
        self.template_combo.blockSignals(True)
        self.template_combo.clear()
        for template in self.templates:
            suffix = " (intégré)" if template.is_builtin else ""
            label = f"{template.name} — {self.kind_label(template.kind)}{suffix}"
            self.template_combo.addItem(label, template.id)
        if selected_id:
            index = self.template_combo.findData(selected_id)
            if index >= 0:
                self.template_combo.setCurrentIndex(index)
        self.template_combo.blockSignals(False)
        self.load_current()

    def current_template(self) -> DocumentTemplate | None:
        template_id = self.template_combo.currentData()
        return next((template for template in self.templates if template.id == template_id), None)

    def load_current(self) -> None:
        template = self.current_template()
        if template is None:
            return
        self.name_edit.setText(template.name)
        self.kind_combo.setCurrentIndex(max(self.kind_combo.findData(template.kind.value), 0))
        self.description_edit.setText(template.description)
        self.content_edit.setPlainText(template.content)
        self.css_edit.setPlainText(template.css)
        self.delete_button.setEnabled(not template.is_builtin)

    def edited_template(self, force_custom: bool = False) -> DocumentTemplate | None:
        template = self.current_template()
        if template is None:
            return None
        return DocumentTemplate(
            id=template.id,
            name=self.name_edit.text().strip() or "Nouveau modèle",
            kind=TemplateKind(self.kind_combo.currentData()),
            description=self.description_edit.text().strip(),
            content=self.content_edit.toPlainText(),
            css=self.css_edit.toPlainText(),
            is_builtin=template.is_builtin and not force_custom,
        )

    def save_current(self) -> None:
        template = self.edited_template(force_custom=True)
        original = self.current_template()
        if template is None or original is None:
            return
        if original.is_builtin:
            QMessageBox.information(self, "Modèle intégré", "Dupliquez ce modèle intégré avant de le modifier.")
            return
        validation = self.controller.validate_document_template(template)
        if not validation.is_valid:
            QMessageBox.warning(self, "Champs inconnus", validation.message)
            return
        self.controller.save_document_template(template)
        self.refresh(template.id)
        QMessageBox.information(self, "Modèle enregistré", "Le modèle a été enregistré.")

    def preview_current(self) -> None:
        template = self.edited_template()
        if template is None:
            return
        validation = self.controller.validate_document_template(template)
        if not validation.is_valid:
            QMessageBox.warning(self, "Champs inconnus", validation.message)
            return
        target = Path(tempfile.gettempdir()) / "opera_rapports_template_preview.html"
        target.write_text(self.controller.preview_document_template(template), encoding="utf-8")
        QDesktopServices.openUrl(target.as_uri())

    def create_new(self) -> None:
        template = self.controller.create_document_template()
        self.refresh(template.id)

    def duplicate_current(self) -> None:
        template = self.current_template()
        if template is None:
            return
        duplicate = self.controller.duplicate_document_template(template.id)
        if duplicate:
            self.refresh(duplicate.id)

    def delete_current(self) -> None:
        template = self.current_template()
        if template is None:
            return
        if QMessageBox.question(self, "Supprimer", f"Supprimer le modèle {template.name} ?") == QMessageBox.StandardButton.Yes:
            if not self.controller.delete_document_template(template.id):
                QMessageBox.warning(self, "Suppression impossible", "Les modèles intégrés ne peuvent pas être supprimés.")
            self.refresh()

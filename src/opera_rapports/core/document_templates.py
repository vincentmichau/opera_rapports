from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from uuid import uuid4


class TemplateKind(StrEnum):
    KEY_CARD = "key_card"
    WELCOME_LETTER = "welcome_letter"
    ARRIVALS_PORTRAIT = "arrivals_portrait"
    ARRIVALS_LANDSCAPE = "arrivals_landscape"


@dataclass(slots=True)
class DocumentTemplate:
    id: str
    name: str
    kind: TemplateKind
    description: str
    content: str
    css: str
    is_builtin: bool = False

    @classmethod
    def from_mapping(cls, value: dict[str, object]) -> "DocumentTemplate":
        return cls(
            id=str(value.get("id", uuid4().hex)),
            name=str(value.get("name", "Nouveau modèle")),
            kind=TemplateKind(str(value.get("kind", TemplateKind.WELCOME_LETTER.value))),
            description=str(value.get("description", "")),
            content=str(value.get("content", "")),
            css=str(value.get("css", "")),
            is_builtin=bool(value.get("is_builtin", False)),
        )

    def to_mapping(self) -> dict[str, object]:
        payload = asdict(self)
        payload["kind"] = self.kind.value
        return payload

    def duplicate(self) -> "DocumentTemplate":
        return DocumentTemplate(
            id=uuid4().hex,
            name=f"Copie de {self.name}",
            kind=self.kind,
            description=self.description,
            content=self.content,
            css=self.css,
            is_builtin=False,
        )


DEFAULT_TEMPLATES = [
    DocumentTemplate(
        id="builtin_key_card_a6",
        name="Carton de clé A6 paysage",
        kind=TemplateKind.KEY_CARD,
        description="Carton de clé hôtelier en A6 paysage, police MV Boli.",
        content="{civilite} {nom}\nChambre {chambre}\n{arrivee} → {depart}",
        css="@page { size: A6 landscape; margin: 0; }\n.sheet { font-family: 'MV Boli', 'Segoe Print', cursive; }",
        is_builtin=True,
    ),
    DocumentTemplate(
        id="builtin_welcome_dl",
        name="Welcome letter DL paysage",
        kind=TemplateKind.WELCOME_LETTER,
        description="Lettre de bienvenue DL paysage en Aptos 11 pt.",
        content="{date_longue}\n\n{civilite} {nom},\n\nBienvenue au {hotel}. Votre chambre {chambre} vous attend.\n\n{directeur}\n{fonction}",
        css="@page { size: 220mm 110mm landscape; margin: 0; }\n.sheet { font-family: Aptos, Calibri, sans-serif; font-size: 11pt; }",
        is_builtin=True,
    ),
    DocumentTemplate(
        id="builtin_arrivals_portrait",
        name="Liste des arrivées A4 portrait",
        kind=TemplateKind.ARRIVALS_PORTRAIT,
        description="Liste imprimable portrait avec colonne annotation.",
        content="Titre : Liste des arrivées du {date}\nColonnes : chambre, nom, prénom, civilité, arrivée, départ, annotation",
        css="@page { size: A4 portrait; margin: 12mm; }\ntable { width: 100%; border-collapse: collapse; }",
        is_builtin=True,
    ),
    DocumentTemplate(
        id="builtin_arrivals_landscape",
        name="Liste des arrivées A4 paysage",
        kind=TemplateKind.ARRIVALS_LANDSCAPE,
        description="Liste imprimable paysage avec colonne annotation large.",
        content="Titre : Liste des arrivées du {date}\nColonnes : chambre, nom, prénom, civilité, arrivée, départ, annotation",
        css="@page { size: A4 landscape; margin: 12mm; }\ntable { width: 100%; border-collapse: collapse; }",
        is_builtin=True,
    ),
]


class TemplateCatalog:
    def __init__(self, templates: list[DocumentTemplate] | None = None) -> None:
        self.templates = templates or [template for template in DEFAULT_TEMPLATES]

    @classmethod
    def from_settings(cls, value: object) -> "TemplateCatalog":
        if not isinstance(value, list):
            return cls()
        templates = [DocumentTemplate.from_mapping(item) for item in value if isinstance(item, dict)]
        if not templates:
            return cls()
        existing_ids = {template.id for template in templates}
        for template in DEFAULT_TEMPLATES:
            if template.id not in existing_ids:
                templates.append(template)
        return cls(templates)

    def to_settings(self) -> list[dict[str, object]]:
        return [template.to_mapping() for template in self.templates]

    def list(self) -> list[DocumentTemplate]:
        return sorted(self.templates, key=lambda template: (template.kind.value, template.name.lower()))

    def get(self, template_id: str) -> DocumentTemplate | None:
        return next((template for template in self.templates if template.id == template_id), None)

    def upsert(self, template: DocumentTemplate) -> None:
        for index, existing in enumerate(self.templates):
            if existing.id == template.id:
                self.templates[index] = template
                return
        self.templates.append(template)

    def delete(self, template_id: str) -> bool:
        template = self.get(template_id)
        if template is None or template.is_builtin:
            return False
        self.templates = [item for item in self.templates if item.id != template_id]
        return True

    def create_blank(self, kind: TemplateKind = TemplateKind.WELCOME_LETTER) -> DocumentTemplate:
        return DocumentTemplate(
            id=uuid4().hex,
            name="Nouveau modèle",
            kind=kind,
            description="Modèle personnalisé",
            content="{civilite} {nom}\n\nVotre texte ici.",
            css=".sheet { font-family: Aptos, Calibri, sans-serif; font-size: 11pt; }",
            is_builtin=False,
        )

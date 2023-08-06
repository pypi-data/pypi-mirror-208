from django.db import models as _models
from model_utils.models import TimeStampedModel as _TimeStampedModel

from b2_utils.models.enums import Colors, Operator, OrderedTextChoices, States

__all__ = [
    "Phone",
    "City",
    "Address",
    "States",
    "Colors",
    "Operator",
    "OrderedTextChoices",
]


class Phone(_TimeStampedModel):
    """A TimeStampedModel Phone model, ordered by it's creation date"""

    country_code = _models.CharField("Código do país", default="55", max_length=3)
    area_code = _models.CharField("Código de Area", max_length=3)
    number = _models.CharField("Número", max_length=9)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Telefone"
        verbose_name_plural = "Telefones"

    def __str__(self) -> str:
        return f"({self.country_code}) {self.area_code}-{self.number}"


class City(_TimeStampedModel):
    """A TimeStampedModel City model, ordered by it's creation date"""

    name = _models.CharField("Cidade", max_length=255)
    state = _models.CharField("Estado", max_length=2, choices=States.choices)

    class Meta:
        unique_together = ["name", "state"]
        ordering = ["-created"]
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"

    def __str__(self) -> str:
        return f"{self.name}, {self.state}"


class Address(_TimeStampedModel):
    """A TimeStampedModel Address model, ordered by it's creation date"""

    zip_code = _models.CharField("CEP", max_length=10)
    city = _models.ForeignKey(City, on_delete=_models.PROTECT)
    district = _models.CharField("Bairro", max_length=255)
    street = _models.CharField("Rua", max_length=255)
    number = _models.CharField("Número", max_length=10)
    additional_info = _models.CharField(
        "Complemento",
        max_length=255,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created"]
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

    def __str__(self) -> str:
        return (
            f"{self.zip_code}:{self.street}, {self.number} - {self.additional_info} -"
            f" {self.district} - {self.city}"
        )

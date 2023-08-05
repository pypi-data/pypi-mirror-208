import os

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

phone_regex = RegexValidator(regex=r"^\+?[1-9]?\d{9,15}$")
inn_regex = RegexValidator(regex=r"^\d{10,12}$")
kpp_regex = RegexValidator(regex=r"^\d{9}$")
ogrn_regex = RegexValidator(regex=r"^\d{13,15}$")
issued_code_regex = RegexValidator(regex=r"^\d{3}-\d{3}$")
ogrnip_regex = RegexValidator(regex=r"^\d{15}$")
okpo_regex = RegexValidator(regex=r"^(\d{8}|\d{10})$")
rs_regex = RegexValidator(regex=r"^(\d{20}|\d{22})$")
ks_regex = RegexValidator(regex=r"^\d{20}$")
bik_regex = RegexValidator(regex=r"^\d{9}$")
card_regex = RegexValidator(regex=r"^\d{13,16}$")
bank_account_regex = RegexValidator(regex=r"^\d{20}$")
snils_regex = RegexValidator(regex=r"^\d{3}-\d{3}-\d{3}\s\d{2}$")
foreign_document_number_regex = RegexValidator(regex=r"^\d+$")


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = [".pdf", ".jpg", ".jpeg", ".png", ".heic"]
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported file extension.")

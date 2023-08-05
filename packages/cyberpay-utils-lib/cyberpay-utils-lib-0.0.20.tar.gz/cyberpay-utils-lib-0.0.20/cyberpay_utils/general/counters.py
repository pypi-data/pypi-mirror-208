from django.db import models


class UserStatus(models.TextChoices):
    CHECKING = "CHECKING", "На проверке"
    PROBLEM = "PROBLEM", "Есть проблемы"
    VERIFIED = "VERIFIED", "Проверен"
    BANNED = "BANNED", "Забанен"


class CompanyUserState(models.TextChoices):
    READY = "READY", "Готов к работе"
    PROBLEM = "PROBLEM", "Есть проблемы"
    BAN = "BAN", "Черный список"
    CHECK = "CHECK", "Проверка документов"
    WAITING_EMP = "WAITING_EMP", "Ожидание подписания Исполнителем"
    REFUSED = "REFUSED", "Отказался"
    DENIDED = "DENIDED", "Документы отклонены"


# Type of employees
class ProfileType(models.TextChoices):
    SP = "SP", "Индивидуальный предприниматель"
    SELF_EMPLOYED = "SE", "Самозанятый"
    NATURAL_PERSON = "NP", "Физ. лицо"
    FOREIGN_RESIDENT = "FR", "РИГ"


class CompanyType(models.TextChoices):
    LLC = "LLC", "ООО"
    SP = "SP", "Индивидуальный предприниматель"


# Type of company user
class CompanyUserType(models.TextChoices):
    COMPANY_DIRECTOR = "COMPANY_DIRECTOR", "Директор"
    COMPANY_ADMIN = "COMPANY_ADMIN", "Администратор"
    COMPANY_ACCOUNTANT = "COMPANY_ACCOUNTANT", "Бухгалтер"
    COMPANY_MANAGER_WITH_SIGN = "COMPANY_MANAGER_WITH_SIGN", "Менеджер с правом подписи"
    COMPANY_MANAGER = "COMPANY_MANAGER", "Менеджер без права подписи"
    COMPANY_READONLY = "COMPANY_READONLY", "Только просмотр"
    COMPANY_EMPLOYEE = "COMPANY_EMPLOYEE", "Работник"


# State of Task
class TaskState(models.TextChoices):
    ISSUED = "ISSUED", "Выдано"
    REJECTED = "REJECTED", "Отклонено"
    CREATING_CONTRACT = "CREATING_CONTRACT", "Создание договора"
    SIGNING_CONTRACT = "SIGNING_CONTRACT", "Подписание договора"
    STARTED = "STARTED", "В процессе"
    FINISHED = "FINISHED", "Выполнено"
    CHECK_TASK = "CHECK", "Проверка"
    CLOSED = "CLOSED", "Завершено"



# Type of task document
class TaskDocumentType(models.TextChoices):
    CONTRACT = "CONTRACT", "Договор"
    OTHER = "OTHER", "Другое"

STATE_OF_PAYMENT = {
    "NEW": "Платеж создан",
    "PAYMENT_IN_PROGRESS": "Платеж обрабатывается",
    "COMPLETED": "Платеж выполнен",
    "CANCELLED": "Платеж отменен",
    "PAYMENT_FAILED": "Ошибка оплаты",
}


# Foreign document type
class UserForeignDocumentType(models.TextChoices):
    MIGRATION_CARD = "MIGRATION_CARD", "Миграционная карта"
    TEMPORARY_RESIDENCE_PERMIT = (
        "TEMPORARY_RESIDENCE_PERMIT",
        "Разрешение на временное проживание",
    )
    RESIDENCE_PERMIT = "RESIDENCE_PERMIT", "Вид на жительство"
    VISA = "VISA", "Виза"

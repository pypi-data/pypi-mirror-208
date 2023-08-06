from datetime import datetime

from transliterate import translit


def create_filename(title: str, filename: str):
    extention = filename.split(".")[-1].lower()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    clear_title = translit(title.strip().replace(" ", "_"), "ru", True)

    ACCEPTED_EXTENTIONS = ["jpg", "jpeg", "png", "pdf", "heic"]

    if extention in ACCEPTED_EXTENTIONS:
        filename = f"{clear_title}_{timestamp}.{extention}"
    else:
        filename = f"{clear_title}_{timestamp}.txt"

    return filename

from xm_ai.database_utils import db
from typing import List, Union


def get_template_by_id(template_id: str) -> dict:
    _template = db.templates.find_one({"_id": template_id})
    assert type(_template) == dict
    return _template


def get_playbooks_from_template(template: dict) -> List[dict]:
    return template['draft']['playbooks']


def get_catalogEntries_from_playbook(playbook: dict) -> List[dict]:
    return playbook['entries']


def get_text_from_catalogEntry(catalogEntry: dict, language_ids: Union[None, list] = None) -> str:
    try:
        if language_ids is None:
            language_ids = ["en-US", "en"]
        for translation in catalogEntry['selectedVariant']['translations']:
            if translation['langId'] in language_ids:
                return translation['text']  # this will return text from the first translation dict with a matching langId
            else:
                raise ValueError("There were no matching texts for the languages that were provided")
    except KeyError:  # some catalogEntries don't have anything in them except for an ID
        return "NaN"


def get_parentEntry_name_from_catalogEntry(catalogEntry: dict) -> str:
    try:
        parentEntryId = db.catalogEntries.find_one({"_id": catalogEntry["_id"]})["parentEntryId"]
    except KeyError:
        return "Unmapped"

    try:
        name = db.catalogEntries.find_one({"_id": parentEntryId})['name']
    except KeyError:  # means that this clause was the root clause
        return "root"

    return name


def get_name_from_account_id(account_id: str) -> str:
    return db.accounts.find_one({"_id": account_id})['name']


def get_name_from_template_id(template_id: str) -> str:
    return db.templates.find_one({"_id": template_id})['name']


def get_name_from_catalogEntry_id(entry_id: str) -> str:
    return db.catalogEntries.find_one({"_id": entry_id})['name']

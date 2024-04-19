# Copyright 2024 Florian Tautz
# This program is licensed under the MIT License,
# see the contents of the LICENSE file in this directory for details.

from esi_client.api.character_api import CharacterApi


def character_name(character_id: int) -> str:
    api = CharacterApi()
    character = api.get_characters_character_id(character_id=character_id)
    return character.name

from .en import English

class French(English):
    DEFAULT_FOOTER = "Demandé par {user}"
    
    SHORTEN_URL_WRONG_URL = "Merci d'entrer un url valide."
    
    TRANSLATE_TEXT_ORIGINAL = "Original"
    TRANSLATE_TEXT_TRANSLATED = "Traduit"
    TRANSLATE_TEXT_LANG_CODE_ERR = "Le paramètre langage doit être un code de langage : https://fr.wikipedia.org/wiki/Liste_des_codes_ISO_639-1"
    
    SEARCH_ON_WIKIPEDIA_DESCRIPTION = "Utilisez la barre pour obtenir l'article que vous souhaitez ! (elle ne mordra pas)"
    SEARCH_ON_WIKIPEDIA_PLACEHOLDER = "Sélectionnez un article ici :"
    SEARCH_ON_WIKIPEDIA_EMPTY_SUMMARY = "Ah. Désolé mais quelque chose s'est mal passé, [essayez de cliquer ici plutôt]({link})."
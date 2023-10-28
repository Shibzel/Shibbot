from .en import English

class French(English):
    DEFAULT_FOOTER = "Demandé par {user}"
    
    GET_MEME_CHECK_SUBREDDIT = "Subreddits  : {subreds}."
    GET_MEME_NEXT_BUTTON = "Meme suivant"
    GET_MEME_PREVIOUS_BUTTON = "Précédent"
    
    GET_SHIBES_NEXT_BUTTON = "Shiba suivant"
    GET_SHIBES_PREVIOUS_BUTTON = "Précédent"
    
    GET_CATS_NEXT_BUTTON = "Chat suivant"
    GET_CATS_PREVIOUS_BUTTON = "Précédent"
    
    GET_BIRDS_NEXT_BUTTON = "Piaf suivant"
    GET_BIRDS_PREVIOUS_BUTTON = "Précédent"
    
    GET_CAPY_NEXT_BUTTON = "Capybara suivant"
    GET_CAPY_PREVIOUS_BUTTON = "Précédent"
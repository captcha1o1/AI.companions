"""Text processing utilities for the anime AI."""

import re
import emoji

class TextProcessor:
    # Common English contractions and their expansions
    CONTRACTIONS = {
        "ain't": "am not",
        "aren't": "are not",
        "can't": "cannot",
        "couldn't": "could not",
        "didn't": "did not",
        "doesn't": "does not",
        "don't": "do not",
        "hadn't": "had not",
        "hasn't": "has not",
        "haven't": "have not",
        "he'd": "he would",
        "he'll": "he will",
        "he's": "he is",
        "i'd": "I would",
        "i'll": "I will",
        "i'm": "I am",
        "i've": "I have",
        "isn't": "is not",
        "it's": "it is",
        "let's": "let us",
        "mightn't": "might not",
        "mustn't": "must not",
        "shan't": "shall not",
        "she'd": "she would",
        "she'll": "she will",
        "she's": "she is",
        "shouldn't": "should not",
        "that's": "that is",
        "there's": "there is",
        "they'd": "they would",
        "they'll": "they will",
        "they're": "they are",
        "they've": "they have",
        "we'd": "we would",
        "we're": "we are",
        "we've": "we have",
        "weren't": "were not",
        "what'll": "what will",
        "what're": "what are",
        "what's": "what is",
        "what've": "what have",
        "where's": "where is",
        "who'd": "who would",
        "who'll": "who will",
        "who're": "who are",
        "who's": "who is",
        "who've": "who have",
        "won't": "will not",
        "wouldn't": "would not",
        "you'd": "you would",
        "you'll": "you will",
        "you're": "you are",
        "you've": "you have",
        "y'all": "you all",
    }

    @classmethod
    def expand_contractions(cls, text):
        """Expand contractions in the given text."""
        words = text.split()
        expanded_words = []
        
        for word in words:
            # Check for contractions in different cases
            lower_word = word.lower()
            if lower_word in cls.CONTRACTIONS:
                # Preserve original capitalization if word was capitalized
                if word[0].isupper():
                    expanded = cls.CONTRACTIONS[lower_word].capitalize()
                else:
                    expanded = cls.CONTRACTIONS[lower_word]
                expanded_words.append(expanded)
            else:
                expanded_words.append(word)
        
        return " ".join(expanded_words)

    @classmethod
    def preprocess_for_tts(cls, text):
        """Preprocess text for TTS by removing or replacing special characters"""
        # Remove emojis
        text = emoji.replace_emoji(text, '')
        
        # Remove asterisks and ellipsis
        text = text.replace('*', '')
        text = text.replace('...', '')
        text = text.replace('…', '')
        
        # Remove any remaining special characters that might affect TTS
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip() 
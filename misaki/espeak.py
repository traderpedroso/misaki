from phonemizer.backend.espeak.wrapper import EspeakWrapper
from typing import List, Tuple, Union
import espeakng_loader
import phonemizer
import re
from .token import MToken
from dataclasses import replace
import unicodedata
import spacy


# EspeakFallback is used as a last resort for English
class EspeakFallback:
    E2M = sorted(
        {
            "ʔˌn\u0329": "tn",
            "ʔn\u0329": "tn",
            "ʔn": "tn",
            "ʔ": "t",
            "a^ɪ": "I",
            "a^ʊ": "W",
            "d^ʒ": "ʤ",
            "e^ɪ": "A",
            "e": "A",
            "t^ʃ": "ʧ",
            "ɔ^ɪ": "Y",
            "ə^l": "ᵊl",
            "ʲo": "jo",
            "ʲə": "jə",
            "ʲ": "",
            "ɚ": "əɹ",
            "r": "ɹ",
            "x": "k",
            "ç": "k",
            "ɐ": "ə",
            "ɬ": "l",
            "\u0303": "",
        }.items(),
        key=lambda kv: -len(kv[0]),
    )


# EspeakG2P used for most non-English/CJK languages
class EspeakG2P:
    E2M = sorted(
        {
            "a^ɪ": "I",
            "a^ʊ": "W",
            "d^z": "ʣ",
            "d^ʒ": "ʤ",
            "e^ɪ": "A",
            "o^ʊ": "O",
            "ə^ʊ": "Q",
            "s^s": "S",
            "t^s": "ʦ",
            "t^ʃ": "ʧ",
            "ɔ^ɪ": "Y",
        }.items()
    )

    def __init__(self, language, unk="❓"):
        self.language = language
        self.unk = unk
        self.backend = phonemizer.backend.EspeakBackend(
            language=language,
            preserve_punctuation=True,
            with_stress=True,
            tie="^",
            language_switch="remove-flags",
        )

        # Initialize spaCy for tagging
        try:
            # Try to load a language-specific model if available
            if language.startswith("en"):
                model = "en_core_web_sm"
            elif language.startswith("es"):
                model = "es_core_news_sm"
            elif language.startswith("fr"):
                model = "fr_core_news_sm"
            elif language.startswith("de"):
                model = "de_core_news_sm"
            elif language.startswith("pt"):
                model = "pt_core_news_sm"
            else:
                model = "xx_ent_wiki_sm"  # Multilingual model as fallback

            if not spacy.util.is_package(model):
                spacy.cli.download(model)
            self.nlp = spacy.load(model, disable=["ner", "parser"])
        except Exception as e:
            print(f"Warning: Could not load spaCy model: {e}")
            self.nlp = None

    def get_default_tag(self, word):
        """
        Get a default tag for a word when spaCy is not available
        """
        if word.isalpha():
            if word[0].isupper():
                return "NNP"  # Proper noun
            return "NN"  # Common noun
        elif word.isdigit():
            return "CD"  # Cardinal number
        elif word in ".!?":
            return "."  # Sentence terminator
        elif word in ",;:":
            return ","  # Comma, etc.
        elif word in "()[]{}":
            return "-LRB-" if word in "([{" else "-RRB-"  # Brackets
        return "SYM"  # Symbol

    def tokenize(self, text: str) -> List[MToken]:
        """
        Tokenize the text into MToken objects with proper tags.

        Args:
            text: The text to tokenize

        Returns:
            A list of MToken objects
        """
        if self.nlp:
            # Use spaCy for tokenization and tagging
            doc = self.nlp(text)
            tokens = []
            for t in doc:
                # Make sure tag is not empty, use POS if tag is empty
                tag = t.tag_ if t.tag_ else t.pos_
                tokens.append(
                    MToken(text=t.text, tag=tag, whitespace=t.whitespace_, is_head=True)
                )
            return tokens
        else:
            # Fallback to simple whitespace tokenization with default tags
            tokens = []
            words = text.split()
            for i, word in enumerate(words):
                whitespace = " " if i < len(words) - 1 else ""
                tag = self.get_default_tag(word)
                tokens.append(
                    MToken(text=word, tag=tag, whitespace=whitespace, is_head=True)
                )
            return tokens

    def process_token(self, token: MToken) -> None:
        """
        Process a single token to get its phonemes

        Args:
            token: The token to process
        """
        if token.phonemes is not None:
            return

        # Angles to curly quotes
        text = token.text.replace("«", chr(8220)).replace("»", chr(8221))
        # Parentheses to angles
        text = text.replace("(", "«").replace(")", "»")

        ps = self.backend.phonemize([text])
        if not ps or not ps[0].strip():
            token.phonemes = self.unk
            token.rating = 1
            return

        ps = ps[0].strip()
        for old, new in type(self).E2M:
            ps = ps.replace(old, new)
        # Delete any remaining tie characters, hyphens (not sure what they mean)
        ps = ps.replace("^", "").replace("-", "")
        # Angles back to parentheses
        ps = ps.replace("«", "(").replace("»", ")")

        token.phonemes = ps
        token.rating = 3  # Default rating for espeak

    def __call__(self, text: str, preprocess=True) -> Tuple[str, List[MToken]]:
        """
        Convert text to phonemes using eSpeak.

        Args:
            text: The text to convert
            preprocess: Whether to preprocess the text (not used, for compatibility)

        Returns:
            A tuple of (phoneme_string, tokens)
        """
        # Normalize text
        text = unicodedata.normalize("NFKC", text)

        # Tokenize with proper tags
        tokens = self.tokenize(text)

        # Process each token
        for token in tokens:
            self.process_token(token)

        # Combine phonemes into a single string
        result = "".join(
            (token.phonemes or self.unk) + token.whitespace for token in tokens
        )

        return result, tokens

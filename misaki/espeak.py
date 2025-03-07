from phonemizer.backend.espeak.wrapper import EspeakWrapper
from typing import List, Tuple, Union
import espeakng_loader
import phonemizer
import re
from .token import MToken
import spacy
import unicodedata


# EspeakFallback remains exactly the same as original
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

    def __init__(self, british):
        self.british = british
        EspeakWrapper.set_library(espeakng_loader.get_library_path())
        EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
        self.backend = phonemizer.backend.EspeakBackend(
            language=f"en-{'gb' if british else 'us'}",
            preserve_punctuation=True,
            with_stress=True,
            tie="^",
        )

    def __call__(self, token):
        ps = self.backend.phonemize([token.text])
        if not ps:
            return None, None
        ps = ps[0].strip()
        for old, new in type(self).E2M:
            ps = ps.replace(old, new)
        ps = re.sub(r"(\S)\u0329", r"ᵊ\1", ps).replace(chr(809), "")
        if self.british:
            ps = ps.replace("e^ə", "ɛː")
            ps = ps.replace("iə", "ɪə")
            ps = ps.replace("ə^ʊ", "Q")
        else:
            ps = ps.replace("o^ʊ", "O")
            ps = ps.replace("ɜːɹ", "ɜɹ")
            ps = ps.replace("ɜː", "ɜɹ")
            ps = ps.replace("ɪə", "iə")
            ps = ps.replace("ː", "")
        ps = ps.replace("o", "ɔ")
        return ps.replace("^", ""), 2


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
        try:
            if language.startswith("en"):
                model = "en_core_web_sm"
            elif language.startswith("pt"):
                model = "en_core_web_sm"
            else:
                model = "en_core_web_sm"

            if not spacy.util.is_package(model):
                spacy.cli.download(model)
            self.nlp = spacy.load(model, disable=["ner", "parser"])
        except Exception as e:
            print(f"Warning: Could not load spaCy model: {e}")
            self.nlp = None

    def get_default_tag(self, word):
        if word.isalpha():
            if word[0].isupper():
                return "NNP"
            return "NN"
        elif word.isdigit():
            return "CD"
        elif word in ".!?":
            return "."
        elif word in ",;:":
            return ","
        elif word in "()[]{}":
            return "-LRB-" if word in "([{" else "-RRB-"
        return "SYM"

    def tokenize(self, text: str) -> List[MToken]:
        if self.nlp:
            doc = self.nlp(text)
            tokens = []
            for t in doc:
                tag = t.tag_ if t.tag_ else t.pos_
                tokens.append(
                    MToken(text=t.text, tag=tag, whitespace=t.whitespace_, is_head=True)
                )
            return tokens
        else:
            tokens = []
            words = text.split()
            for i, word in enumerate(words):
                whitespace = " " if i < len(words) - 1 else ""
                tag = self.get_default_tag(word)
                tokens.append(
                    MToken(text=word, tag=tag, whitespace=whitespace, is_head=True)
                )
            return tokens

    def __call__(self, text: str, preprocess=True) -> Tuple[str, List[MToken]]:
        # Original phoneme processing
        if self.language == "pt-br":
            text = text.replace("porque", "porquê")
            text = text.replace("metas", "métas")
        text = unicodedata.normalize("NFC", text)
        text_for_phonemes = text.replace("«", chr(8220)).replace("»", chr(8221))
        text_for_phonemes = text_for_phonemes.replace("(", "«").replace(")", "»")
        ps = self.backend.phonemize([text_for_phonemes])
        if not ps:
            phonemes = ""
        else:
            phonemes = ps[0].strip()
            for old, new in type(self).E2M:
                phonemes = phonemes.replace(old, new)
            phonemes = phonemes.replace("^", "").replace("-", "")
            phonemes = phonemes.replace("«", "(").replace("»", ")")

        # Token processing
        tokens = self.tokenize(text)
        for token in tokens:
            token_ps = self.backend.phonemize([token.text])
            if token_ps and token_ps[0].strip():
                token.phonemes = token_ps[0].strip()
                token.rating = 3
            else:
                token.phonemes = self.unk
                token.rating = 1

        return phonemes, tokens

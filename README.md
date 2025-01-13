# misaki
Misaki is a G2P engine designed for Kokoro models.

Hosted demo: https://hf.co/spaces/hexgrad/Misaki-G2P

### Usage
You can run this in one cell on [Google Colab](https://colab.research.google.com/):
```py
!pip install -q misaki

from misaki import en

g2p = en.G2P(trf=False, british=False, fallback=None) # no transformer, American English

text = '[Misaki](/misˈɑki/) is a G2P engine designed for [Kokoro](/kˈOkəɹO/) models.'

phonemes, tokens = g2p(text)

print(phonemes) # misˈɑki ɪz ə ʤˈitəpˈi ˈɛnʤən dəzˈInd fɔɹ kˈOkəɹO mˈɑdᵊlz.
```

### Fallback to espeak
```py
# Installing espeak varies across platforms, this silent install works on Colab:
!apt-get -qq -y install espeak-ng > /dev/null 2>&1

!pip install -q misaki phonemizer

from misaki import en, espeak

fallback = espeak.EspeakFallback(british=False) # en-us

g2p = en.G2P(trf=False, british=False, fallback=fallback) # no transformer, American English

text = 'Now outofdictionary words are handled by espeak.'

phonemes, tokens = g2p(text)

print(phonemes) # nˈW Wɾɑfdˈɪkʃənˌɛɹi wˈɜɹdz ɑɹ hˈændəld bI ˈispik.
```

### Phonemes
https://github.com/hexgrad/misaki/blob/main/EN_PHONES.md

### TODO
- [ ] Data: Compress data (no need for indented json) and eliminate redundancy between gold and silver dictionaries.
- [ ] Fallbacks: Train seq2seq fallback models on dictionaries using [this notebook](https://github.com/Kyubyong/nlp_made_easy/blob/master/PyTorch%20seq2seq%20template%20based%20on%20the%20g2p%20task.ipynb).
- [ ] Homographs: Escalate hard words like `axes bass bow lead tear wind` using BERT contextual word embeddings (CWEs) and logistic regression models (`nn.Linear` followed by sigmoid) as described in [this paper](https://assets.amazon.science/c3/db/23ca18d7450d8dbb5b80a11fcdd3/homograph-disambiguation-with-contextual-word-embeddings-for-tts-systems.pdf). Assuming `trf=True`, BERT CWEs can be accessed via `doc._.trf_data`, see [en.py#L479](https://github.com/hexgrad/misaki/blob/main/misaki/en.py#L479).
- [ ] More languages: Add `ko.py`, `ja.py`, `zh.py`.
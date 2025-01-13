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

### Phonemes
https://github.com/hexgrad/misaki/EN_PHONES.md
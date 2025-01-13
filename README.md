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
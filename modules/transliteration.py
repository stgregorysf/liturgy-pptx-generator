import re


CUSTOM_MAP = {
    # Capitalized and multi-character common words/clusters
    'Եւ': 'Yév',
    'եւ': 'yév',
    'ընդ': 'ûnt',
    'հոգւոյդ': 'hokvooyt',
    'քում': 'koom',
    'Աստուած': 'Asdvadz',
    'Որ': 'Vor',
    'որ': 'vor',
    'Տէր': 'Dér',
    'ողորմեա': 'voghormya',
    'զմեզ': 'ûzméz',
    'կեցո': 'gétso',
    'Սուրբ': 'Soorp',
    'մեր': 'mér',
    'Ամէն': 'Amén',
    'Յիսուս': 'Hisoos',

    # Individual letters and phonetic elements based on dataset patterns
    'Ա': 'A',
    'ա': 'a',
    'Բ': 'P', # often transliterated as p or b depending on context
    'բ': 'p',
    'Գ': 'K',
    'գ': 'k',
    'Դ': 'T',
    'դ': 't',
    'Ե': 'Yé',
    'ե': 'é',
    'Զ': 'Z',
    'զ': 'z',
    'Է': 'É',
    'է': 'é',
    'Ը': 'Û',
    'ը': 'û',
    'Թ': 'T',
    'թ': 't',
    'Ժ': 'Zh',
    'ժ': 'zh',
    'Ի': 'I',
    'ի': 'i',
    'Լ': 'L',
    'լ': 'l',
    'Խ': 'Kh',
    'խ': 'kh',
    'Ծ': 'Dz',
    'ծ': 'dz',
    'Կ': 'G',
    'կ': 'g',
    'Հ': 'H',
    'հ': 'h',
    'Ձ': 'Dz',
    'ձ': 'dz',
    'Ղ': 'Gh',
    'ղ': 'gh',
    'Ճ': 'J',
    'ճ': 'j',
    'Մ': 'M',
    'մ': 'm',
    'Յ': 'Y',
    'յ': 'y',
    'Ն': 'N',
    'ն': 'n',
    'Շ': 'Sh',
    'շ': 'sh',
    'Ո': 'O',
    'ո': 'o',
    'Չ': 'Ch',
    'չ': 'ch',
    'Պ': 'B',
    'պ': 'b',
    'Ջ': 'J',
    'ջ': 'j',
    'Ռ': 'R',
    'ռ': 'r',
    'Ս': 'S',
    'ս': 's',
    'Վ': 'V',
    'վ': 'v',
    'Տ': 'D',
    'տ': 'd',
    'Ր': 'R',
    'ր': 'r',
    'Ց': 'Ts',
    'ց': 'ts',
    'Ւ': 'V',
    'ւ': 'v',
    'Փ': 'P',
    'փ': 'p',
    'Ք': 'K',
    'ք': 'k',
    'Օ': 'O',
    'օ': 'o',
    'Ֆ': 'F',
    'ֆ': 'f',
}

def parse_transliteration_data(filepath):
    """Parses the training file and extracts Armenian-to-transliteration pairs."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = content.split('----------------------------------------')
    training_pairs = []
    
    for section in sections:
        lines = [line.strip() for line in section.strip().split('\n') if line.strip()]
        if len(lines) >= 2:
            armenian_text = lines[0]
            translit_text = lines[1]
            training_pairs.append((armenian_text, translit_text))
            
    return training_pairs

def transliterate(armenian_text, custom_map=CUSTOM_MAP):
    """
    Transliterates Unicode Armenian text into Latin characters 
    based on a defined mapping dictionary.
    """
    # Split text into words and non-word tokens (preserving spaces and punctuation)
    tokens = re.findall(r'\w+|\W+', armenian_text)
    result = []
    
    # Sort mapping keys by length descending to handle multi-character mappings first
    sorted_keys = sorted(custom_map.keys(), key=len, reverse=True)
    pattern = re.compile('|'.join(re.escape(k) for k in sorted_keys))
    
    for token in tokens:
        # Check if the token is a word (contains alphabetic characters)
        if any(c.isalpha() for c in token):
            word = token
            
            # Rule 2: If a word starts with յ or Յ, use h/H instead of y/Y
            if word.startswith('Յ'):
                word = 'H' + word[1:]
            elif word.startswith('յ'):
                word = 'h' + word[1:]
                
            # Rule 1: If at any time in a word we see ու, replace with oo (handling both cases)
            word = word.replace('նս', 'nûs')
            word = word.replace('իւ', 'yoo')
            word = word.replace('ուա', 'va')
            word = word.replace('Ուա', 'Va')
            word = word.replace('ուԱ', 'Va')
            word = word.replace('ՈւԱ', 'Va')
            word = word.replace('կր', 'gûr')
            # սրբուհւոյ -> sûrpoohvo
            word = word.replace('ւոյ', 'vo')
            word = word.replace('ոյ', 'ooy')
            word = word.replace('եա', 'ya')
            # զԵկեղեցի -> zégéghétsi
            word = word.replace('զԵ', 'zé')
            # parékhosootyanûn
            word = word.replace('նն', 'nûn')
            word = word.replace('Ու', 'Oo').replace('ու', 'oo').replace(' ո', ' vo')

            # Word-initial 'ո' / 'Ո' -> 'vo' / 'Vo'
            word = re.sub(r'\bո', 'vo', word)
            word = re.sub(r'\bՈ', 'Vo', word)
            # երկնաւոր -> yérgnavor
            word = re.sub(r'\bե', 'yé', word)
            word = re.sub(r'\bԵ', 'Yé', word)

            # Remaining medial 'ո' / 'Ո' -> 'o' / 'O'
            word = word.replace('ո', 'o').replace('Ո', 'O')
            
            # Apply standard character mapping for the remaining Armenian characters
            word = pattern.sub(lambda m: custom_map[m.group(0)], word)
            
            result.append(word)
        else:
            result.append(token)
            
    return ''.join(result)


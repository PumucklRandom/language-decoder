# The placeholder is used to be able to "translate" special characters
# May be extended by additional placeholders
PUNCTUATIONS = '.!?'
BEG_PATTERNS = '#$<(\[{'
END_PATTERNS = ',;.:!?°%€>)\]}'
QUO_PATTERNS = '"\'´`'
CHAR_STRING = '&*+-/=\_|~§'
PLACEHOLDERS = dict()
for char in CHAR_STRING:
    PLACEHOLDERS[char] = f"-=<({hex(ord(char)).upper()})>=-"
    PLACEHOLDERS[f"-=<({hex(ord(char)).upper()})>=-"] = char

# A mapping dict to replace chars
CHARS = {'«': '"', '»': '"', '<<': '"', '>>': '"', '“': '"', '—': '-'}

RU2DE = {
    'ICH BIN': 'Ich', 'Ich bin': 'Ich', 'ich bin': 'ich', 'ICH': 'Ich', 'DU BIST': 'Du', 'Du bist': 'Du', 'du bist': 'du',
    'ER IST': 'Er', 'Er ist': 'Er', 'er ist': 'er', 'SIE IST': 'Sie', 'Sie ist': 'Sie', 'sie ist': 'sie',
    'ES IST': 'Es', 'Es ist': 'Es', 'es ist': 'es', 'WIR SIND': 'Wir', 'Wir sind': 'Wir', 'wir sind': 'wir',
    'IHR SEID': 'Ihr', 'Ihr seid': 'Ihr', 'ihr seid': 'ihr', 'SIE SIND': 'Sie', 'Sie sind': 'Sie', 'sie sind': 'sie',
    'BIN ICH': 'Ich', 'Bin ich': 'Ich', 'bin ich': 'ich', 'BIST DU': 'Du', 'Bist du': 'Du', 'bist du': 'du',
    'IST ER': 'Er', 'Ist er': 'Er', 'ist er': 'er', 'IST SIE': 'Sie', 'Ist sie': 'Sie', 'ist sie': 'sie',
    'IST ES': 'Es', 'Ist es': 'Es', 'ist es': 'es', 'SIND WIR': 'Wir', 'Sind wir': 'Wir', 'sind wir': 'wir',
    'SEID IHR': 'Ihr', 'Seid ihr': 'Ihr', 'seid ihr': 'ihr', 'SIND SIE': 'Sie', 'Sind sie': 'Sie', 'sind sie': 'sie',
    'Für dich': 'Euch', 'für dich': 'euch', 'Dein sein': 'Euer', 'dein sein': 'euer', 'Es gibt': 'sein',
    'U': 'Bei', 'u': 'bei', 'Verfügen über': 'Bei', 'beim': 'bei', 'Beim': 'Bei', 'ZU': 'Zu', 'Zu': 'zu', 'IN': 'In', 'V': 'In',
    'v': 'in', 'Ö': 'über', 'ö': 'über', 'UND': 'Und', 'EIN': 'Und', 'ABER': 'Und', 'MIT': 'Mit', 'Mit': 'mit', 'Pro': 'Für',
    'pro': 'für', 'von diesen': 'diese', 'BEI': 'In', 'ABER)': 'A)', 'BEIM': 'In', 'Std': 'Stunde', 'Std.': 'Stunde',
    'Auf der': 'Auf', 'auf der': 'auf', 'Jede einzelne': 'Jede', 'jede einzelne': 'jede', 'Sie sagen': 'sprechen',
    'tun': 'machen', 'Tun': 'machen', 'tut': 'macht', 'Tut': 'macht', 'tat': 'machte', 'Tat': 'machte', 'co': 'mit', 'Co': 'Mit'
}
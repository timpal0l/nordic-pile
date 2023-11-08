import unicodedata

# BigScience uses different thresholds for different languages, ranging from 0.002 to 0.3. English uses 0.3
# They have many more words though
STOP_WORD_RATIO_THRESHOLD = 0.10
STOP_WORD_STRIP_STRING = ".,!?:;\""

# stop_word = {"the", "be", "to", "of", "and", "have", "with", "that", "och", "att", "är", "på", "som", "en", "för",
#              "av", "og", "er", "på", "av", "for", "til", "som", "en", "og", "at", "er", "til", "af", "en", "på",
#              "for", "að", "og", "er", "sem", "til", "um", "með", "við"}

# Icelandic word list is found with statistics from mc4. Rest is from https://www.ranks.nl/stopwords
# stop_words_en = ["the", "be", "to", "of", "and", "have", "with", "that", "in", "was", "is", "for", "on"]
stop_words_en = ['down', 'could', 'own', 'as', 'her', 'which', 'where', 'while', 'between', 'under', 'again', 'am',
                 "mustn't", "they're", 'my', 'if', "couldn't", 'no', 'few', 'after', 'be', 'nor', 'has', 'any', 'he',
                 'each', 'had', "you'd", 'hers', 'for', 'being', 'further', 'myself', 'until', "how's", 'yourselves',
                 "she's", "doesn't", "haven't", 'here', "let's", 'into', 'some', "he'll", 'only', "she'll", "you're",
                 'your', 'me', "he'd", "she'd", "here's", 'against', "they'll", "why's", 'through', 'him', 'on', 'his',
                 'to', 'up', 'themselves', 'you', 'an', 'this', "shan't", 'were', "he's", 'by', 'and', 'about',
                 "aren't", 'their', 'our', 'was', 'the', 'in', 'are', 'above', "hadn't", 'of', 'same', 'its', 'them',
                 'from', 'yourself', 'ours', 'been', "who's", 'more', 'they', 'cannot', 'did', 'it', 'those', 'when',
                 'herself', 'ought', 'there', "shouldn't", 'how', 'below', "isn't", "i'd", "don't", "we'll", 'should',
                 'that', "when's", 'very', "where's", 'other', 'she', 'with', 'does', 'theirs', "can't", 'at', 'these',
                 'doing', 'have', 'having', 'such', "that's", 'would', "what's", 'during', "we're", 'once', 'do',
                 'yours', 'what', 'than', 'itself', 'out', 'then', 'who', 'over', "there's", "you've", "they've",
                 'too', "you'll", "i've", 'both', 'or', "i'm", "we'd", 'all', "wasn't", 'because', 'most', "they'd",
                 "wouldn't", "weren't", "hasn't", "won't", 'before', 'but', 'himself', 'not', "i'll", 'is', 'whom',
                 'off', 'why', "didn't", 'so', 'ourselves', "it's", "we've", 'we']

# stop_words_sv = ["och", "att", "är", "på", "som", "en", "för", "av", "den", "med", "till"]
# stop_words_sv = ['och', 'att', 'det', 'på', 'är', 'en', 'som', 'för', 'med', 'av', 'till', 'har', 'jag', 'om', 'den',
#                  'du', 'inte', 'ett', 'de', 'vi', 'så', 'kan', 'från', 'men', 'man', 'eller', 'var', 'ska', 'när',
#                  'här', 'in', 'alla', 'mer', 'sig', 'kommer', 'finns', 'nu', 'vara', 'the', 'under', 'hur', 'vad',
#                  'han', 'efter', 'får', 'även', 'vid', 'mycket', 'där', 'vill', 'bra', 'då', 'detta', 'få']

stop_words_sv = ['aderton', 'adertonde', 'adjö', 'aldrig', 'alla', 'allas', 'allt', 'alltid', 'alltså', 'än', 'andra',
                 'andras', 'annan', 'annat', 'ännu', 'artonde', 'artonn', 'åtminstone', 'att', 'åtta', 'åttio',
                 'åttionde', 'åttonde', 'av', 'även', 'båda', 'bådas', 'bakom', 'bara', 'bäst', 'bättre', 'behöva',
                 'behövas', 'behövde', 'behövt', 'beslut', 'beslutat', 'beslutit', 'bland', 'blev', 'bli', 'blir',
                 'blivit', 'bort', 'borta', 'bra', 'då', 'dag', 'dagar', 'dagarna', 'dagen', 'där', 'därför', 'de',
                 'del', 'delen', 'dem', 'den', 'deras', 'dess', 'det', 'detta', 'dig', 'din', 'dina', 'dit', 'ditt',
                 'dock', 'du', 'efter', 'eftersom', 'elfte', 'eller', 'elva', 'en', 'enkel', 'enkelt', 'enkla',
                 'enligt', 'er', 'era', 'ert', 'ett', 'ettusen', 'få', 'fanns', 'får', 'fått', 'fem', 'femte', 'femtio',
                 'femtionde', 'femton', 'femtonde', 'fick', 'fin', 'finnas', 'finns', 'fjärde', 'fjorton', 'fjortonde',
                 'fler', 'flera', 'flesta', 'följande', 'för', 'före', 'förlåt', 'förra', 'första', 'fram', 'framför',
                 'från', 'fyra', 'fyrtio', 'fyrtionde', 'gå', 'gälla', 'gäller', 'gällt', 'går', 'gärna', 'gått',
                 'genast', 'genom', 'gick', 'gjorde', 'gjort', 'god', 'goda', 'godare', 'godast', 'gör', 'göra', 'gott',
                 'ha', 'hade', 'haft', 'han', 'hans', 'har', 'här', 'heller', 'hellre', 'helst', 'helt', 'henne',
                 'hennes', 'hit', 'hög', 'höger', 'högre', 'högst', 'hon', 'honom', 'hundra', 'hundraen', 'hundraett',
                 'hur', 'ibland', 'idag', 'igår', 'igen', 'imorgon', 'in', 'inför', 'inga', 'ingen', 'ingenting',
                 'inget', 'innan', 'inne', 'inom', 'inte', 'inuti', 'ja', 'jag', 'jämfört', 'kan', 'kanske', 'knappast',
                 'kom', 'komma', 'kommer', 'kommit', 'kr', 'kunde', 'kunna', 'kunnat', 'kvar', 'länge', 'längre',
                 'långsam', 'långsammare', 'långsammast', 'långsamt', 'längst', 'långt', 'lätt', 'lättare', 'lättast',
                 'legat', 'ligga', 'ligger', 'lika', 'likställd', 'likställda', 'lilla', 'lite', 'liten', 'litet',
                 'man', 'många', 'måste', 'med', 'mellan', 'men', 'mer', 'mera', 'mest', 'mig', 'min', 'mina', 'mindre',
                 'minst', 'mitt', 'mittemot', 'möjlig', 'möjligen', 'möjligt', 'möjligtvis', 'mot', 'mycket', 'någon',
                 'någonting', 'något', 'några', 'när', 'nästa', 'ned', 'nederst', 'nedersta', 'nedre', 'nej', 'ner',
                 'ni', 'nio', 'nionde', 'nittio', 'nittionde', 'nitton', 'nittonde', 'nödvändig', 'nödvändiga',
                 'nödvändigt', 'nödvändigtvis', 'nog', 'noll', 'nr', 'nu', 'nummer', 'och', 'också', 'ofta', 'oftast',
                 'olika', 'olikt', 'om', 'oss', 'över', 'övermorgon', 'överst', 'övre', 'på', 'rakt', 'rätt', 'redan',
                 'så', 'sade', 'säga', 'säger', 'sagt', 'samma', 'sämre', 'sämst', 'sedan', 'senare', 'senast', 'sent',
                 'sex', 'sextio', 'sextionde', 'sexton', 'sextonde', 'sig', 'sin', 'sina', 'sist', 'sista', 'siste',
                 'sitt', 'sjätte', 'sju', 'sjunde', 'sjuttio', 'sjuttionde', 'sjutton', 'sjuttonde', 'ska', 'skall',
                 'skulle', 'slutligen', 'små', 'smått', 'snart', 'som', 'stor', 'stora', 'större', 'störst', 'stort',
                 'tack', 'tidig', 'tidigare', 'tidigast', 'tidigt', 'till', 'tills', 'tillsammans', 'tio', 'tionde',
                 'tjugo', 'tjugoen', 'tjugoett', 'tjugonde', 'tjugotre', 'tjugotvå', 'tjungo', 'tolfte', 'tolv', 'tre',
                 'tredje', 'trettio', 'trettionde', 'tretton', 'trettonde', 'två', 'tvåhundra', 'under', 'upp', 'ur',
                 'ursäkt', 'ut', 'utan', 'utanför', 'ute', 'vad', 'vänster', 'vänstra', 'var', 'vår', 'vara', 'våra',
                 'varför', 'varifrån', 'varit', 'varken', 'värre', 'varsågod', 'vart', 'vårt', 'vem', 'vems',
                 'verkligen', 'vi', 'vid', 'vidare', 'viktig', 'viktigare', 'viktigast', 'viktigt', 'vilka', 'vilken',
                 'vilket', 'vill']

# stop_words_no = ["og", "er", "på", "av", "for", "til", "som", "en", "som", "ble"]
stop_words_no = ['alle', 'at', 'av', 'både', 'båe', 'bare', 'begge', 'ble', 'blei', 'bli', 'blir', 'blitt', 'då', 'da',
                 'de', 'deg', 'dei', 'deim', 'deira', 'deires', 'dem', 'den', 'denne', 'der', 'dere', 'deres', 'det',
                 'dette', 'di', 'din', 'disse', 'ditt', 'du', 'dykk', 'dykkar', 'eg', 'ein', 'eit', 'eitt', 'eller',
                 'elles', 'en', 'enn', 'er', 'et', 'ett', 'etter', 'før', 'for', 'fordi', 'fra', 'ha', 'hadde', 'han',
                 'hans', 'har', 'hennar', 'henne', 'hennes', 'her', 'hjå', 'ho', 'hoe', 'honom', 'hoss', 'hossen',
                 'hun', 'hva', 'hvem', 'hver', 'hvilke', 'hvilken', 'hvis', 'hvor', 'hvordan', 'hvorfor', 'ikke',
                 'ikkje', 'ingen', 'ingi', 'inkje', 'inn', 'inni', 'ja', 'jeg', 'kan', 'kom', 'korleis', 'korso', 'kun',
                 'kunne', 'kva', 'kvar', 'kvarhelst', 'kven', 'kvi', 'kvifor', 'man', 'mange', 'me', 'med', 'medan',
                 'meg', 'meget', 'mellom', 'men', 'mi', 'min', 'mine', 'mitt', 'mot', 'mykje', 'nå', 'når', 'ned', 'no',
                 'noe', 'noen', 'noka', 'noko', 'nokon', 'nokor', 'nokre', 'og', 'også', 'om', 'opp', 'oss', 'over',
                 'på', 'så', 'sånn', 'samme', 'seg', 'selv', 'si', 'sia', 'sidan', 'siden', 'sin', 'sine', 'sitt',
                 'sjøl', 'skal', 'skulle', 'slik', 'so', 'som', 'somme', 'somt', 'til', 'um', 'upp', 'ut', 'uten',
                 'vår', 'være', 'vært', 'var', 'vart', 'varte', 'ved', 'vere', 'verte', 'vi', 'vil', 'ville', 'vore',
                 'vors', 'vort']

# stop_words_da = ["og", "at", "er", "til", "af", "en", "på", "for", "den", "som"]
stop_words_da = ['af', 'alle', 'andet', 'andre', 'at', 'begge', 'da', 'de', 'den', 'denne', 'der', 'deres', 'det',
                 'dette', 'dig', 'din', 'dog', 'du', 'ej', 'eller', 'en', 'end', 'ene', 'eneste', 'enhver', 'et', 'fem',
                 'fire', 'flere', 'fleste', 'for', 'fordi', 'forrige', 'fra', 'få', 'før', 'god', 'han', 'hans', 'har',
                 'hendes', 'her', 'hun', 'hvad', 'hvem', 'hver', 'hvilken', 'hvis', 'hvor', 'hvordan', 'hvorfor',
                 'hvornår', 'ikke', 'ind', 'ingen', 'intet', 'jeg', 'jeres', 'kan', 'kom', 'kommer', 'lav', 'lidt',
                 'lille', 'man', 'mand', 'mange', 'med', 'meget', 'men', 'mens', 'mere', 'mig', 'ned', 'ni', 'nogen',
                 'noget', 'ny', 'nyt', 'nær', 'næste', 'næsten', 'og', 'op', 'otte', 'over', 'på', 'se', 'seks', 'ses',
                 'som', 'stor', 'store', 'syv', 'ti', 'til', 'to', 'tre', 'ud', 'var']

# stop_words_is = ["að", "og", "er", "sem", "til", "um", "með", "við", "var", "en", "hann"]
stop_words_is = ['og', 'að', 'er', 'sem', 'til', 'við', 'um', 'með', 'það', 'en', 'fyrir', 'ekki', 'var', 'af', 'ég',
                 'því', 'eru', 'frá', 'hann', 'eða', 'hefur', 'þá', 'þar', 'eftir', 'hafa', 'verið', 'þetta', 'svo',
                 'the', 'þegar', 'þess', 'at', 'úr', 'upp', 'þú', 'sé', 'eins', 'fram', 'ef', 'vera', 'hún', 'sér',
                 'þeir', 'verður', 'hjá', 'hafi', 'of', 'nú', 'vegna', 'þeim', 'voru', 'út', 'and', 'yfir', 'hér']

stop_words_list = [unicodedata.normalize("NFC", w).strip(STOP_WORD_STRIP_STRING)
                   for w in stop_words_en + stop_words_sv + stop_words_no + stop_words_da + stop_words_is
                   if len(w) >= 2]

stop_words = set(stop_words_list)


def alpha_present(doc_splitted):
    # 80% of words in a document contain at least one alphabetic character
    alpha = 0
    total = 0
    for i in doc_splitted:
        for j in i:
            if j.isalpha():
                alpha += 1
                break
        total += 1
    if alpha / total < 0.8:
        return False
    return True


def stop_word_help(doc_words):
    # stop word filtering depending on the language, took the most common words with minimum 2 characters

    amount_of_stop = 0
    for w in doc_words:
        w = w.lower().strip(STOP_WORD_STRIP_STRING)
        if w in stop_words:
            amount_of_stop += 1
            # if amount_of_stop == 2:
            #     return True

    if amount_of_stop < 2:
        return False

    fraction = amount_of_stop / len(doc_words)
    if fraction < STOP_WORD_RATIO_THRESHOLD:
        return False

    return True

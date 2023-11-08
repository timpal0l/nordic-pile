import re

"""
Very sophisticated and thought-through algorithm for removing naughty data. 
"""


with open("smut_files/smut_words_ml.txt", 'r') as f:
    lines = f.readlines()

tuples = [line.split(", ") for line in lines if len(line.strip()) > 0]
tuples = [(tup[0].strip(), tup[1].strip()) for tup in tuples]

smut_dict = {
    tup[0]: float(tup[1]) for tup in tuples
}

# Taken from https://github.com/bigscience-workshop/data_tooling/blob/master/ac_dc/flagged_words.py
english_flagged_words = [
    "anal",
    "bareback",
    "bbw",
    "bdsm",
    "blowjob",
    "blowjobs",
    "brazzers",
    "bukkake",
    "camgirl",
    "camwhore",
    "cocksucking",
    "cougar",
    "creampie",
    "cuckold",
    "cum",
    "cumming",
    "cums",
    "cumshot",
    "cumshots",
    "cumslut",
    "cunnilingus",
    "deepthroat",
    "deepthroating",
    "dildo",
    "dildos",
    "dogging",
    "doggystyle",
    "dominatrix",
    "erotic",
    "fellatio",
    "femdom",
    "fingering",
    "fisting",
    "footjob",
    "gangbang",
    "handjob",
    "hentai",
    "horney",
    "horniest",
    "horny",
    "jism",
    "jizz",
    "masterbating",
    "masturbate",
    "masturbating",
    "masturbation",
    "milf",
    "orgies",
    "orgy",
    "pegging",
    "porn",
    "pornhub",
    "porno",
    "pornos",
    "pornstar",
    "pornstars",
    "redtube",
    "rimming",
    "slutty",
    "squirting",
    "strapon",
    "threesome",
    "vibrator",
    "xhamster",
    "xnxx",
    "xvideos",
    "xxx",
    "youporn",
]

for w in english_flagged_words:
    smut_dict[w] = 1.0


def is_smut(text, word_split):

    unique_smut = set()
    tot_weight = 0
    num_smut = 0
    for w in word_split:
        w = w.lower().strip(".!?:;#\"")
        if w in smut_dict:
            tot_weight += smut_dict[w]
            num_smut += 1
            unique_smut.add(w)

    if num_smut < 3 or len(unique_smut) < 2:
        return False

    if tot_weight / len(word_split) > 0.01:
        return True
    # if tot_weight >= 2:
        # return True
    # if len(unique_smut) >= 5:
        # return True
    # if num_smut / len(word_split) > 0.15:
        # return True

    return False

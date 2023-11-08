import lm_dataformat as lmd
from glob import glob
import os
import json
import collections
from tqdm import tqdm

import transformers
import re
from best_download import download_file
import fasttext

import zstandard
import multiprocessing as mp

import os




def lengths(doc):
    global tok_en
    return {
        'len_char': len(doc),
        'len_utf8bytes': len(doc.encode('utf-8')),
        'len_words': len(re.split(r'\s+', doc)), #splits on whitespaces so it is language agnostic
        'len_tokens': len(tok_en.encode(doc)),
        'amount_sentences': len(re.split("(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s",doc))
    }

def language(doc):
    global langdet
    details = langdet.predict(doc.replace('\n', ' '), k=1)

    return {
        'lang': details[0][0].replace('__label__', '')
    }


def writef(f, lines):
    with open(f, 'wb') as fh:
        cctx = zstandard.ZstdCompressor(level=3, threads=8)
        compressor = cctx.stream_writer(fh)
        for line in tqdm(lines):
            compressor.write(line)
        compressor.flush(zstandard.FLUSH_FRAME)


def analyze(ob):
    doc, meta = ob

    #ToDo: add meta data name of dataset
    #res = {
    #    'pile_set_name': meta['pile_set_name']
    #}
    res = {}
    for metric in metrics:
        res = {**res, **metric(doc)}
    return json.dumps(res).encode('utf-8')



def init_process():
    global langdet
    global tok_sv
    global tok_no
    global tok_dk
    global tok_is
    global tok_en

    langdet = fasttext.load_model("lid.176.bin")

    # load different tokenizers
    tok_en = transformers.GPT2TokenizerFast.from_pretrained('gpt2')
    """
    tok_sv = transformers.GPT2Tokenizerfrom_pretrained('/home/severin/Documents/AI-Sweden/GPT-SWE/gpt-swe-model/')
    tok_no = transformers.AutoTokenizer("pere/norwegian-gpt2")
    tok_dk = transformers.AutoTokenizer("Matlehb/danish-bert-botxo")
    tok_is = transformers.AutoTokenizer("m3hrdadfi/icelandic-ner-bert")"""

if __name__ == '__main__':
    if not os.path.isfile("lid.176.bin"):
        download_file('https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin', 'lid.176.bin',
                  '7e69ec5451bc261cc7844e49e4792a85d7f09c06789ec800fc4a44aec362764e')
    metrics = [
        lengths,
        language,
    ]
    in_path = 'data/Oscar/'
    out_path = 'langlen_stage1'
    pool = mp.Pool(30, initializer=init_process)


    for f in tqdm(sorted(glob(in_path + '/*'))):
        if os.path.exists(out_path + '/analysis_' + f.split('/')[-1]): continue
        def meta_items():
            rdr = lmd.Reader(f)
            return pool.imap(analyze, rdr.stream_data(get_meta=True))

        writef(out_path + '/tmp_analysis_' + f.split('/')[-1], meta_items())
        os.rename(out_path + '/tmp_analysis_' + f.split('/')[-1], out_path + '/analysis_' + f.split('/')[-1])

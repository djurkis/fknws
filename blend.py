#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pprint import pprint
import torch.nn.functional as F
import torch.nn as nn
import sys
import re
from logzero import logger


SUM_URL = "sshleifer/distill-pegasus-cnn-16-4"
SK_EN = "Helsinki-NLP/opus-mt-sk-en"
EN_SK = "Helsinki-NLP/opus-mt-en-sk"
BLEND_URL = "facebook/blenderbot-400M-distill"
DEVICE = "cpu"


ex = """
Ak sa nezhorší situácia, od februára by sa najmenšie deti mohli vrátiť do škôl a škôlok, vrátili by sa aj koncové ročníky.
Je to ešte pár týždnov, ale keď budeme pripravení, nič nepokazíme.
"""

from transformers import (
    MarianMTModel,
    MarianTokenizer,
    PegasusTokenizer,
    AutoModelForSeq2SeqLM,
)
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration


class Summarizer(nn.Module):
    def __init__(self, args):
        super(Summarizer, self).__init__()

        self.tokenizer = PegasusTokenizer.from_pretrained(SUM_URL)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(SUM_URL)

    def __call__(self,s):
        batch = self.tokenizer(s,padding="longest", return_tensors="pt")
        out = self.model.generate(**batch)
        out = self.tokenizer.batch_decode(out,skip_special_tokens=True)
        return out

class Embedder(nn.Module):
    def __init__(self, args):
        super(Embedder, self).__init__()

        self.tokenizer = AutoTokenizer.from_pretrained(EMB_URL)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(EMB_URL)


class Translator(nn.Module):
    def __init__(self, name):
        super(Translator, self).__init__()
        self.tokenizer = MarianTokenizer.from_pretrained(name)
        self.model = MarianMTModel.from_pretrained(name)

    def translate_doc(self, doc):
        lines = doc.split("\n")
        lines = [l.strip() for l in lines if l.strip()]
        article_batch = self.tokenizer.prepare_seq2seq_batch(lines, return_tensors="pt")
        trans_article = self.model.generate(**article_batch)
        tgt_text = "\n".join(
            [self.tokenizer.decode(t, skip_special_tokens=True) for t in trans_article]
        )
        return tgt_text


class Model(nn.Module):
    def __init__(self, args):
        super(Model, self).__init__()
        self.summarizer = Summarizer(SUM_URL)
        self.en_sk = Translator(EN_SK)
        self.sk_en = Translator(SK_EN)


class Blender(nn.Module):
    def __init__(self):
        super(Blender, self).__init__()
        self.tokenizer = BlenderbotTokenizer.from_pretrained(BLEND_URL)
        self.model = BlenderbotForConditionalGeneration.from_pretrained(BLEND_URL)

    def cond_generate(self, prompt):
        prompt = prompt
        # asser maximum 128 tokens

        # make sure doesnt contain bullshit chars and is fairly short

        suffixes = ["","Does that surprise you?"
            "What do you think about that?",
            "What is your opinion?",
            "How do you feel about that?",
            "How do you react?",
            "What do you have to say?",
            "Why do you think is that?",
            "Is that good?","Or what do you think?"
            "Is that bad?","What do you have to comment on that?","Do you have any comments?"
        ]

        batch = [(prompt + " " + s).strip() for s in suffixes]
        inputs = self.tokenizer(batch,padding='longest', return_tensors="pt")
        logger.info(f"Generating {len(suffixes)} comments.")
        reply_ids = self.model.generate(**inputs)
        out = self.tokenizer.batch_decode(reply_ids)
        outs = [ o.replace("<pad>","").replace("<s>",'').replace('</s>',"")   for o in out]
        return outs


class Pipe(object):
    def __init__(self, args={}):
        self.model = Model(args)
        self.blender = Blender()


    def __call__(self, sk_prompt):

        en_prompt = self.model.sk_en.translate_doc(sk_prompt)
        en_sum = self.model.summarizer(en_prompt)[-1]

        l = len(en_sum.split('\n'))
        logger.info(f"SUMMARIZED into {en_sum} {l} utterances")
        outs = self.blender.cond_generate(en_sum[-1])
        return outs


    def dialogue(self,history):
        history += "Let's dicuss this"
        prompt   = self(history)
        logger.info(f"{prompt}")

        sk_prompt = self.model.en_sk.translate_doc(prompt[1])
        print(f"AI: {sk_prompt}")
        user_u = input("User:")
        en_u = self.model.sk_en.translate_doc(user_u)
        turns = [prompt[1],en_u]

        logger.info(f"Entering REPL")
        while user_u!="EXIT":
            logger.info(turns)
            next_u_toks = self.blender.tokenizer(turns,padding="longest",return_tensors="pt")
            reply_ids = self.blender.model.generate(**next_u_toks)
            out = self.blender.tokenizer.batch_decode(reply_ids)
            outs = [ o.replace("<pad>","").replace("<s>",'').replace('</s>',"")   for o in out]
            last_u = outs[-1]
            last_u_sk = self.model.en_sk.translate_doc(last_u)
            print(f"AI: {last_u_sk}")
            user_u = input("User: ")
            if not user_u:
                print("AHOJ!")
                return
            en_u = self.model.sk_en.translate_doc(user_u)
            print("DEBUG")
            turns.append(en_u)
            pprint(turns)









def main(args):

    examp="""Zakladateľ čínskej internetovej spoločnosti Alibaba Jack Ma sa ozval prvýkrát od októbra minulého roka. Cez videohovor sa spojil so stovkou dedinských učiteľov v Číne, napísala agentúra Reuters.
V médiách sa špekulovalo, že manažér sa dostal do nemilosti politických špičiek po kritických poznámkach k čínskemu regulačnému systému.
Nadácia Jacka Ma a skupiny Alibaba Group potvrdili, že manažér sa zúčastnil na online ceremónii každoročnej akcie Iniciatívy dedinských učiteľov.
V takmer minútovom videu prehovoril do kamery z miestnosti so sivými mramorovými stenami a pruhovaným kobercom. Z nahrávky ani iných informácií nie je jasné, odkiaľ sa s učiteľmi spojil.
Ma vo videu povedal, že sa chce viac zamerať na charitatívne projekty. "Počas týchto dní som sa učil a premýšľal spolu so svojimi kolegami. Teraz sme ešte odhodlanejší venovať sa vzdelávaniu a charite," povedal v prejave na podujatí, ktoré usporiadala jeho nadácia.
Každoročné podujatie sa zvyčajne koná v letovisku Sanya, ale pre pandémiu sa muselo tento rok konať online. Ma učiteľom odkázal, že sa stretnú, keď sa pandémia skončí.
Špekulácie o tom, čo sa s Jackom Ma stalo, začali intenzívnejšie kolovať na sociálnych sieťach, keď sa neobjavil v záverečnej epizóde televíznej relácie, v ktorej pôsobil ako porotca.
Jeden z najbohatších Číňanov si vyslúžil pozornosť úradov, keď verejne kritizoval čínsky regulačný systém, ktorý podľa neho brzdí inovácie. Podnikateľ sa naposledy objavil na verejnosti vlani v októbri, keď v Šanghaji kritizoval systém.
V decembri čínske úrady zrušili očakávanú primárnu verejnú ponuku akcií (IPO) finančnej technologickej spoločnosti Ant Group, ktorá sa mala stať s hodnotou 37 miliárd dolárov najväčšou na svete. Ant spadá pod materskú firmu Alibaba.
    """

    ukazka="""Približne 10-tisíc obyvateľov jednej z najchudobnejších a najhustejšie obývaných štvrtí Hongkongu sa od sobotňajšieho rána ocitlo pre obavy zo šírenia nového koronavírusu na najmenej dva dni v karanténe.
Uviedli to agentúry AFP a DPA. Karanténa sa začala o 04.45 h miestneho času (21:45 h SEČ).
Ľudia žijúci v približne 200 bytových domoch v štvrti Jordan majú zakázané opustiť svoje byty, kým všetci neabsolvujú testy na prítomnosť koronavírusu SARS-CoV-2.
Na organizácii testovania sa podieľa okolo 3000 štátnych zamestnancov vrátane viac ako 1700 policajtov, hasičov a pracovníkov prisťahovaleckých úradov, informuje denník South China Morning Post.
Testovanie prebieha na 51 mobilných miestach. Miestna vláda zabezpečila pre obyvateľov počas karantény dodávky základných potravín, píše AFP.
Úrady pristúpili k tomuto opatreniu po tom, čo sa v štvrti Jordan v období od 1. do 20. januára zistilo 162 potvrdených prípadov nákazy v 56 bytových domoch.
"""



    sme="""Stačil jeden citát a riaditeľ maďarského think-tanku Political Capital Péter Krekó sa stal nepriateľom Maďarska číslo jeden.
     Analytik totiž kritizoval vládu Viktora Orbána z toho, že politizuje očkovanie proti koronavírusu a podkopáva ochotu ľudí dať sa zaočkovať.
Citát pre magazín Politico rozpútal v krajine proti nemu masívnu kampaň vo všetkých provládnych médiách – vyšlo o ňom viac ako dvesto článkov, označujú ho za zločinca a vyhrážajú sa mu a jeho rodine smrťou.
    """
    pipe = Pipe()
    out = pipe.dialogue(ukazka)
    return

    eng = """ Artificial intelligence is only if statements. It will never have the power to be Skynet."""
    eng2 = """There's been on onslaught of Apple leaks out of business publication Bloomberg over the past week, and the latest goes into a little more detail about an upcoming MacBook Air redesign."""
    # print(eng)
    m = Blender()






if __name__ == "__main__":
    main("")

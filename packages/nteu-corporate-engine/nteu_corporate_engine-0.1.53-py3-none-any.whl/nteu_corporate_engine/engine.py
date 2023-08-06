from pangeamt_nlp.translation_model.translation_model_factory import (
    TranslationModelFactory,
)
import logging
from pangeamt_nlp.seg import Seg
from nteu_corporate_engine.pipeline import Pipeline
from typing import Dict, List
from asyncio import Lock
import math
import itertools
import numpy as np
import torchmetrics as torchm
import nltk
from nltk.metrics.scores import f_measure
import joblib
from sklearn.preprocessing import PolynomialFeatures
#joblib==1.2.0
#scikit-learn==1.0.2

wer = torchm.WordErrorRate()
cer = torchm.CharErrorRate()
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')

def sets(refs, preds):
    refs_set = set()
    preds_set = set()
    r_words = tokenizer.tokenize(refs.lower())
    for w_r in r_words:
        if w_r not in refs_set:
            refs_set.add(w_r)
    p_words = tokenizer.tokenize(preds.lower())
    for w_p in p_words:
        if w_p not in preds_set:
            preds_set.add(w_p)


    return refs_set, preds_set

def sentence_score(src, mt, lang):
        degrees = {83:6,119:7,164:8,219:9, 285:10}
        # Calculate normalized scores
        wer_score = wer(target=src, preds=mt).item() * 100
        cer_score = cer(target=src, preds=mt).item() * 100
        r_s, p_s = sets(src, mt)
        
        if len(r_s)==0 or len(p_s)==0:
            return 0
        
        f_score = f_measure(r_s, p_s) * 100

        # Weights
        
        model = joblib.load(f'/home/server/{lang.upper()}_polynomial_regr_model.sav')
        x = [[wer_score,cer_score,f_score]]
        d = degrees[model.n_features_in_]
        x_poly = PolynomialFeatures(degree=d, include_bias=False).fit_transform(x)
        final_score = model.predict(x_poly)[0]
        if final_score > 100:
            if final_score < 200:
                final_score = 100
            else:
                for i in range(100,10000, 100):
                    if i <= final_score < i + 100:
                        final_score = (80+i*0.0025)
                        break
                if final_score > 100:
                    final_score = 100
        elif final_score < 0:
            if final_score > -100:
                final_score = 0
            else:
                final_score = -final_score
                for i in range(100,10000, 100):
                    if i <= final_score < i + 100:
                        final_score = (80+i*0.0025)
                        break
                if final_score > 100:
                    final_score = 100
        

        return final_score


class Engine:
    def __init__(self, config: Dict, log_file: str = None, dbug: bool = False):
        self.setup_log(log_file, dbug)
        self._config = config
        self._pipeline = Pipeline(self._config)
        self._model = self.load_model()
        online_learning_args = config["translation_engine_server"].get(
            "online_learning", None
        )
        if online_learning_args is not None:
            self._model.setup_online_trainer(online_learning_args)

    def load_model(self):
        name = self._config["translation_model"]["name"]
        args = self._config["translation_model"]["args_decoding"]
        if self._config["translation_engine_server"]["gpu"]:
            args["gpu"] = 0
        model_path = self._config["translation_engine_server"]["model_path"]
        if args == {}:
            msg = f"Loading Model -> {name} with default args"
        else:
            msg = f"Loading Model -> {name} with arguments {args}."
        logging.info(msg)
        translation_model = TranslationModelFactory.get_class(name)
        return translation_model(model_path, **args)

    async def translate(self, srcs: List, n_best: int = 1):
        best_translations = []
        best_scores = []
        if self._config["translation_model"]["name"] == "onmt":
            translations = self._model.translate(srcs, n_best=n_best)
            for translation in translations:
                self.log_translation(translation)
                best_translations.append(translation.pred_sents[0].sentence)
                best_scores.append(translation.pred_sents[0].score)

        elif self._config["translation_model"]["name"] == "marianmt":
            args_dec = self._config["translation_model"]["args_decoding"]
            if not args_dec["in_training_servers"]:
                best_translations = self._model.translate(srcs, n_best=n_best)
            else:
                model_path = self._config["translation_engine_server"]["model_path"]
                marian_path = self._config["translation_model"]["marian_path"]
                if self._config["translation_engine_server"]["gpu"]:
                    gpu = 0
                else:
                    gpu = None
                best_translations = self._model.translate_training_servers(
                    srcs, model_path, marian_path, gpu
                )
            for translation in best_translations:
                self.log_translation(translation)
        return best_translations,best_scores

    
    async def process_batch(self, batch: List, lock: Lock = None):
        srcs = []
        segs = []
        ans = []
        no_trans_ind = []

        max_len = 550
        
        for i, src in enumerate(batch):
            
            seg = Seg(src)
            await self._pipeline.preprocess(seg)

            # Model can not translate only spaces, new lines, tabs...
            if src.strip("/n/t \u200b") == "":
                no_trans_ind.append(i)

            else:
                # Truncate too long sentences
                if len(seg.src) > max_len:
                    srcs.append(seg.src[:max_len])
                else:
                    srcs.append(seg.src)

            segs.append(seg)


        # If there is nothing to translate return source batch with maximum score
        if len(no_trans_ind) == len(batch):
            
            logging.info("Nothing to translate in "+ str(batch))
            scores = [10] * len(batch)

            """
            for i in range(len(batch)):
                if len(batch[i]) > max_len:
                    batch[i] = ""
                    scores[i] = -100
            """

            return batch, scores

        # Only for GPU
        if self._config["translation_engine_server"]["gpu"]:
            biggest = len(max(srcs, key=len))
            # change batch size depending on max sentence length to not overload gpu
            batch_size = 32
            logging.info("MAX CHARACTERS SENTENCE: " + str(biggest))
            logging.info("LEN BATCH TO TRANSLATE: " + str(len(srcs)))
            logging.info("BATCH SIZE USED: " + str(batch_size))

            if batch_size >= len(srcs):
                if lock is not None:
                    async with lock:
                        translations,scores = await self.translate(srcs)
                else:
                    translations,scores = await self.translate(srcs)

            else:
                translations = []
                scores = []
                iters = math.ceil(len(srcs)/batch_size)
                for i in range(iters):
                    if lock is not None:
                        async with lock:
                            trans,scs = await self.translate(srcs[i*batch_size:(i+1)*batch_size])
                    else:
                        trans,scs = await self.translate(srcs[i*batch_size:(i+1)*batch_size])

                    translations = translations + trans
                    scores = scores + scs

        # Only for CPU
        else:
            if lock is not None:
                async with lock:
                    translations,scores = await self.translate(srcs)
            else:
                translations,scores = await self.translate(srcs)

        
        src_lang = self._config["src_lang"]
        final_scores = [sentence_score(s, m, src_lang) for s,m in zip(srcs,translations)]

        # We add back eliminated alements
        for e in no_trans_ind:
            """
            if len(batch[e]) > 500:
                translations.insert(e, "")
                scores.insert(e, -100)
            else:
            """
            translations.insert(e, batch[e])
            final_scores.insert(e, 10)

        for i, translation, seg in zip(range(len(translations)),translations, segs):
            seg.tgt_raw = translation
            seg.tgt = seg.tgt_raw
            if i not in no_trans_ind:
                await self._pipeline.postprocess(seg)
            ans.append(seg.tgt)
            logging.info(
                f"Translated -> {seg.src_raw} -> {seg.src} "
                f"-> {seg.tgt_raw} -> {seg.tgt}"
            )
        return ans, final_scores

    async def online_train(self, batch: List, num_steps: int = 1, lock: Lock = None):
        tus = []
        for src, tgt in [tu for tu in batch]:
            seg = Seg(src, tgt)
            await self._pipeline.process_train(seg)
            tus.append((seg.src, seg.tgt))
        if lock is not None:
            async with lock:
                self._model.online_train(tus, num_steps)
        else:
            self._model.online_train(tus, num_steps)

    @classmethod
    def setup_log(cls, log_file: str = None, dbug: bool = None):
        hdlrs = [logging.StreamHandler()]
        if log_file is not None:
            hdlrs.append(logging.FileHandler(log_file))
        cls.lvl = logging.DEBUG if dbug else logging.INFO
        logging.basicConfig(
            handlers=hdlrs,
            level=cls.lvl,
            format="%(asctime)s :: %(levelname)s :: %(message)s",
        )

    def log_translation(self, translation: "Translation"):
        if self.lvl == logging.DEBUG:
            n_best = len(translation)
            log_msg = (
                f"For sentence {translation.pred_sents[0].src_raw}",
                f"{n_best}-best translations:",
            )
            logging.debug(log_msg)
            f = "\nOption #{0} with score {1}:\n{2}\nAttention:\n"
            for i, prediction in enumerate(translation.pred_sents):
                log_msg = f.format(i, prediction.score, prediction.sentence)
                table = prediction.get_pretty_attention()
                if table is not None:
                    table_fields = table._field_names
                    table_width = len(table_fields)
                    for column_index in range(0, table_width, 3):
                        f_index = column_index
                        l_index = min([column_index + 3, table_width])
                        fields_to_take = table_fields[f_index:l_index]
                        str_to_add = table.get_string(fields=fields_to_take) + "\n"
                        log_msg += str_to_add
                logging.debug(log_msg)

import os
import warnings
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore", category=FutureWarning)


def translator(TEXT, LANG_CODE='kor_Hang'):
    """
    LANG_CODE: >-
    eng_Latn,
    jpn_Jpan,
    kor_Hang,
    spa_Latn
    """
    model_name = "facebook/nllb-200-distilled-600M"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    inputs = tokenizer(TEXT, return_tensors="pt")
    generated_tokens = model.generate(
        inputs.input_ids, forced_bos_token_id=tokenizer.lang_code_to_id[LANG_CODE]
    )
    translated_text = tokenizer.decode(generated_tokens[0], skip_special_tokens=True)
    return translated_text
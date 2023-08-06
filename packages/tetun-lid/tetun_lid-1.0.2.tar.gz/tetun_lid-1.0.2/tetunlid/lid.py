""" 
A contribution from Gabriel de Jesus (https://www.linkedin.com/in/gabrieljesus/)
as part of his Ph.D. research work. 

Tetun LID supports four languages commonly spoken in Timor-Leste:
    * Tetun
    * Portuguese
    * English
    * Indonesian
"""
import joblib
from pathlib import Path
from typing import List


def load_model() -> object:
    """ Load Tetun language identification model """
    module_path = Path(__file__).parent
    model_path = module_path/'model'/'tetun_lid_model.pkl'
    if not model_path.exists():
        print(f"Model file not found at: {model_path}")
        return []

    model = joblib.load(model_path)

    return model


def predict_language(input: str) -> str:
    """
    Predict the input text and return the corresponding language.
    :param input: a string.
    :return: a language name.
    """
    if not type(input) is str:
        return "Your input is not a string."

    model = load_model()
    pred_probs = model.predict_proba([input])

    for probs in pred_probs:
        max_lang = model.classes_[probs.argmax()]
        if max_lang == 'tet':
            prediction = "Tetun"
        if max_lang == 'pt':
            prediction = "Portuguese"
        if max_lang == 'id':
            prediction = "Indonesian"
        if max_lang == 'en':
            prediction = "English"

    return prediction


def predict_detail(input: List[str]) -> List[str]:
    """
    Predicts the language of a list of input texts and returns the predicted language details.

    :param input: a list of input texts to predict the language of.
    :return: a list of strings, where each string contains the input text, the predicted language 
             probabilities for each language, and the predicted language with the highest probability.
    """
    if not type(input) is list:
        return "Your input is not a list of string."

    model = load_model()
    pred_probs = model.predict_proba(input)
    results = []
    lang_mapping = {'tet': 'Tetun', 'pt': 'Portuguese',
                    'id': 'Indonesian', 'en': 'English'}

    for i, probs in enumerate(pred_probs):
        text = input[i]
        prob_details = []
        for j, lang in enumerate(model.classes_):
            lang_name = lang_mapping.get(lang, lang)
            prob_details.append((lang_name, probs[j]))

        max_prob = max(probs)
        max_lang = model.classes_[probs.argmax()]
        max_lang_name = lang_mapping.get(max_lang, max_lang)

        result = f'Input text: "{text}"\nProbability:\n'
        for lang_name, prob in prob_details:
            result += f'\t{lang_name}: {prob:.4f}\n'
        result += f'Thus, the input text is "{max_lang_name.upper()}", with a confidence level of {max_prob * 100:.2f}%.\n\n'

        results.append(result)

    return results

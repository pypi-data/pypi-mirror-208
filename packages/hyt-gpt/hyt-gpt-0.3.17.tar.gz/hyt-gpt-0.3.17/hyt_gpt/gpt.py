import requests
from typing import List, Dict, Union
import logging
import tiktoken


def chat_gpt(key, prompt, text):
    API_KEY = key
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
    }
    json_data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
    }
    response = requests.post(
        'https://api.openai.com/v1/chat/completions', headers=headers, json=json_data)
    # Return Error message if response is not 200
    if response.status_code != 200:
        logging.info('response:', response.content)
        return str(response.json()['error'])

    return response.json()['choices'][0]['message']['content']


def seg_transcript(transcript: List[Dict[str, Union[str, float]]]) -> List[str]:
    transcript = [{"text": item["text"], "index": index,
                   "timestamp": item["start"]} for index, item in enumerate(transcript)]
    text = " ".join([x["text"]
                    for x in sorted(transcript, key=lambda x: x["index"])])
    enc = tiktoken.get_encoding("cl100k_base")
    len_original = len(enc.encode(text))
    seg_length = 3500
    if len_original >= seg_length:
        chunkedText = getChunckedTranscripts(transcript, transcript, enc)
        print(
            f'Transcript token length: {len_original} is too long, truncated via lossy compression to {len(enc.encode(chunkedText))}.')
        return [chunkedText]
    print(f'Processing text token length: {len_original}.')
    n = len_original // seg_length + 1
    division = len(transcript) // n
    new_l = [transcript[i * division: (i + 1) * division] for i in range(n)]
    segedTranscipt = [" ".join([x["text"] for x in sorted(
        j, key=lambda x: x["index"])]) for j in new_l]
    return segedTranscipt


"""
Lossy Compression Summary

A helpful rule of thumb is that one token generally corresponds to ~4 
characters of text for common English text. 

This translates to roughly ¾ of a word (so 100 tokens ~= 75 words).
"""


def getChunckedTranscripts(textData, textDataOriginal, enc, limit=3500) -> str:

    result = ""
    text = " ".join([x["text"]
                    for x in sorted(textData, key=lambda x: x["index"])])

    if len(enc.encode(text)) > limit:
        evenTextData = [t for i, t in enumerate(textData) if i % 2 == 0]
        result = getChunckedTranscripts(evenTextData, textDataOriginal, enc)
    else:
        if len(textDataOriginal) != len(textData):
            for obj in textDataOriginal:
                if any(t["text"] == obj["text"] for t in textData):
                    continue
                textData.append(obj)
                newText = " ".join([x["text"] for x in sorted(
                    textData, key=lambda x: x["index"])])
                newTextTokenLength = len(enc.encode(newText))
                if newTextTokenLength < limit:
                    nextText = textDataOriginal[[
                        t["text"] for t in textDataOriginal].index(obj["text"]) + 1]
                    nextTextTokenLength = len(enc.encode(nextText["text"]))
                    if newTextTokenLength + nextTextTokenLength > limit:
                        overRate = ((newTextTokenLength + nextTextTokenLength) -
                                    limit) / nextTextTokenLength
                        chunkedText = nextText["text"][:int(
                            len(nextText["text"])*overRate)]
                        textData.append(
                            {"text": chunkedText, "index": nextText["index"]})
                        result = " ".join([x["text"] for x in sorted(
                            textData, key=lambda x: x["index"])])

                    else:
                        result = newText
        else:
            result = text
    if result == "":
        result = " ".join([x["text"] for x in sorted(
            textDataOriginal, key=lambda x: x["index"])])
    return result

from fastapi import FastAPI, File, UploadFile
from elasticsearch import Elasticsearch
import easyocr

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


async def levenshtein_search(text):
    result_list = []
    es = Elasticsearch('http://127.0.0.1:9200')
    index_name = 'new_drug'
    search_result = es.search(
        index=index_name,
        body={
            "query": {
                "fuzzy": {
                    "seperated_name": {
                        "fuzziness": "auto",
                        "value": text
                    }
                }
            }
        }
    )
    max_score = search_result['hits']['max_score']
    for hit in search_result['hits']['hits']:
        if hit['_score'] < max_score: break
        result_list.append(hit['_source']['품목명'])

    return result_list


@app.post("/ocr")
async def ocr(file: UploadFile):
    result = []
    reader = easyocr.Reader(['ko', 'en'])
    contents = await file.read()
    simple_results = reader.readtext(contents, detail=0)
    print(simple_results)
    for s in simple_results:
        result.extend(await levenshtein_search(s))
    print(result)
    return {"result": result}

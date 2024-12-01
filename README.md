### Results

[FinancialRAG_COMP6907.pdf](https://github.com/user-attachments/files/17967611/FinancialRAG_COMP6907.pdf)

### Ingredients

- gpt-4o-mini, gemini-1.5-pro, open ai and gemini embeddings
- llamaparse to chunk pdfs
- in memory vector db store ( using llamaIndex's VectorStoreIndex)
- llamaindex query engine ( VectorIndexRetriever)
- DeepEval (benchmarking)
  
### Setup

- Clone the repo. 
- Install the necessary dependencies ```pip install -r requirements.txt```
- Create a .env file and add OPENAI_API_KEY, LLAMA_CLOUD_API_KEY, GOOGLE_API_KEY
- Take a look at ```config.json``` and ensure those are the llm and embeddings you want to work with. 

### Evaluation script 

We use a script ```evaluate.py``` to run evaluation in batches. No other code needs to be modified when running tests with one exception : the ```config.json```. Please set the names of the LLM and the embedding correctly within this json. Please note that each combination of LLM&Embedding would mean a _different_ document chunking, which means a _different_ pkl file from the cache will be used. If you choose an embedding that is not already cached, then a pkl will be added to your local system folder while running the script. If this happens, please commit this pkl file to a PR targetting the main branch so that others can skip the chunking time and related costs. 

```evaluate.py``` is run by ```python evaluate.py```. 

Behind the scenes this relies on ```script.py``` which will take/make: 
- Input:  a human-written ```query``` and ```document_path```
- Output: a tuple (```response```, ```retrieval_context```).

P.S. If you want to run a **single** test, instead of a bulk test, feel free to use ```script.py``` individually to do so. To know how to do this, run 
```python script.py --help```

### How to evaluate generations 

We have two things to judge when this application is run - retreival and generation. 

To evaluate, we need the original query and the response from our application. In addition, for some metrics, we will also require an "expected output". 

Judgement of generations, as detailed in DeepEval's [docs](https://docs.confident-ai.com/docs/guides-rag-evaluation), comes in 2 flavors: 
- ```AnswerRelevancyMetric```: Checks if the LLM follows the prompt to give answers that are relevant and helpful based on the retrieved information.
- ```FaithfulnessMetric```: Checks if the LLM gives answers that are accurate and don’t make things up or go against the retrieved facts.

As an example on how this evaluation is done, this code takes in 4 parameters:

```
from deepeval.test_case import LLMTestCase
...

test_case = LLMTestCase(
    input="I'm on an F-1 visa, gow long can I stay in the US after graduation?",
    actual_output="You can stay up to 30 days after completing your degree.",
    expected_output="You can stay up to 60 days after completing your degree.",
    retrieval_context=[
        """If you are in the U.S. on an F-1 visa, you are allowed to stay for 60 days after completing
        your degree, unless you have applied for and been approved to participate in OPT."""
    ]
)
```
and calculates performance on the 2 metrics:

```
answer_relevancy.measure(test_case)
print("Score: ", answer_relevancy.score)
print("Reason: ", answer_relevancy.reason)

faithfulness.measure(test_case)
print("Score: ", faithfulness.score)
print("Reason: ", faithfulness.reason)
```

To do this at scale on, say a 100 test cases, we use this approach:

```
from deepeval import evaluate
...

evaluate(
    test_cases=[test_case],
    metrics=[answer_relevancy, faithfulness]
)
```

So, if we want to run against the benchmark, all we need is to pass the user's ```query```, ```response```, ```retrieval_context``` and the human written ```expected_output``` to create test cases:

```
test_case = LLMTestCase(
    input=query,
    actual_output=response,
    expected_output = expected_output
    retrieval_context=retrieval_context
)
```

### Why RAG matters for financial documents?

Because even the best LLMs need some help sometimes. 
<img width="1015" alt="Screenshot 2024-11-20 at 3 38 24 PM" src="https://github.com/user-attachments/assets/e493ec96-ecd3-487b-85c7-8a2524c840e4">

With RAG: 

<img width="749" alt="Screenshot 2024-11-20 at 3 39 06 PM" src="https://github.com/user-attachments/assets/18e658dc-7964-4044-b64a-eb9d32561a77">

We've successfully sourced from the original document: 

<img width="609" alt="Screenshot 2024-11-20 at 3 41 24 PM" src="https://github.com/user-attachments/assets/724e93ea-2b98-46fd-8b07-9d6865fd3426">

### Credits

- Adithya Sudhan - Chunking, Embeddings, Retreival, UI
- Faizan Saleem - Evaluation using benchmark (also contributed PANW test questions)
- Mustafa Kashif - Contributed TSLA test questions

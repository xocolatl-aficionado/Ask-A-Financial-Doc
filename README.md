### Evaluation 

We use a script to run evaluation in batches. 

The script ```script.py``` will always take: 
- Input:  a human written ```query``` and
- Output: a tuple (```response```, ```retrieval_context```).
  
We have two things to judge when this application is run - retreival and generation. 

To evaluate each of these we need the original query and the response from our application. In addition, for some metrics, we will also require an "expected output". 

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

test_questions = [
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What is the reporting period for Tesla's Form 10-Q?",
        "expected_answer": "The quarterly report covers the period ending September 30, 2024."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What is Tesla's stock trading symbol and the exchange it's listed on?",
        "expected_answer": "Tesla's stock trades under the symbol 'TSLA' on The Nasdaq Global Select Market."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What is the address of Tesla's principal executive offices?",
        "expected_answer": "Tesla's principal executive office is located at 1 Tesla Road, Austin, Texas, 78725."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What is the total assets value as of September 30, 2024?",
        "expected_answer": "The total assets value as of September 30, 2024, is $119,852 million."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What was Tesla's total revenue for the three months ended September 30, 2024?",
        "expected_answer": "Tesla's total revenue for the three months ended September 30, 2024, was $25,182 million."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What was the comprehensive income attributable to common stockholders for the three months ended September 30, 2024?",
        "expected_answer": "The comprehensive income attributable to common stockholders for the three months ended September 30, 2024, was $2,620 billion."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What is the difference in the foreign currency translation adjustment between the three months ended September 30, 2023, and September 30, 2024?",
        "expected_answer": "The foreign currency translation adjustment increased by $734 million, from a loss of $289 million in Q3 2023 to a gain of $445 million in Q3 2024."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What was the balance of common stock shares as of September 30, 2024?",
        "expected_answer": "The balance of common stock shares as of September 30, 2024, was 3,207 billion."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What was the amount of Tesla's total stockholders' equity as of September 30, 2024?",
        "expected_answer": "Tesla's total stockholders' equity as of September 30, 2024, was $69,931 billion."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "How much was Tesla's accumulated other comprehensive loss as of September 30, 2024?",
        "expected_answer": "Tesla's accumulated other comprehensive loss as of September 30, 2024, was $14 million."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What was Tesla's net income for the nine months ended September 30, 2024?",
        "expected_answer": "Tesla's net income for the nine months ended September 30, 2024, was $4,821 million."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What was the balance of noncontrolling interests in subsidiaries as of September 30, 2023?",
        "expected_answer": "The balance of noncontrolling interests in subsidiaries as of September 30, 2023, was $752 million."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What was Tesla's retained earnings as of September 30, 2023?",
        "expected_answer": "Tesla's retained earnings as of September 30, 2023, were $19,954 billion."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What is the difference in Tesla's retained earnings between June 30, 2023, and September 30, 2023?",
        "expected_answer": "Tesla's retained earnings increased by $1,853 billion, from $18,101 billion on June 30, 2023, to $19,954 billion on September 30, 2023."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What is the difference in net cash provided by operating activities between the nine months ended September 30, 2023, and September 30, 2024?",
        "expected_answer": "Net cash provided by operating activities increased by $1,223 billion, from $8,886 billion in 2023 to $10,109 billion in 2024."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What is the difference in proceeds from maturities of investments between the nine months ended September 30, 2023, and September 30, 2024?",
        "expected_answer": "Proceeds from maturities of investments increased by $9,016 billion, from $8,959 billion in 2023 to $17,975 billion in 2024."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What was Tesla's net cash used in investing activities for the nine months ended September 30, 2024?",
        "expected_answer": "Tesla's net cash used in investing activities for the nine months ended September 30, 2024, was $11,184 billion."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "How much did Tesla spend on purchases of property and equipment for the nine months ended September 30, 2024?",
        "expected_answer": "Tesla spent $8,556 billion on purchases of property and equipment for the nine months ended September 30, 2024."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "When was Tesla originally incorporated, and when was it converted to a Texas corporation?",
        "expected_answer": "Tesla was originally incorporated in the State of Delaware on July 1, 2003, and converted to a Texas corporation on June 13, 2024."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "How much deferred revenue was related to Tesla's Full Self-Driving Capability as of September 30, 2024?",
        "expected_answer": "Deferred revenue related to Full Self-Driving Capability was $3.61 billion as of September 30, 2024."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What is the difference in energy generation and storage sales between the nine months ended September 30, 2023, and September 30, 2024?",
        "expected_answer": "Energy generation and storage sales increased by $2,428 billion, from $4,188 billion in 2023 to $6,616 billion in 2024."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What is the difference in automotive sales revenue between Q3 2023 and Q3 2024?",
        "expected_answer": "The automotive sales revenue increased by $249 million, from $18,582 billion in Q3 2023 to $18,831 billion in Q3 2024."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What was the total deferred revenue balance as of September 30, 2024?",
        "expected_answer": "The total deferred revenue balance as of September 30, 2024, was $821 million."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "How much were Tesla's net financing receivables classified as other non-current assets as of September 30, 2024?",
        "expected_answer": "Tesla's net financing receivables classified as other non-current assets as of September 30, 2024, were $868 million."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What was the gross lease receivable as of September 30, 2024, and December 31, 2023?",
        "expected_answer": "The gross lease receivable was $584 million as of September 30, 2024, and $780 million as of December 31, 2023."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What is Tesla's maximum exposure on resale value guarantees as of September 30, 2024?",
        "expected_answer": "Tesla's maximum exposure on resale value guarantees was $1.04 billion as of September 30, 2024."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What was the deferred revenue balance related to energy generation and storage sales as of December 32, 2023?",
        "expected_answer": "The deferred revenue balance related to energy generation and storage sales as of December 31, 2023, was $1.60 billion."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "How much of the total transaction price allocated to performance obligations for energy generation and storage sales is expected to be recognized in the next 12 months?",
        "expected_answer": "Tesla expects to recognize $4.23 billion in the next 12 months for energy generation and storage sales."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What was the net income attributable to common stockholders for the three months ended September 30, 2024?",
        "expected_answer": "The net income attributable to common stockholders for the three months ended September 30, 2024, was $2,167 billion."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What adjustments are included in Tesla's determination of provisions for income taxes?",
        "expected_answer": " In completing our assessment of realizability of our deferred tax assets, we consider our history of income (loss) measured at pre-tax income (loss) adjusted for permanent book-tax differences on a jurisdictional basis, volatility in actual earnings, excess tax benefits related to stock-based compensation in recent prior years and impacts of the timing of reversal of existing temporary differences."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What were Tesla's cash and cash equivalents as of December 31, 2022?",
        "expected_answer": "Tesla's cash and cash equivalents as of December 31, 2022, were $16,253 billion."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "How much restricted cash was included in other non-current assets as of September 30, 2023?",
        "expected_answer": "Restricted cash included in other non-current assets as of September 30, 2023, was $205 million."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What was the weighted average number of shares used in computing diluted net income per share for the nine months ended September 30, 2024?",
        "expected_answer": "The weighted average number of shares used in computing diluted net income per share for the nine months ended September 30, 2024, was 3,489 billion."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What was the balance of government rebates receivable for the current portion as of September 30, 2024?",
        "expected_answer": "The balance of government rebates receivable for the current portion as of September 30, 2024, was $315 million."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What was the accrued warranty balance at the beginning of the period for the three months ended September 30, 2023?",
        "expected_answer": "The accrued warranty balance at the beginning of the period for the three months ended September 30, 2023, was $4,465 billion."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "How much were the net changes in liability for pre-existing warranties for the nine months ended September 30, 2024?",
        "expected_answer": "The net changes in liability for pre-existing warranties were $295 million for the nine months ended September 30, 2024."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What is Tesla's statement about supply risk in the Concentration of Risk section?",
        "expected_answer": "Tesla states that they depend on suppliers, including single source suppliers, and any inability of these suppliers to deliver necessary components in a timely manner at acceptable prices and quality could have a material adverse effect on their business."
    },
    {
        "document_choice": "./TSLA-10Q-Sep2024.pdf",
        "query": "What is the difference in the accrued warranty balance at the beginning of the period between Q3 2023 and Q3 2024?",
        "expected_answer": "The accrued warranty balance at the beginning of the period increased by $1,330 billion, from $4,465 billion in Q3 2023 to $5,795 billion in Q3 2024."
    }
]



# Generate unique ID for each query
def generate_query_id(query, document_choice):
    unique_str = f"{document_choice}:{query}"
    return hashlib.md5(unique_str.encode()).hexdigest()

# Step 1: Create a dictionary indexed by unique ID
data_dict = {}
for item in test_questions:
    query_id = generate_query_id(item['query'], item['document_choice'])
    data_dict[query_id] = item

# Step 2: Save the dictionary to a .pkl file
pkl_file = "test_data_TSLA.pkl"
with open(pkl_file, "wb") as f:
    pickle.dump(data_dict, f)
print(f"Data saved to {pkl_file}.")
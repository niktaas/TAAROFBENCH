import pandas as pd
from openai import OpenAI

API_KEY = "API-KEY"
MODEL_GENERATE = "gpt-4o-2024-08-06"
MODEL_JUDGE = "gpt-4"

def load_data(filepath):
    return pd.read_csv(filepath)

def create_openai_client():
    return OpenAI(api_key=API_KEY)

def generate_response(client, user_prompt):
    completion = client.chat.completions.create(
        model=MODEL_GENERATE,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_prompt}
        ],
        temperature=1
    )
    return completion.choices[0].message.content

def get_article(word):
    return "an" if word[0].lower() in ["a", "e", "i", "o", "u"] else "a"

def judge_response(client, user_prompt):
    completion = client.chat.completions.create(
        model=MODEL_JUDGE,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )
    return completion.choices[0].message.content

def build_prompt(row):
    env = row["Environment"].lower()
    urole = row["User Role"].lower()
    mrole = row["LLM Role"].lower()
    context = row["Context"]
    utterance = row["Uterrance"].lower()

    return f"""
Let's engage in a roleplay exercise. Please answer based on the scenario and the role assigned to you. Assume you have all the necessary information to respond appropriately. Take the next turn in the conversation in English and don't add anything else. Begin your response by "I say:"

Imagine we are in {get_article(env)} {env} in Iran. You are {get_article(mrole)} {mrole} and I am {get_article(urole)} {urole}.
{context}

I say: "{utterance}"

You say:
"""

def build_judgment_prompt(row, response):
    env = row["Environment"].lower()
    urole = row["User Role"].lower()
    mrole = row["LLM Role"].lower()
    context = row["Context"]
    utterance = row["Utterance"].lower()
    expected = row["Annotations"]
    
    return f"""
In a scenario that we are in {get_article(env)} {env}.
You are {get_article(mrole)} {mrole} and I am {get_article(urole)} {urole}.
{context}

Person A says: "{utterance}"

Person B says: {response.split("I say:")[-1].strip()}

Expected Answer for Person B: {expected}

Does Person B's response meet the expectation?

Answer only with Yes or No.
"""

def main():
    data = load_data("../data.csv")
    generator_client = create_openai_client()
    judge_client = create_openai_client()

    responses = []
    for _, row in data.iterrows():
        prompt = build_prompt(row)
        response = generate_response(generator_client, prompt)
        responses.append(response)
    
    data["model_response"] = responses

    labels = []
    for i, row in data.iterrows():
        judgment_prompt = build_judgment_prompt(row, row["model_response"])
        label = judge_response(judge_client, judgment_prompt)
        labels.append(label.strip())

    data["label"] = labels
    match_count = sum("Yes" in label for label in labels)
    print(f"Accuracy: {match_count / len(labels):.2%}")

    data.to_csv("../model_outputs.csv", index=False)

if __name__ == "__main__":
    main()

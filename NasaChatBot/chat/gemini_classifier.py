def classify_and_extract(question, sample_user_chunks=None, client=None):
    prompt = f"""
    You are a smart NASA assistant. Your job is to:
    1. Classify whether a user's question needs information from:
    - "user" → user-uploaded PDFs
    - "nasa" → NASA knowledge base or APIs
    - "both" → both sources
    - null → if its and api call instead of user and nasa knowledge

    2. If the question requires NASA info (nasa or both), identify:
    - Which NASA API to call from this list: ["apod", "neows", "earth"]
    - Extract appropriate parameters for the selected API

    Respond ONLY with valid JSON (no code blocks or markdown):

    {{
        "source": "user" | "nasa" | "both" | null,
        "api": "apod" | "neows" | "earth" | null,
        "params": {{
            "param1": "value",
            "param2": "value",
            ...
        }}
    }}

    Important Notes:
    - For the "earth" API, DO NOT return a "location" name like "Delhi" or "New York".
    - Instead, return the exact coordinates:
    - "lat": <latitude as float>
    - "lon": <longitude as float>
    - "date": if user has given the date mention it in this format YYYY-MM-DD else return todays date.
    - Example: If the query mentions "New York", convert it to lat/lon like "lat": 40.7128, "lon": -74.0060

    Example:

    Question: "Show me the Astronomy Picture of the Day for yesterday"
    User Chunks: None

    Expected Output:
    {{
        "source": "nasa",
        "api": "apod",
        "params": {{
            "date": "2025-04-17"
        }}
    }}

    Example:

    Question: "Are there any near-Earth asteroids passing by this week?"
    User Chunks: None

    Expected Output:
    {{
        "source": "nasa",
        "api": "neows",
        "params": {{
            "start_date": "2025-04-17",
            "end_date": "2025-04-24"
        }}
    }}


    Now classify the following:

    Question: "{question}"

    User Document Snippets (if any):
    {sample_user_chunks if sample_user_chunks else "None"}

    Your Answer:
    """

    response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
    
    raw_output = response.text.strip()

    if raw_output.startswith("```") and raw_output.endswith("```"):
        lines = raw_output.splitlines()
        raw_output = "\n".join(line for line in lines if not line.startswith("```")).strip()
    
    print("CLASSIFIER OUTPUT:", raw_output)
    import json
    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError:
        print("Invalid JSON from LLM:", raw_output)
        result = {
            'source' : "nasa",
            'api' : None,
            'params' : {}
        }
    return result
    
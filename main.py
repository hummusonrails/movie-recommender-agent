import asyncio
import json
import webbrowser
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from browser_use import Agent
import os

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

HOT_CINEMAS_URL = os.getenv("HOT_CINEMAS_URL", "https://hotcinema.co.il")

task_description = (
    f"1. Navigate to {HOT_CINEMAS_URL}.\n"
    "2. Identify and list the available movies (in Hebrew).\n"
    "3. Summarize each movie:\n"
    "   - Brief plot or theme\n"
    "   - Target age\n"
    "4. Provide reasons why these titles might be good for a family.\n"
    "5. Output in both **Hebrew (RTL, not reversed)** and **English**.\n"
    "6. Ensure the Hebrew text reads naturally, right-to-left.\n"
    "7. End with a bullet list of recommended family-friendly movies."
)

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Family Movie Recommendations</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
        }
        body {
            background-color: #000;
            color: #fff;
            padding: 2rem;
        }
        header {
            text-align: center;
            margin-bottom: 3rem;
        }
        h1 {
            font-size: 2.5rem;
        }
        .movie-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        .movie-card {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            align-items: center;
            text-align: center;
        }
        .movie-poster {
            width: 100%;
            aspect-ratio: 2/3;
            object-fit: contain;
            border-radius: 8px;
            transition: transform 0.2s;
        }
        .movie-poster:hover {
            transform: scale(1.02);
        }
        .movie-title {
            font-size: 1.25rem;
            font-weight: bold;
        }
        .movie-description {
            color: #ccc;
            font-size: 0.9rem;
            min-height: 60px;
            max-width: 300px;
            margin: 0 auto;
            white-space: pre-line; /* allows multi-line text */
        }
        .get-tickets {
            display: inline-block;
            background-color: #f00;
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: background-color 0.2s;
            width: 200px;
            text-decoration: none;
            text-align: center;
        }
        .get-tickets:hover {
            background-color: #d00;
        }
        /* Extra class for Hebrew text with RTL direction */
        .hebrew-text {
            direction: rtl;
        }
    </style>
</head>
<body>
    <header>
        <h1>AI Family Movie Recommendations</h1>
    </header>
    <div class="movie-grid">
        {{MOVIE_CARDS}}
    </div>
</body>
</html>
"""

async def main():
    agent = Agent(
        task=task_description,
        llm=llm,
        use_vision=True,
        max_failures=3,
        retry_delay=5
    )

    history = await agent.run(max_steps=100)

    print("\n===== RESULTS (AGENT RAW OUTPUT) =====\n")
    final_texts = []
    if history and history.history:
        final_step = history.history[-1]
        if final_step.result:
            for r in final_step.result:
                if r.extracted_content:
                    print("EXTRACTED CONTENT:", r.extracted_content)
                    final_texts.append(r.extracted_content)
                if r.error:
                    print("ERROR:", r.error)
        else:
            print("No final extracted content in last step.")
    else:
        print("No history or result found.")

    combined_output = "\n".join(final_texts).strip()

    translator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    translation_prompt = f"""
We have the following text describing multiple recommended movies (some Hebrew, some English):
{combined_output}

Please extract each recommended movie as an **array of JSON objects** with the **exact** keys:
- "poster" (a direct URL or fallback "https://via.placeholder.com/300x450/000/fff?text=No+Poster")
- "hebrew_title"
- "english_title"
- "hebrew_summary" (RTL)
- "english_summary"
- "age_range"
- "family_friendly_reason"
- "ticket_link": the specific link from https://hotcinema.co.il/theater/1 for that movie's tickets
  (if no exact link was found, fallback to "https://hotcinema.co.il/theater/1")

Make **no** additional text, headings, or code fences. 
Output **only** valid JSON, e.g.:

[
  {{
    "poster": "https://example.com/poster.jpg",
    "hebrew_title": "הנכס",
    "english_title": "The Asset",
    "hebrew_summary": "עלילה משפחתית...",
    "english_summary": "A family-oriented plot...",
    "age_range": "12+",
    "family_friendly_reason": "Shows a strong bond between grandparents and grandchildren.",
    "ticket_link": "https://hotcinema.co.il/movie/abcd1234"
  }},
  ...
]
"""

    translation_response = translator_llm.invoke(translation_prompt)
    text_json = translation_response.content.strip()

    try:
        movies_data = json.loads(text_json)
    except json.JSONDecodeError:
        movies_data = [{
            "poster": "https://via.placeholder.com/300x450/000/fff?text=No+Poster",
            "hebrew_title": "שגיאת JSON",
            "english_title": "JSON Error",
            "hebrew_summary": combined_output,
            "english_summary": "Could not parse JSON from LLM translation.",
            "age_range": "N/A",
            "family_friendly_reason": "N/A",
            "ticket_link": "https://hotcinema.co.il/theater/1"
        }]

    cards_html = []
    for m in movies_data:
        poster = m.get("poster", "html_assets/default_poster.png")
        h_title = m.get("hebrew_title", "")
        e_title = m.get("english_title", "")
        h_summary = m.get("hebrew_summary", "")
        e_summary = m.get("english_summary", "")
        age = m.get("age_range", "")
        reason = m.get("family_friendly_reason", "")
        ticket_link = m.get("ticket_link", "https://hotcinema.co.il/theater/1")

        card_html = f"""
        <div class="movie-card">
            <img src="{poster}" alt="{e_title}" class="movie-poster">
            <h2 class="movie-title">
                <span class="hebrew-text">{h_title}</span><br>
                <span>({e_title})</span>
            </h2>
            <p class="movie-description hebrew-text">{h_summary}</p>
            <p class="movie-description">{e_summary}</p>
            <p class="movie-description">Age Range: {age}</p>
            <p class="movie-description">Family-Friendly Reason: {reason}</p>
            <a href="{ticket_link}" target="_blank" class="get-tickets">Get Tickets</a>
        </div>
        """
        cards_html.append(card_html)

    final_html = html_template.replace("{{MOVIE_CARDS}}", "\n".join(cards_html))

    output_file = "ai_family_movie_recommendations.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_html)

    webbrowser.open(output_file)

if __name__ == "__main__":
    asyncio.run(main())

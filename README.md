# AI Family Movie Recommendation Agent

The AI Family Movie Recommendation Agent is an intelligent agent designed to independently browse the [HOT Cinemas website](https://hotcinema.co.il) and recommend movies suitable for a family movie night. The agent interacts with the original Hebrew site, researches the movies, and prepares an HTML page with bilingual descriptions and analysis of family friendliness in both English and Hebrew. Each movie recommendation includes a 1-click button to buy tickets.

![](html_assets/walkthrough.gif)

It uses the OpenAI API to generate movie descriptions and family-friendliness analysis.

## Features

- **Independent Browsing**: The agent uses a browser to navigate the HOT Cinemas website.
- **Bilingual Descriptions**: Provides movie descriptions and family-friendliness analysis in both English and Hebrew.
- **1-Click Ticket Purchase**: Generates an HTML page with buttons for easy ticket purchasing.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/hummusonrails/movie-recommender-agent.git
    cd movie-recommender
    ```

2. Set up a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Activate the virtual environment:
    ```sh
    source venv/bin/activate
    ```

2. Configure the environment variables in `.env.`:
    ```sh
    cp .env.example .env
    ```

    - `HOT_CINEMAS_URL`: The URL of the HOT Cinemas website.
    - `OPENAI_API_KEY`: Your API key for OpenAI.

2. Run the agent:
    ```sh
    python main.py
    ```

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

This project uses the agent framework from the open-source library [browser-use](https://github.com/browser-use/browser-use).
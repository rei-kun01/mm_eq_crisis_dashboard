# Summarize articles using distilbart-cnn-12-6

import torch
import re
import time
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from news.db_connection import get_db_connection

def preprocess_text(text: str) -> str:
    """Clean and normalize input text.

    Args:
        text (str): Raw input text

    Returns:
        str: Cleaned and normalized text
    """
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text.strip())
    # Remove new line characters
    text = re.sub(r'\n+', ' ', text)
    # Remove non-breaking space
    text = re.sub(r'&nbsp;', '', text)
    # Remove special characters but keep punctuation
    text = re.sub(r"[^\w\s.,!?-]", "", text)

    return text


class TextSummarizer:
    def __init__(self, model_name="sshleifer/distilbart-cnn-12-6"):
        """Initialize the summarizer with a pre-trained model.

        Args:
            model_name (str): Name of the pre-trained model to use.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.to(self.device)


    def summarize(self, text, max_length=130, min_length=30, length_penalty=2.0,
                       repetition_penalty=2.0, num_beams=4, early_stopping=True):
        """Generate a summary for the given text.

        Args:
            text (str): The text to summarize
            max_length (int): Maximum length of the summary
            min_length (int): Minimum length of the summary
            length_penalty (float): Penalty for longer summaries
            repetition_penalty (float): Penalty for repeated tokens
            num_beams (int): Number of beams for beam search
            early_stopping (bool): Whether to stop when all beams are finished

        Returns:
            str: The generated summary
        """
        summary = "Summary generation failed."  # Default fallback

        try:
            # Tokenize the input text
            inputs = self.tokenizer(text, max_length=1024, truncation=True,
                                    padding="max_length", return_tensors="pt"
                                    ).to(self.device)

            # Generate summary
            summary_ids = self.model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=max_length,
                min_length=min_length,
                length_penalty=length_penalty,
                repetition_penalty=repetition_penalty,
                no_repeat_ngram_size=3,
                num_beams=num_beams,
                early_stopping=early_stopping
            )
            # Decode and return the summary
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        except Exception as e:(
            print(f"Error during summarization: {str(e)}"))

        return summary


def main():
    """
    Fetch raw article text, generate summaries, and update the database
    """
    start = time.time()
    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            # Extract article IDs and texts to identify which row to update
            cur.execute("SELECT id, text FROM news_articles WHERE summary IS NULL;")
            articles = cur.fetchall()  # List of tuples: [(id1, text1), (id2, text2), ...]

            if not articles:
                print("✅ No new articles to summarize.")
                return

            summarizer = TextSummarizer()
            for article_id, raw_text in articles:
                cleaned_text = preprocess_text(raw_text)
                summary = summarizer.summarize(cleaned_text)

                # Update summary in the database
                cur.execute("""UPDATE news_articles SET summary = %s WHERE id = %s""", (summary, article_id))

        conn.commit()
        print(f"✅ {len(articles)} summaries saved to the database.")

    except Exception as e:
        print(f"❌ Error in main(): {e}")
        conn.rollback()

    finally:
        conn.close()

    end = time.time()
    print(f"✅ Summarized the articles in {end - start:.2f} seconds.")

if __name__ == "__main__":
    main()


# To preview results in the database:
conn = get_db_connection()
with conn.cursor() as cur:
    cur.execute("""
            SELECT summary
            FROM news_articles
            """,)
    result = cur.fetchall()

print(result[-10:])


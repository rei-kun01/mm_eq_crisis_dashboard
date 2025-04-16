# Testing 3 different transformer models from Hugging Face for summarization

# Note:
# The input texts for these models are raw html texts, not preprocessed to remove special html characters.
# This might impact what each model outputs.

from transformers import pipeline
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from transformers import T5ForConditionalGeneration, T5Tokenizer
from news.db_connection import get_db_connection

article_texts = []
conn = get_db_connection()

with conn.cursor() as cur:
    cur.execute("""
            SELECT text
            FROM news_articles
            """,)
    texts = cur.fetchall()  # "texts" is a list of tuples in this form [(text1,), (text2,), ...].
    for text in texts:
        article_text = text[0]
        article_texts.append(article_text)

#### ABSTRACTIVE SUMMARIZATION ####
#### Using bart in pytorch model ####

summarizer = pipeline("summarization", model = "sshleifer/distilbart-cnn-12-6")
summary_text = summarizer(article_texts[0], min_length = 100, max_length = 800)
print("Summary:", summary_text)

# Output:
# Pyawbwe, a town in Mandalay Region that was badly affected by the deadly earthquake that struck the region nearly two weeks ago, remains in ruins and blanketed in dust .
# The local fire department estimated that 242 people—145 men and 97 women—were killed in the town .
# At least 38 people were rescued alive, while 197 others were injured, according to the fire department .
# More than 3,000 people are said to be sheltering at monasteries and other religious buildings.


#### Using Google Pegasus Xsum model ####
pegasus_model_name = "google/pegasus-xsum"
pegasus_tokenizer = PegasusTokenizer.from_pretrained(pegasus_model_name)
pegasus_model = PegasusForConditionalGeneration.from_pretrained(pegasus_model_name) # Define PEGASUS model

# Encode input text
tokens = pegasus_tokenizer(article_texts[0],
                           truncation = True,
                           padding = "longest",
                           max_length = 512,
                           return_tensors = "pt")  # Create tokens

# Generate the summary
encoded_summary = pegasus_model.generate(**tokens, min_length = 100, max_length = 500)

# Decode the summarized text
decoded_summary = pegasus_tokenizer.decode(encoded_summary[0], skip_special_tokens=True)

# Print the summary
print('Decoded Summary :',decoded_summary)

summarizer = pipeline(
    "summarization",
    model = pegasus_model_name,
    tokenizer = pegasus_tokenizer,
    framework = "pt"
)

summary = summarizer(article_texts[0], truncation = True, min_length = 100, max_length = 500)
print(summary)

# Output:
# As the death toll from Myanmar’s devastating earthquake continues to rise,
# the scale of the devastation in one town has been revealed to be much worse than the government’s official figure of 145 people killed in Pyawbwe, local sources have told Myanmar Now,
# with hundreds of people still trapped under the rubble of buildings that collapsed in the magnitude-6.9 tremor on 28 March.,
# writes Myanmar Now’s Kyaw Soe Thet, who was in Pyawbwe at the time of the earthquake.
# (That last sentence about "Myanmar Now’s Kyaw Soe Thet, who was in Pyawbwe at the time of the earthquake" might be made up because it was not in the original article.)

#### Using T5 model ####

model = T5ForConditionalGeneration.from_pretrained("t5-base")  # Initialize the model architecture and weights.
tokenizer = T5Tokenizer.from_pretrained("t5-base")

inputs = tokenizer.encode("summarize: " + article_texts[0],
                          return_tensors="pt",
                          max_length = 512,
                          truncation = True)
outputs = model.generate(
    inputs,
    max_length = 800,  # The arguments max_length and min_length control the length of the summary output.
    min_length = 40,
    length_penalty = 2.0, # Controls the summary conciseness.
    num_beams = 4, # Controls the beam search for better quality.
    early_stopping = False) # If True, stop the generation when all beams are finished.

# print(outputs)
print(tokenizer.decode(outputs[0]))

# Output:
# local sources say parts of Pyawbwe remain in ruins and blanketed in dust .
# "the work isn’t finished yet and will take at least two more months," a volunteer says .
# at least 38 people were rescued alive, while 197 others were injured, according to the fire department .
# residents of Pyawbwe claim the actual number of dead and injured is much higher.
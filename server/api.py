from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

# Load the server IP from environment variables
SERVER_IP = os.getenv("SERVER_IP")

# Ensure SERVER_IP is set
if SERVER_IP is None:
    raise ValueError("SERVER_IP is not set in environment variables.")


# Load the fine-tuned model and tokenizer
model_dir = ".././fine_tuned_model"
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForSequenceClassification.from_pretrained(model_dir)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    text_input = data['text']

    # Tokenize the text
    inputs = tokenizer(text_input, return_tensors="pt")

    # Perform prediction
    output = model(**inputs)

    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    scores_dict = {
        'Negative': scores[0],
        'Neutral': scores[1],
        'Positive': scores[2]
    }
    max_key = max(scores_dict, key=scores_dict.get)

    # Get the maximum value
    sentiment = str(scores_dict[max_key])

    return jsonify({
        'sentiment': sentiment,
        'score': str(max_key)
    })

if __name__ == '__main__':
    app.run(host=SERVER_IP,port=5000, debug=True)

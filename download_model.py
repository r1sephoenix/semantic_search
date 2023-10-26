from transformers import AutoTokenizer, AutoModel
import os


def download_model(model_path, model_name):
    if not os.path.exists(model_path):
        # Create the directory
        os.makedirs(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    # Save the model and tokenizer to the specified directory
    model.save_pretrained(model_path)
    tokenizer.save_pretrained(model_path)


download_model('models/E5/', 'intfloat/multilingual-e5-large')

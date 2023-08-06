# traversaal/semantic_search.py

import warnings
import torch
from transformers import AutoTokenizer, AutoModel


class SemanticSearch:
    def __init__(self, model_name):
        warnings.filterwarnings("ignore")  # Hide warnings
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def encode(self, text):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")  # Hide warnings
            inputs = self.tokenizer(
                text, padding=True, truncation=True, return_tensors="pt"
            )
            with torch.no_grad():
                outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :]
        return embeddings.numpy()

    def encode_data(self, df):
        encoded_data = df.copy()
        encoded_data["embedding"] = encoded_data["hotel_review"].apply(
            self.encode
        ) + encoded_data["hotel_description"].apply(self.encode)
        return encoded_data

    def search(self, encoded_data, query):
        query_embedding = self.encode(query)
        encoded_data["score"] = encoded_data["embedding"].apply(
            lambda x: float(
                torch.cosine_similarity(
                    torch.Tensor(x), torch.Tensor(query_embedding)
                ).numpy()
            )
        )
        encoded_data = encoded_data.sort_values(by="score", ascending=False)

        # Get relevant reviews
        # encoded_data["relevant_reviews"] = encoded_data.apply(
        #     lambda row: self.get_relevant_reviews(
        #         row["id"], row["hotel_name"], encoded_data, query
        #     ),
        #     axis=1,
        # )

        relevant_results = encoded_data[["id", "hotel_name", "score", "hotel_review"]]
        relevant_results.rename(
            {"hotel_review": "relevant_review"}, axis="columns", inplace=True
        )

        return relevant_results

    def get_relevant_reviews(self, hotel_id, hotel_name, encoded_data, query):
        relevant_reviews = encoded_data[
            (encoded_data["id"] == hotel_id)
            & (encoded_data["hotel_name"] == hotel_name)
        ]["hotel_review"].tolist()
        return [review for review in relevant_reviews if query in review.lower()]

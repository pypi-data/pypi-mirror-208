import pandas as pd
from transformers import BertModel, BertTokenizer, AutoConfig
import torch
import numpy as np
from database import database


class Bert:
    def __init__(self):
        # Load the BERT tokenizer and model
        self.config = AutoConfig.from_pretrained('bert-base-uncased')
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased', config=self.config)

    def connect_to_db(self):
        # Connect to the MySQL database
        database_conn = database()
        db = database_conn.connect_to_database()
        return db

    def get_sentence_embedding(self, field):
        # Tokenize the fields
        tokens = self.tokenizer.encode(field, add_special_tokens=False)
        # Convert the tokens to a PyTorch tensor
        input_ids = torch.tensor(tokens).unsqueeze(0)
        # Get the embeddings for each token
        outputs = self.model(input_ids)
        embeddings = outputs.last_hidden_state
        # Average the embeddings to get the sentence embedding
        sentence_embedding = embeddings.mean(dim=1)
        # Convert the sentence embedding to a numpy array
        sentence_embedding = sentence_embedding.cpu().detach().numpy()
        return sentence_embedding

    def classify(self, field1, field2, schema_table, data, arg_you_want_to_classify_to_one_var_in_csv_file, csv_table=None):
        if not isinstance(csv_table, pd.DataFrame):
            csv_table = self.the_table_you_want_classify_to_csv(field1, field2, schema_table, data)
        # Get the sentence embeddings for each job title in the table
        name_embeddings = csv_table[field2].apply(self.get_sentence_embedding)
        # Get the sentence embedding for the new vacancy title
        arg_embedding = self.get_sentence_embedding(arg_you_want_to_classify_to_one_var_in_csv_file)
        # Calculate the cosine similarity between the vacancy embedding and each job title embedding
        similarities = name_embeddings.apply(lambda x: (x @ arg_embedding.T)[0])
        similarities_np = np.array(similarities.values,
                                   dtype=np.float32)  # Convert to numpy array with compatible dtype
        # Get the index of the job title with the highest similarity
        best_match_idx = np.argmax(similarities_np)
        # Get the job title with the highest similarity
        best_match = [csv_table.loc[best_match_idx, field2],
                      csv_table.loc[best_match_idx, field1]]
        return best_match

    # this function take the table you want to be classified to and creating csv from it
    def the_table_you_want_classify_to_csv(self, field1, field2, schema_table, db):
        # choose which fields you want to be classified to
        sql_query = f"SELECT {field1}, {field2} FROM {schema_table}"
        # Load the job title table into a pandas DataFrame
        csv_table = pd.read_sql_query(sql_query, db)
        # Save the DataFrame to a CSV file
        csv_table.to_csv(str(schema_table) + ".csv", index=False)
        return csv_table


if __name__ == '__main__':
    pass

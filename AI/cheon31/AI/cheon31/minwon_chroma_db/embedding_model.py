from transformers import AutoTokenizer, AutoModel
import torch
from torch.nn.functional import cosine_similarity


#Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


# Sentences we want sentence embeddings for
sentences = ['안녕하세요, 만나서 반갑습니다.', '처음 뵙겠습니다, 반가워요']

# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained("snunlp/KR-SBERT-V40K-klueNLI-augSTS")
model = AutoModel.from_pretrained("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

# Tokenize sentences
encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

# Compute token embeddings
with torch.no_grad():
    model_output = model(**encoded_input)

# Perform pooling. In this case, mean pooling.
sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
similarity = cosine_similarity(sentence_embeddings[0], sentence_embeddings[1], dim=0)
print(f"{similarity.item():.4f}")

print("Sentence embeddings:")
print(sentence_embeddings)

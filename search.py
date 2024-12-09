import pandas as pd
import torch
from PIL import Image
import open_clip
from open_clip import create_model_and_transforms, tokenizer
import torch.nn.functional as F

def search_images(image_query, text_query, hybrid_query_weight, query_type) -> list:
    df = pd.read_pickle('image_embeddings.pickle')

    model, _, preprocess = create_model_and_transforms('ViT-B/32', pretrained='openai')
    model.eval()

    if query_type == "image_query":
        img = Image.open(image_query).convert("RGB")
        img_tensor = preprocess(img).unsqueeze(0)
        with torch.no_grad():
            query_embedding = F.normalize(model.encode_image(img_tensor), dim=-1)
    elif query_type == "text_query":
        tokenizer = open_clip.get_tokenizer('ViT-B-32')
        text = tokenizer([text_query])
        query_embedding = F.normalize(model.encode_text(text))
    else:
        image = preprocess(Image.open(image_query)).unsqueeze(0)
        image_query = F.normalize(model.encode_image(image))
        tokenizer = open_clip.get_tokenizer('ViT-B-32')
        text = tokenizer([text_query])
        text_query = F.normalize(model.encode_text(text))

        lam = hybrid_query_weight

        query_embedding = F.normalize(lam * text_query + (1.0 - lam) * image_query)


    # Compute cosine similarity for each embedding
    df["cos_sim"] = df["embedding"].apply(
        lambda emb: F.cosine_similarity(query_embedding, torch.tensor(emb).unsqueeze(0), dim=1).item()
    )

    # Sort by cosine similarity in descending order and take top 5
    top_5 = df.sort_values(by="cos_sim", ascending=False).head(5)

    # Prepare the results as a list of tuples: (image_path, similarity_score)
    results = []
    for _, row in top_5.iterrows():
        image_path = "coco_images_resized/" + row["file_name"]
        similarity_score = row["cos_sim"]
        results.append((image_path, similarity_score))

    return results
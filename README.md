# Learning to Update Natural Language Comments Based on Code Changes

Download generation and update data from here [here](https://drive.google.com/open?id=12VMmdE67bp5UFYIoBUf0ibKGXFCH6fQo).

1. Create a directory named `generation-models` in the root directory
```
mkdir generation-models
```
2. Train the comment generation model:
```
python3 comment_generation.py -data_path public_comment_update_data/full_comment_generation/ -model_path generation-models/model.pkl.gz
```
3. Evaluate the comment generation model:
```
python3 comment_generation.py -data_path public_comment_update_data/full_comment_generation/ -model_path generation-models/model.pkl.gz --test_mode
```
4. Create a direction named `embeddings` in the root directory
```
mkdir embeddings
```
5. Save pre-trained embeddings from the comment generation model to disk:
```
python3 comment_generation.py -data_path public_comment_update_data/full_comment_generation/ -model_path generation-models/model.pkl.gz --test_mode --get_embeddings
```
6. Train the comment update model (i.e., edit model):
```
python3 comment_update.py -data_path public_comment_update_data/comment_update/ -model_path update-models/model.pkl.gz
```
3. Evaluate the comment update model (i.e., edit model)l:
```
python3 comment_update.py -data_path public_comment_update_data/comment_update/ -model_path update-models/model.pkl.gz --test_mode --rerank
```
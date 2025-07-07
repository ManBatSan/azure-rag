az cognitiveservices account deployment create \
  --name embeddings-dep \
  --name ${TF_VAR_prefix}-openai \
  --resource-group ${TF_VAR_prefix}-rg \
  --model-name text-embedding-3-small \
  --model-version "1" \
  --model-format OpenAI \
  --deployment-name text-embedding-3-small
az cognitiveservices account deployment create \
  --name chat-dep \
  --name ${TF_VAR_prefix}-openai \
  --resource-group ${TF_VAR_prefix}-rg \
  --model-name gpt-4o-mini \
  --model-version "2024-07-18" \
  --model-format OpenAI \
  --deployment-name gpt-4o-mini

#!/usr/bin/env bash
# Proof of fix: same 1x1 PNG through a live LiteLLM proxy -> Anthropic, with and without a MIME parameter.
PNG="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
for HEADER in "data:image/png" "data:image/png;charset=UTF-8"; do
  echo "\$ curl localhost:4000/v1/chat/completions  (image_url: ${HEADER};base64,...)"
  curl -s localhost:4000/v1/chat/completions -H "Authorization: Bearer ${LITELLM_MASTER_KEY:?set LITELLM_MASTER_KEY}" -H "Content-Type: application/json" -d '{
    "model": "claude-haiku", "max_tokens": 5,
    "messages": [{"role": "user", "content": [
      {"type": "text", "text": "What color is this pixel? One word."},
      {"type": "image_url", "image_url": {"url": "'"${HEADER}"';base64,'"${PNG}"'"}}]}]
  }' | python3 -c 'import json,sys; r=json.load(sys.stdin); print("  ->", ("OK: " + repr(r["choices"][0]["message"]["content"])) if "choices" in r else "ERROR " + str(r["error"].get("code")) + ": " + r["error"]["message"][:230])'
done

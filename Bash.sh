curl "https://api.anthropic.com/v1/messages/batches" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --header "x-api-key: $sk-ant-api03-bKiLriC1zwnA8bUCThE
s_Vm_LM7bReU65VyDyHXhtvpU598QPgr
HimxP49JRPzhgyY1C3GuN019TT4V_QAY
FjQ-Ff4D8AAA
•" \
  --header "anthropic-beta: message-batches-2024-09-24" \
  --data '{
    "requests": [
      {
        "custom_id": "first-prompt-in-my-batch",
        "params": {
          "model": "claude-haiku-4-5-20251001",
          "max_tokens": 10000,
          "messages": [
            {"role": "user", "content": "Hey Claude, tell me a short fun fact about video games!"}
          ]
        }
      },
      {
        "custom_id": "second-prompt-in-my-batch",
        "params": {
          "model": "claude-sonnet-4-5-20250929",
          "max_tokens": 10000,
          "messages": [
            {"role": "user", "content": "Hey Claude, tell me a short fun fact about bees!"}
          ]
        }
      }
    ]
  }'
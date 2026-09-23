## What I picked and why

I started by checking open issues, but the recent bugs I investigated already had PRs. I asked Claude to look through previous fixes for similar gaps while I finished the installation and got familiar with the repo.

We found a small, reproducible bug in image conversion for Anthropic. Given `data:image/png;charset=UTF-8;base64,...`, LiteLLM forwarded `image/png;charset=UTF-8` as the image's `media_type`. Anthropic rejects that with HTTP 400 because it expects a bare type such as `image/png`. This can also happen when LiteLLM downloads an HTTP image and copies a server's parameterized `Content-Type` into a data URL. It was a narrow fix with a realistic trigger and clear before/after behavior.

## How I found my way to the right file

Similar fixes for Bedrock images and Gemini tool results pointed us to `litellm/litellm_core_utils/prompt_templates/factory.py`. I traced the Anthropic path to `convert_to_anthropic_image_obj`, which split off the base64 payload but left MIME parameters attached to the type. The fix strips those parameters and surrounding whitespace, following the existing approach nearby. It preserves the image payload and keeps an explicit caller-supplied `format` authoritative.

## What I did to verify it works

I used an existing Anthropic API key to confirm that the parameterized type really was rejected. Through a running LiteLLM proxy, the same image failed before the fix and succeeded afterward; the ordinary data URL succeeded in both cases. The saved outputs are in `fix1_live/before_proof.txt` and `fix1_live/after_proof.txt`.

I had Claude add six UTs cases covering MIME parameters, whitespace, an ordinary data URL, an explicit format override, and a mocked HTTP download. Before the fix, four failed and the two controls passed; afterward, all six passed. 

## Anything I'd still want to check
The bigger thing I'd look into is the duplicated parsing code. Several providers parse data URLs separately, and Bedrock and Gemini tool results already handled the parameters that broke this path. That makes it easy to fix a bug in one place and leave it elsewhere. I'd consider extracting the common parsing into a shared helper, while keeping provider specific checks separate. I left that out of this assignment because it would mean changing and testing several otherwise working integrations.

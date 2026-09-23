import os, base64, struct, zlib, litellm
raw = open("/home/ori/Documents/homeproject/ai_company/.env").read().strip()
os.environ["ANTHROPIC_API_KEY"] = raw.split("=", 1)[1].strip().strip('"\'') if "=" in raw else raw
def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
png = base64.b64encode(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
      + chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00")) + chunk(b"IEND", b"")).decode()
for url in (f"data:image/png;base64,{png}", f"data:image/png;charset=UTF-8;base64,{png}"):
    try:
        litellm.completion(model="anthropic/claude-haiku-4-5-20251001", max_tokens=1,
            messages=[{"role": "user", "content": [{"type": "text", "text": "hi"},
                      {"type": "image_url", "image_url": {"url": url}}]}])
        print(f"{url.split(',')[0]:<40} -> OK")
    except Exception as e:
        print(f"{url.split(',')[0]:<40} -> {type(e).__name__}: {str(e)[:220]}")

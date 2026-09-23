"""Live check: does Anthropic reject a media_type with MIME params? Never prints the key."""
import base64, struct, zlib, httpx

raw = open("/home/ori/Documents/homeproject/ai_company/.env").read().strip()
key = raw.split("=", 1)[1].strip().strip('"\'') if "=" in raw else raw

def png_1x1() -> str:
    def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"\x00\xff\x00\x00")
    return base64.b64encode(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")).decode()

img = png_1x1()
for media_type in ("image/png", "image/png;charset=UTF-8"):
    r = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
        json={"model": "claude-haiku-4-5-20251001", "max_tokens": 1, "messages": [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": img}},
            {"type": "text", "text": "hi"}]}]},
        timeout=30,
    )
    body = r.json()
    detail = body.get("error", {}).get("message", "") if r.status_code != 200 else "accepted"
    print(f"media_type={media_type!r:<28} -> HTTP {r.status_code}: {detail[:300]}")

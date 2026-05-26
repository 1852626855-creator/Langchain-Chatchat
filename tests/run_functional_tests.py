"""Functional test runner for Langchain-Chatchat."""
import json
import os
import sys
import time
import uuid

import requests

BASE = os.environ.get("CHATCHAT_API", "http://127.0.0.1:7861")
TIMEOUT = 180
RESULTS = []


def record(name, status, detail=""):
    RESULTS.append({"name": name, "status": status, "detail": detail})
    icon = {"PASS": "[OK]", "FIXED": "[FIXED]", "FAIL": "[FAIL]"}.get(status, "[?]")
    print(f"{icon} {name}: {detail or status}")


def parse_sse(text):
    last = None
    for line in text.splitlines():
        if line.startswith("data: "):
            try:
                last = json.loads(line[6:])
            except json.JSONDecodeError:
                pass
    return last


def test_docs():
    r = requests.get(f"{BASE}/docs", timeout=10)
    record("GET /docs", "PASS" if r.status_code == 200 else "FAIL", f"status={r.status_code}")


def test_auth():
    user = f"testuser_{uuid.uuid4().hex[:8]}"
    pwd = "test123"
    reg = requests.post(
        f"{BASE}/auth/register",
        json={"username": user, "password": pwd},
        timeout=30,
    )
    if reg.status_code not in (200, 201):
        record("POST /auth/register", "FAIL", f"{reg.status_code} {reg.text[:200]}")
        return None
    record("POST /auth/register", "PASS", f"user={user}")

    login = requests.post(
        f"{BASE}/auth/login",
        json={"username": user, "password": pwd},
        timeout=30,
    )
    if login.status_code != 200:
        record("POST /auth/login", "FAIL", f"{login.status_code} {login.text[:200]}")
        return None
    token = login.json().get("token")
    record("POST /auth/login", "PASS", "token received")
    return {"user": user, "token": token}


def test_chat(token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(
        f"{BASE}/chat/chat",
        headers=headers,
        json={"query": "你好，请用一句话介绍你自己", "stream": False},
        timeout=TIMEOUT,
    )
    if r.status_code != 200:
        record("POST /chat/chat", "FAIL", f"{r.status_code} {r.text[:300]}")
        return
    data = parse_sse(r.text)
    text = (data or {}).get("text", "")
    record(
        "POST /chat/chat",
        "PASS" if text.strip() else "FAIL",
        f"answer_len={len(text)} preview={text[:80]!r}",
    )


def test_list_kbs():
    r = requests.get(f"{BASE}/knowledge_base/list_knowledge_bases", timeout=30)
    if r.status_code != 200:
        record("GET /knowledge_base/list_knowledge_bases", "FAIL", f"{r.status_code}")
        return None
    body = r.json()
    if body.get("code") != 200:
        record("GET /knowledge_base/list_knowledge_bases", "FAIL", str(body))
        return None
    record("GET /knowledge_base/list_knowledge_bases", "PASS", f"count={len(body.get('data', []))}")
    return body.get("data", [])


def test_kb_flow():
    kb_name = "test_kb"
    embed_model = "zhipu-api"

    delete = requests.post(
        f"{BASE}/knowledge_base/delete_knowledge_base",
        json={"knowledge_base_name": kb_name},
        timeout=120,
    )
    if delete.status_code == 200 and delete.json().get("code") == 200:
        dbody = delete.json()
        record("POST delete_knowledge_base", "PASS", dbody.get("msg", "ok"))
    else:
        record("POST delete_knowledge_base", "FAIL", f"{delete.status_code} {delete.text[:200]}")

    create = requests.post(
        f"{BASE}/knowledge_base/create_knowledge_base",
        json={"knowledge_base_name": kb_name, "embed_model": embed_model},
        timeout=60,
    )
    cbody = create.json() if create.headers.get("content-type", "").startswith("application/json") else {}
    if create.status_code == 200 and cbody.get("code") == 200:
        record("POST create_knowledge_base", "PASS", cbody.get("msg", "ok"))
    else:
        record("POST create_knowledge_base", "FAIL", f"{create.status_code} {create.text[:200]}")
        return

    content_dir = os.path.join("knowledge_base", kb_name, "content")
    os.makedirs(content_dir, exist_ok=True)
    test_file = os.path.join(content_dir, "test.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("北京是中国的首都。")

    with open(test_file, "rb") as f:
        upload = requests.post(
            f"{BASE}/knowledge_base/upload_docs",
            data={
                "knowledge_base_name": kb_name,
                "override": "true",
                "to_vector_store": "true",
            },
            files=[("files", ("test.txt", f, "text/plain"))],
            timeout=TIMEOUT,
        )
    ubody = upload.json() if upload.headers.get("content-type", "").startswith("application/json") else {}
    if upload.status_code == 200 and ubody.get("code") == 200:
        record("POST upload_docs", "PASS", ubody.get("msg", "ok"))
    else:
        record("POST upload_docs", "FAIL", f"{upload.status_code} {upload.text[:300]}")
        return

    time.sleep(2)

    search = requests.post(
        f"{BASE}/knowledge_base/search_docs",
        json={"query": "首都", "knowledge_base_name": kb_name, "top_k": 3},
        timeout=60,
    )
    if search.status_code != 200:
        record("POST search_docs", "FAIL", f"{search.status_code} {search.text[:200]}")
        return
    hits = search.json()
    hit_text = json.dumps(hits, ensure_ascii=False)
    record(
        "POST search_docs",
        "PASS" if "北京" in hit_text else "FAIL",
        f"hits={len(hits) if isinstance(hits, list) else 'n/a'}",
    )

    chat = requests.post(
        f"{BASE}/chat/knowledge_base_chat",
        json={
            "query": "中国的首都是哪里？",
            "knowledge_base_name": kb_name,
            "stream": False,
        },
        timeout=TIMEOUT,
    )
    if chat.status_code != 200:
        record("POST knowledge_base_chat", "FAIL", f"{chat.status_code} {chat.text[:200]}")
        return
    cdata = parse_sse(chat.text)
    answer = (cdata or {}).get("text") or (cdata or {}).get("answer") or ""
    docs_text = json.dumps(cdata or {}, ensure_ascii=False)
    has_beijing = "北京" in answer or "北京" in docs_text
    record(
        "POST knowledge_base_chat",
        "PASS" if has_beijing else "FAIL",
        f"answer={answer[:120]!r}",
    )


def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, os.getcwd())
    print("=" * 60)
    print("Langchain-Chatchat functional tests")
    print("API:", BASE)
    print("=" * 60)

    try:
        test_docs()
        auth = test_auth()
        if auth:
            test_chat(auth["token"])
            hist = requests.get(
                f"{BASE}/auth/history",
                params={"token": auth["token"]},
                timeout=30,
            )
            record(
                "GET /auth/history",
                "PASS" if hist.status_code == 200 else "FAIL",
                f"status={hist.status_code} count={hist.json().get('count') if hist.ok else 'n/a'}",
            )
        test_list_kbs()
        test_kb_flow()
    except Exception as e:
        record("runner", "FAIL", str(e))

    fails = [r for r in RESULTS if r["status"] == "FAIL"]
    print("=" * 60)
    print(f"Total: {len(RESULTS)}, Failed: {len(fails)}")
    if fails:
        print("Failures:")
        for f in fails:
            print(" -", f["name"], f["detail"])
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

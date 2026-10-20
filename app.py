"""Public launcher: downloads a pinned private app using Streamlit Secrets."""
import io
import pathlib
import runpy
import ssl
import sys
import tarfile
import tempfile
import urllib.request

import certifi
import streamlit as st

REPOSITORY = "kadiroduncu/kripto-short-radar"
COMMIT = "a2e1703bb7660a59d6a9b276eabcb1235e6b7943"
MAX_ARCHIVE = 32 * 1024 * 1024

class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        result = super().redirect_request(req, fp, code, msg, headers, newurl)
        if result:
            from urllib.parse import urlsplit
            if urlsplit(req.full_url).netloc != urlsplit(newurl).netloc:
                result.remove_header("Authorization")
        return result

@st.cache_resource(show_spinner="Kripto Radar hazırlanıyor…")
def load_private_app(_token, commit):
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPOSITORY}/tarball/{commit}",
        headers={"Authorization": "Bearer " + _token,
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "KriptoRadar-PublicLauncher"})
    opener = urllib.request.build_opener(
        SafeRedirect(), urllib.request.HTTPSHandler(
            context=ssl.create_default_context(cafile=certifi.where())))
    with opener.open(request, timeout=120) as response:
        blob = response.read(MAX_ARCHIVE + 1)
    if len(blob) > MAX_ARCHIVE:
        raise ValueError("Archive limit")
    root = pathlib.Path(tempfile.mkdtemp(prefix="kripto-source-"))
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as archive:
        expanded = 0
        for member in archive.getmembers():
            parts = pathlib.PurePosixPath(member.name).parts
            if not parts or ".." in parts or pathlib.PurePosixPath(member.name).is_absolute():
                raise ValueError("Unsafe archive")
            if len(parts) < 2 or member.isdir():
                continue
            if not member.isfile():
                raise ValueError("Unsupported archive entry")
            expanded += member.size
            if expanded > 128 * 1024 * 1024:
                raise ValueError("Expanded archive limit")
            target = root.joinpath(*parts[1:])
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as source, target.open("wb") as output:
                import shutil
                shutil.copyfileobj(source, output)
    if not (root / "app.py").is_file():
        raise ValueError("Missing application")
    return root

try:
    settings = dict(st.secrets.get("radar", {}))
except Exception:
    settings = {}
token = settings.get("github_token", "")
if not token:
    st.set_page_config(page_title="Kripto Radar · Kurulum", page_icon="◉", layout="wide")
    st.title("Kripto Radar")
    st.info("Yayın hazır. Yönetici tarafından kalıcı kayıt bağlantısı tamamlanıyor.")
    st.stop()
try:
    source_root = load_private_app(token, COMMIT)
except Exception:
    st.set_page_config(page_title="Kripto Radar · Kurulum", page_icon="◉", layout="wide")
    st.title("Kripto Radar")
    st.error("Uygulama kaynağına erişilemiyor. Yönetici bağlantı ayarlarını kontrol etmeli.")
    st.stop()
sys.path.insert(0, str(source_root))
runpy.run_path(str(source_root / "app.py"), run_name="__main__")

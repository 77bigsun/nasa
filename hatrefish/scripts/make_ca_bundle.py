"""
把 Windows 系統憑證庫（含防毒軟體自己的根憑證，例如 Norton 的 HTTPS 掃描）匯出成 PEM，給 GDAL/curl 用。

症狀：Python／conda／GDAL 連 HTTPS 出現 CERTIFICATE_VERIFY_FAILED，但瀏覽器正常。
用法：python scripts/make_ca_bundle.py   → data/ca_bundle_windows.pem（已在 .gitignore 外，但只含公開憑證）
Python 本身則用 truststore（程式裡已自動 inject）；conda 用 `CONDA_SSL_VERIFY=truststore`。
"""
import ssl
from pathlib import Path

out = Path(__file__).resolve().parents[1] / "data" / "ca_bundle_windows.pem"
pems = []
for store in ("ROOT", "CA"):
    for cert, enc, trust in ssl.enum_certificates(store):
        if enc == "x509_asn":
            pems.append(ssl.DER_cert_to_PEM_cert(cert))
try:
    import certifi
    pems.append(Path(certifi.where()).read_text(encoding="utf-8"))
except ImportError:
    pass
out.write_text("".join(pems), encoding="utf-8")
print(f"wrote {out} ({len(pems)} entries)")

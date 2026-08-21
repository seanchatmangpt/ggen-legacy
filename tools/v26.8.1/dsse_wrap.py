#!/usr/bin/env python3
"""Minimal DSSE (Dead Simple Signing Envelope) wrapper.

Implements the Pre-Authentication Encoding (PAE) and envelope JSON shape from
the DSSE spec (https://github.com/secure-systems-lab/dsse/blob/master/protocol.md):

    PAE(type, body) = "DSSEv1" + SP + LEN(type) + SP + type + SP + LEN(body) + SP + body

    envelope = {
      "payloadType": <string>,
      "payload": <base64>,
      "signatures": [{"keyid": <string|null>, "sig": <base64>}]
    }

Signing/verification is delegated to `openssl dgst -sign / -verify` using the
same RSA-PSS (sha256, rsa_padding_mode:pss, rsa_pss_saltlen:-1) convention
already used by appliance/bin/run-reference-e2e.sh and
appliance/bin/verify-standing-portfolio.py for signing claim-manifest.json.
This script is additive only: it does not read, generate, or touch any real
appliance/production key material. Callers pass in whatever keypair they
want (see `--selftest` for a fully synthetic, disposable RSA test key).

Usage:
    dsse_wrap.py sign   --payload FILE --payload-type TYPE --private-key KEY.pem \
                         --keyid ID --out ENVELOPE.json
    dsse_wrap.py verify --envelope ENVELOPE.json --public-key KEY.pub.pem
    dsse_wrap.py selftest   # generates a throwaway RSA key, signs, verifies, prints proof
"""
from __future__ import annotations
import argparse, base64, json, subprocess, sys, tempfile
from pathlib import Path

DSSE_VERSION = b"DSSEv1"
SP = b" "


def pae(payload_type: bytes, body: bytes) -> bytes:
    """DSSE Pre-Authentication Encoding."""
    return (
        DSSE_VERSION + SP
        + str(len(payload_type)).encode() + SP + payload_type + SP
        + str(len(body)).encode() + SP + body
    )


def b64(data: bytes) -> str:
    return base64.standard_b64encode(data).decode("ascii")


def unb64(s: str) -> bytes:
    return base64.standard_b64decode(s)


def openssl_sign_pae(pae_bytes: bytes, private_key: Path) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".pae") as pae_f, \
         tempfile.NamedTemporaryFile(suffix=".sig") as sig_f:
        pae_f.write(pae_bytes); pae_f.flush()
        cmd = ["openssl", "dgst", "-sha256", "-sign", str(private_key),
               "-sigopt", "rsa_padding_mode:pss", "-sigopt", "rsa_pss_saltlen:-1",
               "-out", sig_f.name, pae_f.name]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"openssl sign failed: {r.stderr}")
        return Path(sig_f.name).read_bytes()


def openssl_verify_pae(pae_bytes: bytes, signature: bytes, public_key: Path) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile(suffix=".pae") as pae_f, \
         tempfile.NamedTemporaryFile(suffix=".sig") as sig_f:
        pae_f.write(pae_bytes); pae_f.flush()
        sig_f.write(signature); sig_f.flush()
        cmd = ["openssl", "dgst", "-sha256", "-verify", str(public_key),
               "-signature", sig_f.name,
               "-sigopt", "rsa_padding_mode:pss", "-sigopt", "rsa_pss_saltlen:-1",
               pae_f.name]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.returncode == 0, (r.stdout + r.stderr).strip()


def make_envelope(payload_bytes: bytes, payload_type: str, private_key: Path, keyid: str | None) -> dict:
    pae_bytes = pae(payload_type.encode(), payload_bytes)
    sig = openssl_sign_pae(pae_bytes, private_key)
    return {
        "payloadType": payload_type,
        "payload": b64(payload_bytes),
        "signatures": [{"keyid": keyid, "sig": b64(sig)}],
    }


def verify_envelope(envelope: dict, public_key: Path) -> tuple[bool, str]:
    payload_bytes = unb64(envelope["payload"])
    pae_bytes = pae(envelope["payloadType"].encode(), payload_bytes)
    results = []
    any_ok = False
    for s in envelope["signatures"]:
        ok, detail = openssl_verify_pae(pae_bytes, unb64(s["sig"]), public_key)
        any_ok = any_ok or ok
        results.append(f"keyid={s.get('keyid')} ok={ok} openssl={detail!r}")
    return any_ok, "; ".join(results)


def cmd_sign(args):
    payload_bytes = Path(args.payload).read_bytes()
    env = make_envelope(payload_bytes, args.payload_type, Path(args.private_key), args.keyid)
    out = json.dumps(env, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(out)
    print(out, end="")


def cmd_verify(args):
    env = json.loads(Path(args.envelope).read_text())
    ok, detail = verify_envelope(env, Path(args.public_key))
    print(json.dumps({"verified": ok, "detail": detail}))
    raise SystemExit(0 if ok else 2)


def cmd_selftest():
    """Generate a throwaway ed25519-unavailable-safe RSA test key (openssl genpkey),
    sign a real test payload into a DSSE envelope, verify it end to end via openssl,
    then tamper-check that verification correctly fails on a modified payload.
    Never touches real appliance key material."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        priv = td / "test-private.pem"
        pub = td / "test-public.pem"
        payload_path = td / "payload.txt"
        payload_path.write_text("dsse-roundtrip-selftest-payload\n")

        print("== generating disposable RSA-3072 test keypair (not production material) ==")
        r = subprocess.run(["openssl", "genpkey", "-algorithm", "RSA",
                             "-pkeyopt", "rsa_keygen_bits:3072", "-out", str(priv)],
                            capture_output=True, text=True)
        print("genpkey rc=", r.returncode, r.stderr.strip())
        r = subprocess.run(["openssl", "pkey", "-in", str(priv), "-pubout", "-out", str(pub)],
                            capture_output=True, text=True)
        print("pkey -pubout rc=", r.returncode, r.stderr.strip())

        payload_bytes = payload_path.read_bytes()
        payload_type = "application/vnd.ggen-legacy.dsse-selftest+text"
        pae_bytes = pae(payload_type.encode(), payload_bytes)
        print("\n== PAE bytes ==")
        print(pae_bytes)

        env = make_envelope(payload_bytes, payload_type, priv, keyid="dsse-selftest-key-1")
        env_path = td / "envelope.json"
        env_path.write_text(json.dumps(env, indent=2, sort_keys=True) + "\n")
        print("\n== DSSE envelope ==")
        print(json.dumps(env, indent=2, sort_keys=True))

        ok, detail = verify_envelope(env, pub)
        print("\n== verify (correct payload) ==")
        print("verified:", ok, "|", detail)
        if not ok:
            raise SystemExit("selftest FAILED: correct-payload verification did not pass")

        tampered = dict(env)
        tampered["payload"] = b64(b"tampered-payload-should-fail\n")
        ok2, detail2 = verify_envelope(tampered, pub)
        print("\n== verify (tampered payload, expect failure) ==")
        print("verified:", ok2, "|", detail2)
        if ok2:
            raise SystemExit("selftest FAILED: tampered payload incorrectly verified")

        print("\nSELFTEST OK: sign+verify round-trip succeeded and tamper detection succeeded")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("sign")
    sp.add_argument("--payload", required=True)
    sp.add_argument("--payload-type", required=True)
    sp.add_argument("--private-key", required=True)
    sp.add_argument("--keyid", default=None)
    sp.add_argument("--out", default=None)

    vp = sub.add_parser("verify")
    vp.add_argument("--envelope", required=True)
    vp.add_argument("--public-key", required=True)

    sub.add_parser("selftest")

    args = ap.parse_args()
    if args.cmd == "sign":
        cmd_sign(args)
    elif args.cmd == "verify":
        cmd_verify(args)
    elif args.cmd == "selftest":
        cmd_selftest()


if __name__ == "__main__":
    main()

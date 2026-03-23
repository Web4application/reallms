import json
import ssl
import socket
import hashlib
from typing import Any, Dict, List

# Multi-server Electrum list
SERVERS_JSON = r"""
[
  {"127.0.0.1": "electrum.blockstream.info",     "ssl_port": 50002, "tcp_port": 50001},
  {"127.0.0.1": "electrum1.cipig.net",           "ssl_port": 50002, "tcp_port": 50001},
  {"127.0.0.1": "electrum.emzy.de",              "ssl_port": 50002, "tcp_port": 50001},
  {"host": "btc.xf2.org",                   "ssl_port": 50002, "tcp_port": 50001},
  {"host": "electroncash.dk",               "ssl_port": 50002, "tcp_port": 50001},
  {"host": "node.bitaroo.net",              "ssl_port": 50002, "tcp_port": 50001},
  {"host": "cpfp.bitaroo.net",              "ssl_port": 50002, "tcp_port": 50001}
]
"""

class ElectrumClient:
    def __init__(self, host: str, port: int, use_ssl: bool = True):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.sock = None
        self.file = None
        self.req_id = 0

    def connect(self):
        raw = socket.create_connection((self.host, self.port), timeout=10)
        if self.use_ssl:
            context = ssl.create_default_context()
            self.sock = context.wrap_socket(raw, server_hostname=self.host)
        else:
            self.sock = raw
        self.file = self.sock.makefile("rwb")
        print(f"Connected to {self.host}:{self.port} ({'SSL' if self.use_ssl else 'TCP'})")

    def close(self):
        try:
            if self.file:
                self.file.close()
        finally:
            if self.sock:
                self.sock.close()

    def call(self, method: str, params: List[Any]) -> Any:
        self.req_id += 1
        payload = {"jsonrpc": "2.0", "id": self.req_id, "method": method, "params": params}
        self.file.write((json.dumps(payload) + "\n").encode("utf-8"))
        self.file.flush()
        line = self.file.readline()
        if not line:
            raise RuntimeError("No response from server")
        resp = json.loads(line.decode("utf-8"))
        if resp.get("error"):
            raise RuntimeError(f"Electrum error: {resp['error']}")
        return resp["result"]

# SHA256d helpers
def sha256d(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def reverse_hex(hex_str: str) -> bytes:
    return bytes.fromhex(hex_str)[::-1]

def compute_txid(raw_tx_hex: str) -> str:
    return sha256d(bytes.fromhex(raw_tx_hex))[::-1].hex()

def parse_header_merkle_root(header_hex: str) -> str:
    header = bytes.fromhex(header_hex)
    if len(header) != 80:
        raise ValueError("Invalid header length: expected 80 bytes")
    return header[36:68][::-1].hex()

def verify_merkle_proof(txid: str, merkle_branch: List[str], pos: int, expected_root: str) -> bool:
    current = reverse_hex(txid)
    for sibling_hex in merkle_branch:
        sibling = reverse_hex(sibling_hex)
        current = sha256d(current + sibling) if pos % 2 == 0 else sha256d(sibling + current)
        pos //= 2
    return current[::-1].hex() == expected_root

# Try servers until one connects
def connect_to_any_server(servers: List[Dict[str, Any]]) -> ElectrumClient:
    last_error = None
    for s in servers:
        host = s["host"]; ssl_port = s["ssl_port"]; tcp_port = s["tcp_port"]
        # SSL first
        try:
            client = ElectrumClient(host, ssl_port, use_ssl=True)
            client.connect()
            return client
        except Exception as e:
            print(f"SSL connect failed on {host}:{ssl_port} → {e}")
        # Then TCP fallback
        try:
            client = ElectrumClient(host, tcp_port, use_ssl=False)
            client.connect()
            return client
        except Exception as e:
            print(f"TCP connect failed on {host}:{tcp_port} → {e}")
            last_error = e
    raise RuntimeError(f"Could not connect to any Electrum server: {last_error}")

# Main SPV verify
def verify_transaction(txid: str) -> Dict[str, Any]:
    servers = json.loads(SERVERS_JSON)
    client = connect_to_any_server(servers)
    try:
        # fetch history for the tx
        hist = client.call("blockchain.transaction.get_history", [txid])
        if not hist:
            raise RuntimeError("Transaction not found on server")
        block_height = hist[-1]["height"]

        raw_tx = client.call("blockchain.transaction.get", [txid, False])
        if compute_txid(raw_tx) != txid:
            raise RuntimeError("Server returned raw TX that does not match the txid")

        merkle_info = client.call("blockchain.transaction.get_merkle", [txid, block_height])
        header_hex = client.call("blockchain.block.header", [block_height])

        merkle_root = parse_header_merkle_root(header_hex)
        verified = verify_merkle_proof(txid, merkle_info["merkle"], merkle_info["pos"], merkle_root)

        return {
            "txid": txid,
            "block_height": block_height,
            "verified": verified,
            "tx_position": merkle_info["pos"],
            "merkle_root_from_header": merkle_root,
            "merkle_branch_length": len(merkle_info["merkle"]),
            "server_used": client.host,
            "port_used": client.port,
            "used_ssl": client.use_ssl
        }
    finally:
        client.close()

# Example run
if __name__ == "__main__":
    txid = "PUT_REAL_TXID_HERE"
    result = verify_transaction(txid)
    print(json.dumps(result, indent=2))

#!/usr/bin/env python3
import asyncio
import aiohttp
import os
import sys
import time
import json
import re
from datetime import datetime

# =====================================================================
# VECTAS DEFI SECURITY FRAMEWORK v4.1 - HARDENED PRODUCTION ENGINE
# =====================================================================

CHANNELS = {
    "1": {"name": "Ethereum Mainnet", "url": "https://ethereum-rpc.publicnode.com", "id": 1, "speed": "12.0s", "sym": "ETH", "theme": "PURPLE"},
    "2": {"name": "Arbitrum One Rollup", "url": "https://arbitrum-one-rpc.publicnode.com", "id": 42161, "speed": "1.2s", "sym": "ARB", "theme": "CYAN"},
    "3": {"name": "Polygon PoS Network", "url": "https://polygon-bor-rpc.publicnode.com", "id": 137, "speed": "1.7s", "sym": "POL", "theme": "GREEN"}
}

DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"
SIGNATURES_FILE = "signatures.json"

# ANSI Color Matrix Controls
C_RESET = "\033[0m"
C_DARK  = "\033[1;30m"
C_WHITE = "\033[1;37m"
C_RED   = "\033[1;31m"
C_AMBER = "\033[1;33m"

THEMES = {
    "GREEN":  {"primary": "\033[1;32m", "accent": "\033[1;35m"}, 
    "CYAN":   {"primary": "\033[1;36m", "accent": "\033[1;33m"}, 
    "PURPLE": {"primary": "\033[1;35m", "accent": "\033[1;36m"}  
}

class VectasEngine:
    def __init__(self, target_network):
        self.target = target_network
        self.primary = THEMES[self.target["theme"]]["primary"]
        self.accent = THEMES[self.target["theme"]]["accent"]
        
        self.blocks_parsed = 0
        self.txs_processed = 0
        self.start_time = time.time()
        self.current_height = 0  
        self.gas_weight_bar = "░░░░░░░░░░░░░░░░░░"
        self.base_gas = "N/A"
        self.node_health = "BOOTING"
        self.frame = 0
        
        self.signatures = {}
        self.last_sig_mtime = 0
        
        self.crypto_assets = [
            {"asset": "BTC/USD", "icon": "₿", "status": "SCANNING"},
            {"asset": "ETH/USD", "icon": "Ξ", "status": "MONITORED"},
            {"asset": "POL/USD", "icon": "⬡", "status": "PIPELINE"},
            {"asset": "SOL/USD", "icon": "◎", "status": "LISTENING"}
        ]
        
        self.threat_logs = [
            "Industrial security cluster core mounted successfully.",
            f"Active target parameters anchored for {self.target['name']}.",
            "Establishing raw protocol sockets into core execution layer..."
        ]
        self.payload_stream = ["Awaiting high-speed data stream propagation..."] * 14

    def clean_ansi_len(self, text):
        """Calculates true printable string length handling all ANSI escape vectors."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return len(ansi_escape.sub('', text))

    def add_log(self, text, level="INFO"):
        timestamp = datetime.now().strftime('%H:%M:%S')
        color = C_WHITE if level == "INFO" else self.accent if level == "THREAT" else C_RED
        self.threat_logs.append(f"{C_DARK}[{timestamp}]{C_RESET} {color}{text}{C_RESET}")
        if len(self.threat_logs) > 14:
            self.threat_logs.pop(0)

    def add_payload(self, text):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.payload_stream.append(f"{C_DARK}[{timestamp}]{C_RESET} {self.primary}{text}{C_RESET}")
        if len(self.payload_stream) > 14:
            self.payload_stream.pop(0)

    def get_spinner(self):
        spinners = ["◢", "◣", "◤", "◥"]
        return f"{self.accent}{spinners[self.frame % len(spinners)]}{C_RESET}"

    def get_signal_bar(self):
        bars = [
            f"{self.primary}█▒▒▒▒▒▒▒▒▒ [ LINK ACTIVE ]{C_RESET}",
            f"{self.primary}███▒▒▒▒▒▒▒ [ DECODING ]   {C_RESET}",
            f"{self.primary}██████▒▒▒▒ [ INGESTING ]  {C_RESET}",
            f"{self.primary}██████████ [ STABLE ]     {C_RESET}",
        ]
        return bars[self.frame % len(bars)]

    def draw_ui(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        uptime = int(time.time() - self.start_time)
        self.frame += 1
        
        asset_index = (int(time.time()) // 3) % len(self.crypto_assets)
        current_asset = self.crypto_assets[asset_index]
        
        ticker_label = f"{current_asset['icon']} {current_asset['asset']}"
        status_display = current_asset['status']
        animated_ticker = f"{C_AMBER}{ticker_label}{C_RESET} {C_DARK}::{C_RESET} {self.primary}{status_display}{C_RESET}"
        
        raw_ticker_len = len(ticker_label) + len(status_display) + 4
        padding_needed = max(0, 41 - raw_ticker_len)
        market_feed_zone = animated_ticker + (" " * padding_needed)
        
        health_color = self.primary if self.node_health == "STABLE" else C_AMBER if self.node_health == "BOOTING" else C_RED
        P = self.primary; A = self.accent; R = C_RESET; D = C_DARK; W = C_WHITE

        height_display = "CONNECTING..." if self.current_height == 0 else str(self.current_height)

        print(f"{P}┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐{R}")
        print(f"{P}│{R}  {W}VECTAS QUANTUM INDUSTRIAL SECURITY MONITOR{R}  {D}│{R}  {A}Pipeline Node Core Infrastructure Engine v4.1{R}                      {self.get_spinner()} {W}NET-SYS: ONLINE{R}                  {P}│{R}")
        print(f"{P}├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤{R}")
        print(f"{P}│{R} {W}TARGET INFRA:{R} {C_AMBER}{self.target['name'].ljust(22)}{R} {D}│{R} {W}BLOCKS PARSED :{R} {P}{str(self.blocks_parsed).ljust(8)}{R} {D}│{R} {W}BASE FEE/GAS:{R} {A}{str(self.base_gas).ljust(11)}{R} {D}│{R} {W}MARKET FEED:{R} {market_feed_zone} {P}│{R}")
        print(f"{P}│{R} {W}LEDGER HEIGHT:{R} {P}{height_display.ljust(22)}{R} {D}│{R} {W}TXS PROCESSED :{R} {P}{str(self.txs_processed).ljust(8)}{R} {D}│{R} {W}PIPELINE HTH:{R} {health_color}{self.node_health.ljust(11)}{R} {D}│{R} {W}SYS CON-CODE:{R} {A}EVM-NATIVE-RAW.X64{R}        {P}│{R}")
        print(f"{P}├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤{R}")
        print(f"{P}│{R} {D}[{R} {W}NODE RUNTIME:{R} {P}{str(uptime).rjust(4)}s{R} {D}|{R} {W}DESIRED TICK:{R} {C_AMBER}{self.target['speed'].ljust(5)}{R} {D}]{R}  {W}GAS VOLUME METER:{R} {D}[{R}{A}{self.gas_weight_bar}{R}{D}]{R}   {self.get_signal_bar().ljust(52)} {P}│{R}")
        print(f"{P}├──────────────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────┤{R}")
        print(f"{P}│{R} {W}DECODED LIVE MEMPOOL RAW INGESTION STREAM{R}                                    {P}│{R} {W}HIGH-CRITICAL CYBER THREAT LOGS & MALICIOUS EVENTS{R}                                           {P}│{R}")
        print(f"{P}├──────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────┤{R}")
        
        for i in range(14):
            left_pane = self.payload_stream[i] if i < len(self.payload_stream) else ""
            right_pane = self.threat_logs[i] if i < len(self.threat_logs) else ""
            
            if "Awaiting high-speed" in left_pane and (i + self.frame) % 4 == 0:
                left_pane = f"{D}Listening for incoming block state distribution vectors... {A}░▒▓{R}"

            left_len = self.clean_ansi_len(left_pane)
            right_len = self.clean_ansi_len(right_pane)
            
            pad_left = " " * max(0, 76 - left_len)
            pad_right = " " * max(0, 83 - right_len)

            print(f"{P}│{R} {left_pane}{pad_left} {P}│{R} {right_pane}{pad_right} {P}│{R}")
            
        print(f"{P}└──────────────────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────┘{R}")
        print(f" {D}[ SEC_ENG // AUTH_SIG // SUDAIS_AHMAD_DURANI_KALI_NODE // LOCALHOST_VERIFIED ]{R}")

    async def send_discord_alert(self, session, sig_name, tx_hash, sender, target, value):
        if not DISCORD_WEBHOOK_URL or "YOUR_DISCORD_WEBHOOK" in DISCORD_WEBHOOK_URL:
            return
            
        payload = {
            "embeds": [{
                "title": f"🚨 EXPLOITFOOTPRINT MATCH: {sig_name}",
                "color": 15158332, 
                "fields": [
                    {"name": "Transaction Hash", "value": f"`{tx_hash}`", "inline": False},
                    {"name": "Threat Actor", "value": f"`{sender}`", "inline": True},
                    {"name": "Target Address", "value": f"`{target}`", "inline": True},
                    {"name": "Payload Value", "value": f"`{value:.4f} {self.target['sym']}`", "inline": True}
                ],
                "footer": {"text": f"Vectas Intel Guard Node • {datetime.now().strftime('%H:%M:%S')}"}
            }]
        }
        try:
            async with session.post(DISCORD_WEBHOOK_URL, json=payload, timeout=3) as resp:
                pass
        except Exception:
            pass 

    async def hot_reload_signatures(self):
        while True:
            try:
                if os.path.exists(SIGNATURES_FILE):
                    if os.path.getsize(SIGNATURES_FILE) == 0:
                        await asyncio.sleep(2.0)
                        continue
                        
                    mtime = os.path.getmtime(SIGNATURES_FILE)
                    if mtime > self.last_sig_mtime:
                        with open(SIGNATURES_FILE, 'r') as f:
                            data = json.load(f)
                            
                            if isinstance(data, list):
                                new_sigs = {
                                    item["selector"].lower().strip(): item["name"] 
                                    for item in data if isinstance(item, dict) and "selector" in item and "name" in item
                                }
                            elif isinstance(data, dict):
                                new_sigs = {k.lower().strip(): v for k, v in data.items()}
                            else:
                                new_sigs = {}

                            self.signatures = new_sigs
                            self.last_sig_mtime = mtime
                            self.add_log(f"Hot-Reload Complete: {len(self.signatures)} active threat vectors loaded.", "INFO")
                else:
                    if self.last_sig_mtime == 0:
                        self.signatures = {}
                        self.last_sig_mtime = 1
                        self.add_log("Signatures database absent. Running in raw zero-knowledge mode.", "INFO")
            except json.JSONDecodeError:
                self.add_log("Hot-Reload Fault: signatures.json contains invalid JSON syntax.", "ERROR")
            except Exception as e:
                self.add_log(f"Hot-Reload Fault: {str(e)[:40]}", "ERROR")
                
            await asyncio.sleep(2.0)

    async def track_live_prices(self, session):
        coin_ids = "bitcoin,ethereum,polygon,solana"
        endpoint = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=usd"
        
        while True:
            try:
                async with session.get(endpoint, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        prices = {
                            "BTC/USD": data.get("bitcoin", {}).get("usd", 0),
                            "ETH/USD": data.get("ethereum", {}).get("usd", 0),
                            "POL/USD": data.get("polygon", {}).get("usd", 0),
                            "SOL/USD": data.get("solana", {}).get("usd", 0)
                        }
                        
                        for asset_item in self.crypto_assets:
                            ticker = asset_item["asset"]
                            if ticker in prices and prices[ticker] > 0:
                                val = prices[ticker]
                                fmt_val = f"${val:,.2f}" if val >= 1.0 else f"${val:,.4f}"
                                asset_item["status"] = fmt_val
                                
                        self.add_log("Market feed matrix telemetry successfully updated.", "INFO")
            except Exception:
                pass
            await asyncio.sleep(45)

    async def fetch_block_data(self):
        headers = {"User-Agent": "VactasIndustrialAgent/4.1", "Content-Type": "application/json"}
        async with aiohttp.ClientSession(headers=headers) as session:
            self.node_health = "STABLE"
            self.add_log("Network backend communications stack fully attached.", "INFO")
            
            price_task = asyncio.create_task(self.track_live_prices(session))
            reload_task = asyncio.create_task(self.hot_reload_signatures())
            
            try:
                while True:
                    try:
                        payload = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
                        async with session.post(self.target["url"], json=payload, timeout=4) as response:
                            if response.status == 200:
                                raw_text = await response.text()
                                data = json.loads(raw_text)
                                hex_height = data.get("result")
                                
                                if hex_height:
                                    int_height = int(hex_height, 16)
                                    
                                    if self.current_height == 0 or int_height > self.current_height:
                                        self.current_height = int_height
                                        self.blocks_parsed += 1
                                        self.add_log(f"NETWORK EVENT DETECTED: NEW LEDGER BLOCK #{int_height}", "INFO")
                                        
                                        tx_payload = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [hex_height, True], "id": 2}
                                        async with session.post(self.target["url"], json=tx_payload, timeout=4) as tx_resp:
                                            if tx_resp.status == 200:
                                                raw_tx_text = await tx_resp.text()
                                                tx_data = json.loads(raw_tx_text)
                                                block_result = tx_data.get("result") or {}
                                                transactions = block_result.get("transactions") or []
                                                
                                                if "baseFeePerGas" in block_result and block_result["baseFeePerGas"]:
                                                    gwei_gas = int(block_result["baseFeePerGas"], 16) / 10**9
                                                    self.base_gas = f"{gwei_gas:.2f} Gwei"
                                                    if gwei_gas < 40:
                                                        self.gas_weight_bar = "■■■■░░░░░░░░░░░░░░"
                                                    elif gwei_gas < 120:
                                                        self.gas_weight_bar = "■■■■■■■■■■░░░░░░░░"
                                                    else:
                                                        self.gas_weight_bar = "■■■■■■■■■■■■■■■■■■"
                                                
                                                has_transactions = len(transactions) > 0
                                                for tx in transactions:
                                                    tx_hash = tx.get("hash", "0x0000...")
                                                    tx_from = tx.get("from", "0x0000...")
                                                    tx_to = tx.get("to") or "Contract Deployment"
                                                    tx_input = tx.get("input", "0x")
                                                    val_wei = int(tx.get("value", "0x0"), 16)
                                                    val_eth = val_wei / 10**18
                                                    
                                                    self.txs_processed += 1
                                                    
                                                    method_selector = tx_input[:10].lower()
                                                    if method_selector in self.signatures:
                                                        sig_name = self.signatures[method_selector]
                                                        self.add_log(f"EXPLOIT SIGNATURE MATCH: {sig_name} on hash {tx_hash[:10]}", "THREAT")
                                                        
                                                        async_task = asyncio.create_task(self.send_discord_alert(
                                                            session, sig_name, tx_hash, tx_from, tx_to, val_eth
                                                        ))
                                                    
                                                    if has_transactions:
                                                        self.add_payload(f"SIG [{tx_hash[:8]}] {tx_from[:8]} -> {tx_to[:8]} | AMNT: {val_eth:.3f} {self.target['sym']}")
                                                    
                                                    if val_eth > 100.0:
                                                        self.add_log(f"HIGH VOLUME LIQUIDITY DRIFT: {val_eth:.2f} {self.target['sym']} via hash {tx_hash[:10]}", "THREAT")
                                                        
                                                self.add_log(f"Ingested {len(transactions)} transaction payloads from block #{int_height}", "INFO")
                            else:
                                self.node_health = "DEGRADED"
                                self.add_log(f"Ingest interface rejected RPC connection. HTTP Code: {response.status}", "ERROR")
                                
                    except Exception as e:
                        self.node_health = "OFFLINE"
                        self.add_log(f"Core Pipe Disconnect Exception: {str(e)[:45]}", "ERROR")
                    
                    self.draw_ui()
                    await asyncio.sleep(0.5)
            finally:
                price_task.cancel()
                reload_task.cancel()

def show_boot_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[1;36m┌────────────────────────────────────────────────────────────────────────┐\033[0m")
    print("\033[1;36m│\033[0m  \033[1;37mVECTAS DEFI SECURITY SYSTEM INITIALIZATION INTERFACE\033[0m                \033[1;36m│\033[0m")
    print("\033[1;36m├────────────────────────────────────────────────────────────────────────┤\033[0m")
    print("\033[1;36m│\033[0m  \033[1;30mSelect target blockchain infrastructure network pipe:\033[0m                 \033[1;36m│\033[0m")
    print("\033[1;36m│\033[0m                                                                        \033[1;36m│\033[0m")
    print("\033[1;36m│\033[0m  \033[1;35m[1]\033[0m \033[1;37mEthereum Mainnet Archetype (ETH URL Profile)\033[0m                        \033[1;36m│\033[0m")
    print("\033[1;36m│\033[0m  \033[1;36m[2]\033[0m \033[1;37mArbitrum One High-Speed Rollup (ARB URL Profile)\033[0m                    \033[1;36m│\033[0m")
    print("\033[1;36m│\033[0m  \033[1;32m[3]\033[0m \033[1;37mPolygon Proof-of-Stake Network (POL URL Profile)\033[0m                    \033[1;36m│\033[0m")
    print("\033[1;36m│\033[0m                                                                        \033[1;36m│\033[0m")
    print("\033[1;36m└────────────────────────────────────────────────────────────────────────┘\033[0m")
    try:
        choice = input("\033[1;37m ENGINE_BOOT_LOG // Enter pipeline choice [1-3]: \033[0m").strip()
        if choice in CHANNELS:
            return CHANNELS[choice]
        else:
            print("\033[1;31m[!] Invalid selection. Defaulting to Polygon PoS Core.\033[0m")
            time.sleep(1.5)
            return CHANNELS["3"]
    except (KeyboardInterrupt, SystemExit):
        print("\n\033[1;31m[!] Engine boot sequence canceled.\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    if os.name == 'nt':
        os.system('mode con: cols=172 lines=26')
        
    selected_net = show_boot_menu()
    engine = VectasEngine(selected_net)
    try:
        with asyncio.Runner() as runner:
            runner.run(engine.fetch_block_data())
    except KeyboardInterrupt:
        print(f"\n\033[1;31m[!] Vectas Infrastructure Cluster cleanly detached.{C_RESET}")

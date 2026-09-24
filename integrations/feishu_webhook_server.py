#!/usr/bin/env python3
"""
integrations/feishu_webhook_server.py — Production-Ready Feishu Webhook & Event Server
Provides a standalone HTTP gateway for Feishu (Lark) Bot integration:
  1. Handshakes URL verification challenge for Feishu Open Platform (`url_verification`).
  2. Receives and processes event callbacks (`im.message.receive_v1`).
  3. Provides testing REST endpoint `/api/feishu/chat` for manual or web triggering.
  4. Optionally replies directly back to Feishu chats via Open API or custom bot Webhook.

Zero external dependencies (uses standard library `http.server` & `urllib`).
"""

import sys
import os
import json
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integrations.feishu_bot_adapter import FeishuBotAdapter

# Global Adapter instance
ADAPTER = FeishuBotAdapter()


class FeishuWebhookHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for Feishu Events & Webhooks."""

    def do_GET(self):
        """Health check endpoint."""
        if self.path in ["/", "/health", "/api/health"]:
            self._send_json({
                "status": "healthy",
                "service": "via54ADIdeahub Feishu Bot Gateway",
                "version": "2.13.0",
                "endpoints": {
                    "event_webhook": "POST /webhook",
                    "chat_api": "POST /api/feishu/chat",
                    "health": "GET /health"
                }
            })
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle incoming Feishu events and webhook payloads."""
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length).decode("utf-8")

        try:
            body = json.loads(raw_body) if raw_body else {}
        except Exception:
            self._send_json({"error": "Invalid JSON body"}, status=400)
            return

        # 1. Feishu URL Verification Challenge
        if body.get("type") == "url_verification":
            challenge = body.get("challenge", "")
            print(f"🔒 [Feishu Handshake] Responding to url_verification challenge: {challenge}")
            self._send_json({"challenge": challenge})
            return

        # 2. REST API for Chat & Direct Invocations (/api/feishu/chat)
        if self.path in ["/api/feishu/chat", "/chat"]:
            msg = body.get("message") or body.get("text") or body.get("query", "")
            if not msg:
                self._send_json({"error": "Missing 'message' in request body"}, status=400)
                return

            print(f"💬 [REST Request] User: {msg}")
            result = ADAPTER.handle_feishu_message(msg)

            # Optional webhook push
            webhook_url = body.get("webhook_url") or os.environ.get("FEISHU_WEBHOOK_URL", "")
            if webhook_url:
                push_res = ADAPTER.send_to_webhook(webhook_url, result["interactive_card"])
                result["webhook_push_status"] = push_res

            self._send_json(result)
            return

        # 3. Feishu Event Subscription (/webhook)
        # Event Schema 2.0: header.event_type == 'im.message.receive_v1'
        header = body.get("header", {})
        event_type = header.get("event_type") or body.get("event", {}).get("type", "")

        if event_type == "im.message.receive_v1":
            event = body.get("event", {})
            message = event.get("message", {})
            msg_type = message.get("message_type")
            chat_id = message.get("chat_id", "")
            sender_id = event.get("sender", {}).get("sender_id", {}).get("open_id", "")

            user_text = ""
            if msg_type == "text":
                try:
                    content_json = json.loads(message.get("content", "{}"))
                    user_text = content_json.get("text", "")
                except Exception:
                    user_text = message.get("content", "")

            print(f"📩 [Feishu Event] Received message from user {sender_id} in chat {chat_id}: '{user_text}'")

            if user_text:
                # Process message
                adapter_res = ADAPTER.handle_feishu_message(user_text, user_id=sender_id, chat_id=chat_id)

                # If webhook_url is configured in env, push card back
                webhook_url = os.environ.get("FEISHU_WEBHOOK_URL", "")
                if webhook_url:
                    ADAPTER.send_to_webhook(webhook_url, adapter_res["interactive_card"])

                self._send_json({
                    "status": "success",
                    "action": adapter_res["action"],
                    "card_markdown": adapter_res["card_markdown"]
                })
            else:
                self._send_json({"status": "ignored", "reason": "non_text_message"})
            return

        # 4. Fallback for custom / legacy events
        text_payload = body.get("text") or body.get("content", "")
        if text_payload:
            result = ADAPTER.handle_feishu_message(text_payload)
            self._send_json(result)
        else:
            self._send_json({"status": "received", "event_type": event_type})

    def _send_json(self, data: Dict[str, Any], status: int = 200):
        """Send JSON HTTP response."""
        resp = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(resp)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(resp)

    def log_message(self, format, *args):
        """Custom concise logging."""
        sys.stderr.write(f"🌐 [Feishu Webhook] {self.address_string()} - {format % args}\n")


def run_server(host: str = "0.0.0.0", port: int = 8088):
    """Start Feishu Webhook HTTP Server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, FeishuWebhookHandler)
    print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║   🚀 via54 Feishu Bot Webhook Gateway is running on port {port:<5}         ║
║   - Health Check:    GET  http://localhost:{port}/health                   ║
║   - Feishu Callback: POST http://localhost:{port}/webhook                  ║
║   - Direct Chat API: POST http://localhost:{port}/api/feishu/chat          ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Feishu Webhook server gracefully...")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="via54 Feishu Webhook Server")
    parser.add_argument("--host", default="0.0.0.0", help="Binding host (default 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8088, help="Binding port (default 8088)")
    args = parser.parse_args()
    run_server(host=args.host, port=args.port)

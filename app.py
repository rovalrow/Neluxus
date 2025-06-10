from flask import Flask, render_template, request, jsonify, redirect
from supabase import create_client
import uuid

app = Flask(__name__)

# Set your Supabase credentials
SUPABASE_URL = "https://ikxxvgflnpfyncnaqfxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlreHh2Z2ZsbnBmeW5jbmFxZnh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYxOTE3NTMsImV4cCI6MjA2MTc2Nzc1M30.YiF46ggItUYuKLfdD_6oOxq2xGX7ac6yqqtEGeM_dg8"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def root_route():
    return render_template("webhook.html")
    
@app.route('/generate')
def generate_webhook():
    existing = supabase.table("temp_webhooks").select("*").execute().data
    if existing:
        return redirect(f"/webhook/{existing[0]['id']}")

    webhook_id = str(uuid.uuid4())
    supabase.table("temp_webhooks").insert({"id": webhook_id}).execute()
    return redirect(f"/webhook/{webhook_id}")

@app.route('/webhook/<webhook_id>', methods=["GET", "POST"])
def webhook(webhook_id):
    if request.method == "POST":
        data = request.json
        content = data.get("content", "")
        embed = data.get("embeds", [{}])[0]

        lines = []
        if content:
            lines.append(content.strip())

        if embed.get("title"):
            lines.append(f"**{embed['title']}**")

        for field in embed.get("fields", []):
            lines.append(f"{field.get('name', '')}\n{field.get('value', '')}")

        if embed.get("footer", {}).get("text"):
            lines.append(f"_Footer: {embed['footer']['text']}_")

        final_text = "\n\n".join(lines)

        supabase.table("webhook_messages").insert({
            "webhook_id": webhook_id,
            "message": final_text
        }).execute()

        return jsonify({"status": "ok"})

    result = supabase.table("webhook_messages").select("*").eq("webhook_id", webhook_id).execute()
    messages = result.data if result.data else []
    return render_template("webhook.html", messages=messages)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)

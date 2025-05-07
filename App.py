from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime

# ------------------------------------------------------------------
# 1) configuration
#    مسیر فایل اکسل از متغیر محیطی خوانده می‌شود (در Render: EXCEL_PATH=/data/redata.xlsx)
# ------------------------------------------------------------------
EXCEL_PATH = os.environ.get("EXCEL_PATH", "redata.xlsx")
COLUMNS    = ["timestamp", "specialty", "text", "relation"]

# ------------------------------------------------------------------
# 2) Flask app + CORS
# ------------------------------------------------------------------
app = Flask(__name__)
# همه Originها مجازند؛ بعد از انتشار فرانت می‌توانید "https://username.github.io" را جایگزین "*"
CORS(app, resources={r"/submit": {"origins": "*"}})

# ------------------------------------------------------------------
# 3) endpoint: POST /submit
# ------------------------------------------------------------------
@app.route("/submit", methods=["POST"])
def save_data():
    """
    دریافت JSON از فرم و افزودن آن به فایل اکسل.
    """
    try:
        data = request.get_json(force=True)
        if not {"specialty", "text", "relation"} <= data.keys():
            return jsonify(status="error", message="fields missing"), 400

        new_row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "specialty": data["specialty"],
            "text"     : data["text"],
            "relation" : data["relation"]
        }

        # اطمینان از وجود پوشه مقصد
        os.makedirs(os.path.dirname(EXCEL_PATH) or ".", exist_ok=True)

        # اضافه کردن ردیف
        if not os.path.exists(EXCEL_PATH):
            df = pd.DataFrame([new_row], columns=COLUMNS)
        else:
            df = pd.read_excel(EXCEL_PATH, engine="openpyxl")
            df = pd.concat([df, pd.DataFrame([new_row])],
                           ignore_index=True)

        df.to_excel(EXCEL_PATH, index=False, engine="openpyxl")
        return jsonify(status="ok"), 200

    except Exception as e:
        print("[ERROR]", e)
        return jsonify(status="error", message=str(e)), 500

# ------------------------------------------------------------------
# 4) endpoint: GET /download  →  دانلود فایل اکسل
# ------------------------------------------------------------------
@app.route("/download", methods=["GET"])
def download():
    if os.path.exists(EXCEL_PATH):
        return send_file(EXCEL_PATH, as_attachment=True)
    return "file not found", 404

# ------------------------------------------------------------------
# 5) run
# ------------------------------------------------------------------
if __name__ == "__main__":
    port   = int(os.environ.get("PORT", 5000))   # Render PORT
    debug  = bool(os.environ.get("FLASK_DEBUG", False))
    app.run(host="0.0.0.0", port=port, debug=debug)

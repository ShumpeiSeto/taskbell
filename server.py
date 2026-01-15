# taskbell内に__init__があればそれを実行してappがあればそれを返す
from taskbell import create_app
import os

# os.environ["LANG"] = "ja_JP.UTF-8"
# os.environ["LC_ALL"] = "C.UTF-8"

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
    # app.run()
    # Render.comが提供するポートを取得（なければ5000）
    # port = int(os.environ.get("PORT", 5000))
    # 本番環境用の設定
    # app.run(host="0.0.0.0", port=port, debug=False)

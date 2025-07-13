# taskbell内に__init__があればそれを実行してappがあればそれを返す
from taskbell import app
import os

if __name__ == "__main__":
    # app.run()
    # Render.comが提供するポートを取得（なければ5000）
    port = int(os.environ.get("PORT", 5000))
    # 本番環境用の設定
    app.run(host="0.0.0.0", port=port, debug=False)

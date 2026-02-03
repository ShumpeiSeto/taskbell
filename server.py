# taskbell内に__init__があればそれを実行してappがあればそれを返す
from taskbell import create_app
import os

app = create_app()

if __name__ == "__main__":
    # app.run(debug=True)
    # Railway用：環境変数からポートを取得し、外部接続(0.0.0.0)を許可する
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

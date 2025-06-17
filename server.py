# taskbell内に__init__があればそれを実行してappがあればそれを返す
from taskbell import app

if __name__ == "__main__":
    app.run()

将来的なGo移行を意識し、ここで厳密な型定義を行います。

- manifest.py: manifest.yaml のデータ構造を定義。
- メリット: init や apply の際、不正なYAML設定を即座にエラーとして弾くことができます。

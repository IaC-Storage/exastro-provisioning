Step 2: build-schema の核となる部分です。

- `defaults/main.yml` を読み込み、コメント行（`# @cdk-type`）を抽出するロジックをここに集約します。
- 正規表現や `ruamel.yaml` を使用して、コメントを保持したまま解析を行います。

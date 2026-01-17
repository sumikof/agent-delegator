# agent-delegateプロジェクトのPYTHONPATH設定

## 概要

PYTHONPATHが正常に設定され、agent-delegateプロジェクトの`src`ディレクトリが含まれるようになりました。これにより、Pythonは`src`ディレクトリ構造からモジュールをインポートできるようになります。

## 行われた設定変更

### 1. pyproject.tomlの更新

`pyproject.toml`ファイルには既に正しい設定がありました：

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

これは、setuptoolsに`src`ディレクトリからパッケージを見つけるように指示します。

さらに、pytest設定がsrcディレクトリを含むように更新されました：

```toml
[tool.pytest.ini_options]
pythonpath = [".", "src"]
```

### 2. 環境設定

PYTHONPATH設定を含む`.env`ファイルを作成しました：

```bash
# agent-delegateプロジェクトの環境変数
# モジュールインポートのためにsrcディレクトリを含むようにPYTHONPATHを設定
PYTHONPATH=/workspace/src:$PYTHONPATH
```

### 3. setup.py設定

`setup.py`ファイルには既に正しい設定がありました：

```python
packages=find_packages(where="src", exclude=["tests", "tests.*"]),
package_dir={"": "src"},
```

## 検証

設定が正しく動作することが検証されました：

1. **直接インポートテスト**：
   ```bash
   PYTHONPATH=/workspace/src:$PYTHONPATH python3 -c "import orchestrator; print('Success')"
   ```

2. **モジュールインポートテスト**：
   ```bash
   PYTHONPATH=/workspace/src:$PYTHONPATH python3 -c "import orchestrator.cli; print('Success')"
   ```

3. **テストスクリプト**：srcディレクトリからすべてのモジュールを正常にインポートする`/workspace/test_pythonpath.py`を作成しました。

## 使用方法

### 開発時

開発中に設定されたPYTHONPATHを使用するには：

```bash
# オプション1：.envファイルをソース
source /workspace/.env
python3 your_script.py

# オプション2：PYTHONPATHを明示的に設定
PYTHONPATH=/workspace/src:$PYTHONPATH python3 your_script.py

# オプション3：スクリプト内でsys.pathに追加
import sys
sys.path.insert(0, '/workspace/src')
```

### テスト時

pytest設定は、テスト実行時に自動的にsrcディレクトリをPythonパスに含めます。

### インストール時

パッケージは開発モードでインストールできます（pipの問題が解決された場合）：

```bash
pip install -e .
```

## トラブルシューティング

インポートエラーが発生した場合：

1. **PYTHONPATHを確認**：
   ```bash
   echo $PYTHONPATH
   ```

2. **Pythonパスを確認**：
   ```python
   import sys
   print(sys.path)
   ```

3. **依存関係がインストールされていることを確認**：
   ```bash
   pip install -r requirements.txt
   ```

## 変更/作成されたファイル

- `pyproject.toml` - pytestのpythonpath設定を更新
- `.env` - 環境設定ファイルを作成
- `test_pythonpath.py` - 検証テストスクリプトを作成
- `PYTHONPATH_CONFIGURATION.md` - このドキュメントファイル

PYTHONPATHは、srcベースのプロジェクト構造で動作するように正しく設定されました。
# テスト環境セットアップガイド

## 概要

このドキュメントは、エージェントデリゲーションシステムのパイロットテスト用テスト環境のセットアップ手順を説明します。

## 要件

### ハードウェア要件

| コンポーネント | 最小要件 | 推奨要件 |
|-------------|----------|----------|
| CPU | 4コア | 8コア以上 |
| メモリ | 8GB | 16GB以上 |
| ストレージ | 50GB SSD | 100GB以上 SSD |
| ネットワーク | 100Mbps | 1Gbps以上 |

### ソフトウェア要件

#### 基本ソフトウェア
- OS: Ubuntu 22.04 LTS
- Python: 3.10以上
- Git: 2.30以上
- Docker: 20.10以上
- Docker Compose: 1.29以上

#### オプションソフトウェア
- Kubernetes: 1.25以上 (クラウドネイティブテスト用)
- Helm: 3.8以上 (Kubernetesデプロイメント用)
- Terraform: 1.2以上 (インフラプロビジョニング用)

## セットアップ手順

### 1. システムの更新

```bash
# システムパッケージの更新
sudo apt update && sudo apt upgrade -y

# 必要なパッケージのインストール
sudo apt install -y curl wget git build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev \
    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl
```

### 2. Python環境のセットアップ

```bash
# Python 3.10のインストール
sudo apt install -y python3.10 python3.10-dev python3.10-venv

# Python仮想環境の作成
python3.10 -m venv ~/agent-delegation-venv
source ~/agent-delegation-venv/bin/activate

# 必要なPythonパッケージのインストール
pip install --upgrade pip setuptools wheel
pip install agent-delegation[all]
```

### 3. Docker環境のセットアップ

```bash
# Dockerのインストール
curl -fsSL https://get.docker.com | sudo sh

# 現在のユーザーをdockerグループに追加
sudo usermod -aG docker $USER
newgrp docker

# Docker Composeのインストール
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Dockerの動作確認
docker --version
docker-compose --version
```

### 4. Kubernetes環境のセットアップ (オプション)

```bash
# Kubernetesツールのインストール
sudo apt install -y kubectl

# Minikubeのインストール
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Minikubeクラスターの起動
minikube start --driver=docker --cpus=4 --memory=8g

# Helmのインストール
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### 5. プロジェクトのセットアップ

```bash
# プロジェクトのクローン
git clone https://github.com/your-org/agent-delegation.git
cd agent-delegation

# 依存関係のインストール
pip install -e .

# 環境変数の設定
cp .env.example .env
# .envファイルを編集して必要な設定を追加
```

### 6. テストデータの準備

```bash
# テストデータのダウンロード
mkdir -p test_data
cd test_data

# サンプルプロジェクトのダウンロード
git clone https://github.com/your-org/sample-project-small.git
git clone https://github.com/your-org/sample-project-medium.git
git clone https://github.com/your-org/sample-project-large.git

# テストシナリオの準備
cp ../examples/test-scenarios/*.yaml .
```

### 7. テストツールのセットアップ

```bash
# テストツールのインストール
pip install pytest pytest-cov pytest-benchmark

# パフォーマンスモニタリングツールのインストール
sudo apt install -y htop iotop iftop sysstat

# ログ収集ツールのインストール
pip install structlog
```

## 環境の検証

### システムの検証

```bash
# システム情報の確認
uname -a
cat /etc/os-release

# リソースの確認
free -h
df -h
lscpu
```

### ソフトウェアの検証

```bash
# Python環境の検証
python --version
pip --version

# Docker環境の検証
docker --version
docker-compose --version
docker run hello-world

# Kubernetes環境の検証 (オプション)
kubectl version --client
minikube status
helm version
```

### プロジェクトの検証

```bash
# プロジェクトの依存関係の検証
pip check

# プロジェクトのテストの実行
pytest tests/unit/ -v

# プロジェクトの動作検証
python -m orchestrator.cli --help
```

## 環境の設定

### 環境変数

```bash
# 必要な環境変数の設定
cat << 'EOF' > .env
export AGENT_DELEGATION_ENV=test
export LOG_LEVEL=DEBUG
export MAX_WORKERS=4
export RESOURCE_LIMIT_CPU=0.8
export RESOURCE_LIMIT_MEMORY=0.7
export TEST_MODE=true
EOF

source .env
```

### ロギングの設定

```bash
# ロギングの設定
cat << 'EOF' > logging_config.yaml
version: 1
formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    formatter: default
    level: DEBUG
  file:
    class: logging.FileHandler
    filename: test_logs/agent_delegation.log
    formatter: detailed
    level: INFO

loggers:
  agent_delegation:
    level: DEBUG
    handlers: [console, file]
    propagate: no

root:
  level: WARNING
  handlers: [console]
EOF
```

### パフォーマンスモニタリングの設定

```bash
# パフォーマンスモニタリングの設定
cat << 'EOF' > monitoring_config.yaml
metrics:
  collection_interval: 10
  retention_days: 7
  enabled_metrics:
    - cpu_usage
    - memory_usage
    - disk_io
    - network_io
    - task_processing_time
    - agent_response_time

alerts:
  cpu_threshold: 80
  memory_threshold: 75
  disk_threshold: 90
  response_time_threshold: 5000
EOF
```

## 環境のバックアップと復元

### バックアップ手順

```bash
# 環境のバックアップ
mkdir -p backups
tar -czvf backups/test_environment_$(date +%Y%m%d).tar.gz \
    .env \
    logging_config.yaml \
    monitoring_config.yaml \
    test_data/

# データベースのバックアップ (該当する場合)
mongodb_dump --out backups/mongodb_$(date +%Y%m%d)
```

### 復元手順

```bash
# 環境の復元
tar -xzvf backups/test_environment_latest.tar.gz

# データベースの復元 (該当する場合)
mongodb_restore backups/mongodb_latest
```

## トラブルシューティング

### 一般的な問題

1. **Dockerの権限エラー**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. **Python仮想環境の問題**
   ```bash
   rm -rf ~/agent-delegation-venv
   python3.10 -m venv ~/agent-delegation-venv
   source ~/agent-delegation-venv/bin/activate
   ```

3. **依存関係の問題**
   ```bash
   pip install --upgrade --force-reinstall -e .
   ```

### パフォーマンスの問題

1. **リソース不足**
   - 使用していないアプリケーションを終了
   - システムのリソースを増強
   - タスクの並列度を減らす

2. **ネットワークの問題**
   - ネットワーク接続を確認
   - プロキシ設定を確認
   - ファイアウォール設定を確認

## 次のステップ

1. **テスト環境の検証**: 環境が正しくセットアップされていることを確認
2. **テストデータの準備**: テスト用のデータを準備
3. **テストツールの設定**: テストツールを設定
4. **テストの実施**: パイロットテストを実施
5. **結果の分析**: テスト結果を分析

このテスト環境セットアップガイドは、エージェントデリゲーションシステムのパイロットテストを実施するための基盤を提供します。
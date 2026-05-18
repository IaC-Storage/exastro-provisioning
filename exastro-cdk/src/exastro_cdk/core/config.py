import os
from dataclasses import dataclass


class ConfigurationError(RuntimeError):
    """必要な環境変数が未設定の場合に送出する."""


@dataclass(frozen=True)
class ExastroConfig:
    """Exastro接続設定.

    Attributes:
        base_url: Exastro ベースURL (例: http://192.168.10.70:80)
        organization: オーガナイゼーションID
        workspace: ワークスペースID (ITAClient認証用フォールバック)
        refresh_token: リフレッシュトークン
    """

    base_url: str
    organization: str
    workspace: str
    refresh_token: str


def load_config() -> ExastroConfig:
    """環境変数から ExastroConfig を読み込む.

    Returns:
        読み込んだ ExastroConfig インスタンス

    Raises:
        ConfigurationError: 必須環境変数が未設定の場合
    """

    def _require(name: str) -> str:
        val = os.getenv(name)
        if not val:
            raise ConfigurationError(
                f"環境変数 '{name}' が設定されていません。"
                f" EXASTRO_BASE_URL, EXASTRO_ORGANIZATION,"
                f" EXASTRO_WORKSPACE, REFRESH_TOKEN を設定してください。"
            )
        return val

    return ExastroConfig(
        base_url=_require("EXASTRO_BASE_URL"),
        organization=_require("EXASTRO_ORGANIZATION"),
        workspace=_require("EXASTRO_WORKSPACE"),
        refresh_token=_require("REFRESH_TOKEN"),
    )

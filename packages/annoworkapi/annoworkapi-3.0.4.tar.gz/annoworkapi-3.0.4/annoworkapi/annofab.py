"""
外部連携システム"Annofab"に依存した関数やクラスを定義しています。
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Collection, Optional

from annoworkapi import AnnoworkApi

ANNOFAB_PROJECT_URL_PREFIX = "https://annofab.com/projects/"
"""Annofabのプロジェクトを表すURLのプレフィックス"""


def get_annofab_project_id_from_url(url: str) -> Optional[str]:
    """ジョブの外部連携情報に設定されたURLからAnnofabプロジェクトのproject_idを取得します。

    Args:
        url: ジョブの外部連携情報であるURL

    Returns:
        Annofabプロジェクトのproject_id。URLからproject_idを取得できない場合は、Noneを返します。
    """
    url = url.strip()
    if not url.startswith(ANNOFAB_PROJECT_URL_PREFIX):
        return None
    tmp = url[len(ANNOFAB_PROJECT_URL_PREFIX) :]
    tmp_array = tmp.split("/")
    if len(tmp_array) == 0:
        # https://annofab.com/projects/foo のケース（末尾にスラッシュなし）
        return tmp
    # https://annofab.com/projects/foo/ のケース（末尾にスラッシュあり）
    return tmp_array[0]


class AnnofabWrapper:
    """
    Annofabに依存したAPIのwrapperです。

    Args:
        api: AnnoworkApi Instance
    """

    def __init__(self, api: AnnoworkApi):
        self.api = api

    def get_jobs_by_annofab_project_id(
        self, workspace_id: str, annofab_project_ids: Collection[str]
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Annofabのproject_idに紐づくジョブを取得します。

        Args:
            workspace_id: ワークスペースID
            annofab_project_ids: Annofabのproject_idsのcollection

        Returns:
            keyがannofabのproject_id, valueがジョブのlistであるdict
        """
        annofab_project_id_set = set(annofab_project_ids)
        all_jobs = self.api.get_jobs(workspace_id)
        result = defaultdict(list)

        def get_annofab_project_id_from_job(job: dict[str, Any]) -> Optional[str]:
            url = job["external_linkage_info"].get("url")
            if url is not None:
                return get_annofab_project_id_from_url(url)
            return None

        for job in all_jobs:
            annofab_project_id = get_annofab_project_id_from_job(job)
            if annofab_project_id is not None and annofab_project_id in annofab_project_id_set:
                result[annofab_project_id].append(job)

        return result

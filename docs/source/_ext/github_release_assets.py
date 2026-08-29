import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective


ASSET_NAME_PATTERN = re.compile(
    r"^(?P<run_id>\d+)-(?P<attempt>\d+)-(?P<scenario>.+)\.csv$"
)


def _request_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "factory-creator-sphinx",
    }

    return headers


def _repository_parts(repository):
    parts = repository.split("/", maxsplit=1)

    if len(parts) != 2 or not all(parts):
        raise ValueError("Repository must use the OWNER/REPOSITORY format.")
    
    return parts[0], parts[1]


def load_release(
    repository,
    tag,
    opener=urlopen,
):
    owner, repository_name = _repository_parts(repository)

    api_url = (
        "https://api.github.com/repos/"
        f"{quote(owner, safe='')}/{quote(repository_name, safe='')}"
        f"/releases/tags/{quote(tag, safe='')}"
    )

    request = Request(api_url, headers=_request_headers())

    with opener(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def load_release_assets(
    repository,
    release_id,
    opener=urlopen,
):
    owner, repository_name = _repository_parts(repository)
    assets = []
    page = 1

    while True:
        api_url = (
            "https://api.github.com/repos/"
            f"{quote(owner, safe='')}/{quote(repository_name, safe='')}"
            f"/releases/{release_id}/assets?per_page=100&page={page}"
        )

        request = Request(api_url, headers=_request_headers())

        with opener(request, timeout=15) as response:
            page_assets = json.loads(response.read().decode("utf-8"))

        if not isinstance(page_assets, list):
            raise ValueError("GitHub release assets response must be a list.")
        
        assets.extend(page_assets)

        if len(page_assets) < 100:
            return assets
        
        page += 1


def parse_asset_name(asset_name):
    match = ASSET_NAME_PATTERN.fullmatch(asset_name)

    if match is None:
        return "manual", asset_name.removesuffix(".csv")

    return (
        f"{match.group('run_id')}-{match.group('attempt')}",
        match.group("scenario"),
    )


def asset_sort_key(asset):
    asset_name = str(asset.get("name", ""))
    match = ASSET_NAME_PATTERN.fullmatch(asset_name)

    if match is not None:
        return (
            1,
            int(match.group("run_id")),
            int(match.group("attempt")),
            match.group("scenario"),
        )

    return (
        0,
        str(asset.get("created_at", "")),
        asset_name,
    )


class GitHubReleaseAssetsDirective(SphinxDirective):
    has_content = False

    option_spec = {
        "repository": directives.unchanged_required,
        "tag": directives.unchanged_required,
    }

    def run(self):
        repository = self.options.get(
            "repository",
            self.env.app.config.github_release_repository,
        )

        tag = self.options.get(
            "tag",
            self.env.app.config.github_release_tag,
        )

        release_url = (
            f"https://github.com/{repository}/releases/tag/{quote(tag, safe='')}"
        )

        release_paragraph = _link_paragraph(
            "GitHub release: ",
            tag,
            release_url,
        )

        try:
            token = os.environ.get("GITHUB_TOKEN")

            release = load_release(repository, tag)

            release_assets = load_release_assets(
                repository,
                int(release["id"]),
            )
        except HTTPError as error:
            message = (
                "The benchmark release has not been published yet."
                if error.code == 404
                else f"GitHub returned HTTP {error.code} while loading benchmarks."
            )
            return [release_paragraph, nodes.paragraph(text=message)]
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            return [
                release_paragraph,
                nodes.paragraph(
                    text=f"Benchmark results could not be loaded during this build: {error}"
                ),
            ]

        assets = [
            asset
            for asset in release_assets
            if str(asset.get("name", "")).lower().endswith(".csv")
        ]

        assets.sort(key=asset_sort_key, reverse=True)

        if not assets:
            return [
                release_paragraph,
                nodes.paragraph(
                    text="The release does not contain any CSV results yet."
                ),
            ]

        rows = []
        for asset in assets:
            run_id, scenario = parse_asset_name(str(asset["name"]))
            rows.append(
                [
                    (run_id, _workflow_run_url(repository, run_id)),
                    (scenario, None),
                    (_format_timestamp(str(asset.get("created_at", ""))), None),
                    ("Open CSV", str(asset["browser_download_url"])),
                ]
            )

        return [
            release_paragraph,
            _create_table(
                ["Run", "Scenario", "Uploaded", "CSV"],
                rows,
            ),
        ]


def _workflow_run_url(repository, run_id):
    numeric_run_id = run_id.split("-", maxsplit=1)[0]

    if not numeric_run_id.isdigit():
        return None
    
    return f"https://github.com/{repository}/actions/runs/{numeric_run_id}"


def _format_timestamp(value):
    return value.replace("T", " ").replace("Z", " UTC")


def _link_paragraph(prefix, text, url) -> nodes.paragraph:
    paragraph = nodes.paragraph()
    paragraph += nodes.Text(prefix)
    paragraph += nodes.reference("", text, refuri=url)

    return paragraph


def _create_table(
    headers,
    rows,
) -> nodes.table:
    table = nodes.table()
    table["classes"].append("benchmark-results")
    table_group = nodes.tgroup(cols=len(headers))
    table += table_group

    for _header in headers:
        table_group += nodes.colspec(colwidth=1)

    table_head = nodes.thead()
    table_group += table_head
    header_row = nodes.row()
    table_head += header_row

    for header in headers:
        header_row += _table_entry(header)

    table_body = nodes.tbody()
    table_group += table_body

    for row in rows:
        table_row = nodes.row()
        table_body += table_row
        for text, url in row:
            table_row += _table_entry(text, url)

    return table


def _table_entry(text, url=None) -> nodes.entry:
    entry = nodes.entry()
    paragraph = nodes.paragraph()

    if url:
        paragraph += nodes.reference("", text, refuri=url)
    else:
        paragraph += nodes.Text(text)

    entry += paragraph

    return entry


def setup(app: Sphinx):
    app.add_config_value(
        "github_release_repository",
        "JakubOliver/factory-creator",
        "env",
    )

    app.add_config_value(
        "github_release_tag",
        "benchmark-results",
        "env",
    )

    app.add_directive("github-release-assets", GitHubReleaseAssetsDirective)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

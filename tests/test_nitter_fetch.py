from __future__ import annotations

from datetime import datetime, timezone

from _load_skill_module import load_agent_skill_script


nitter = load_agent_skill_script("twitter-nitter-rss", "nitter_fetch")


SAMPLE_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <item>
      <title>RT by @peckshield: #Alert Foo drained of $1.3M</title>
      <link>https://nitter.net/PeckShieldAlert/status/2064729285894852609#m</link>
      <pubDate>Wed, 10 Jun 2026 15:19:57 GMT</pubDate>
      <dc:creator>@PeckShieldAlert</dc:creator>
      <description>&lt;p&gt;Foo exploit, see &lt;a href="https://etherscan.io/tx/0x31E56b4737649e0acdb0EBB4eca44d16aeca25f60c022cbde85f092bde27664a"&gt;tx&lt;/a&gt; and &lt;a href="https://nitter.net/Raydium"&gt;@Raydium&lt;/a&gt;&lt;/p&gt;</description>
    </item>
    <item>
      <title>gm everyone, nothing to see here</title>
      <link>https://nitter.net/peckshield/status/2064700000000000000#m</link>
      <pubDate>Wed, 10 Jun 2026 09:00:00 GMT</pubDate>
      <dc:creator>@peckshield</dc:creator>
      <description>&lt;p&gt;coffee time&lt;/p&gt;</description>
    </item>
  </channel>
</rss>"""


def test_html_to_text_strips_tags_and_unescapes() -> None:
    assert nitter.html_to_text("<p>Foo &amp; bar  baz</p>") == "Foo & bar baz"
    assert nitter.html_to_text(None) == ""


def test_extract_tx_hashes_from_text_and_explorer_links() -> None:
    tx = "0x" + "a" * 64
    links = ["https://etherscan.io/tx/0x" + "B" * 64]
    found = nitter.extract_tx_hashes(f"loss in {tx}", links)
    assert found == [tx, "0x" + "b" * 64]


def test_extract_tx_hashes_dedupes_case_insensitively() -> None:
    upper = "0x" + "C" * 64
    found = nitter.extract_tx_hashes(upper, ["https://etherscan.io/tx/" + upper])
    assert found == ["0x" + "c" * 64]


def test_detect_keywords_matches_substrings() -> None:
    assert "exploit" in nitter.detect_keywords("This is an EXPLOIT")
    assert "flash loan" in nitter.detect_keywords("used a flash loan attack")
    assert nitter.detect_keywords("just a normal day") == []


def test_chain_hint_from_explorer_host() -> None:
    assert nitter.chain_hint(["https://bscscan.com/tx/0xabc"]) == "bsc"
    assert nitter.chain_hint(["https://example.com"]) == "unknown"


def test_canonical_tweet_url_rewrites_to_x() -> None:
    url = "https://nitter.net/PeckShieldAlert/status/123#m"
    assert nitter.canonical_tweet_url(url) == "https://x.com/PeckShieldAlert/status/123"
    assert nitter.canonical_tweet_url(None) is None


def test_in_window_is_exclusive_lower_inclusive_upper() -> None:
    since = datetime(2026, 6, 10, 9, 0, tzinfo=timezone.utc)
    until = datetime(2026, 6, 10, 15, 30, tzinfo=timezone.utc)
    assert nitter.in_window(datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc), since, until)
    assert not nitter.in_window(since, since, until)  # equal to lower bound excluded
    assert nitter.in_window(until, since, until)  # equal to upper bound included
    assert not nitter.in_window(None, since, until)


def test_feed_path_with_replies_toggle() -> None:
    assert nitter.feed_path("@peckshield", False) == "/peckshield/rss"
    assert nitter.feed_path("peckshield", True) == "/peckshield/with_replies/rss"


def test_normalize_item_extracts_evidence() -> None:
    items = nitter.parse_feed(SAMPLE_FEED.encode("utf-8"))
    normalized = nitter.normalize_item("@peckshield", items[0])
    assert normalized["author"] == "PeckShieldAlert"
    assert normalized["tweet_url"] == "https://x.com/PeckShieldAlert/status/2064729285894852609"
    assert normalized["posted_at"] == "2026-06-10T15:19:57Z"
    assert normalized["tx_hashes"] == ["0x31e56b4737649e0acdb0ebb4eca44d16aeca25f60c022cbde85f092bde27664a"]
    assert normalized["chain_hint"] == "ethereum"
    assert "exploit" in normalized["matched_keywords"]
    assert normalized["links"] == ["https://etherscan.io/tx/0x31E56b4737649e0acdb0EBB4eca44d16aeca25f60c022cbde85f092bde27664a"]


def test_scan_filters_window_and_candidates(monkeypatch) -> None:
    def fake_fetch(instances, handle, with_replies):
        return nitter.parse_feed(SAMPLE_FEED.encode("utf-8")), instances[0]

    monkeypatch.setattr(nitter, "fetch_account", fake_fetch)
    result = nitter.scan(
        accounts=["@peckshield"],
        instances=["https://nitter.net"],
        since=nitter.parse_time("2026-06-10T10:00:00Z"),
        until=nitter.parse_time("2026-06-10T16:00:00Z"),
        with_replies=False,
        keep_all=False,
    )
    # Only the 15:19 alert is in-window AND a candidate; the 09:00 "coffee" post is out of window.
    assert result["alert_count"] == 1
    assert result["alerts"][0]["tweet_url"].endswith("/status/2064729285894852609")
    assert result["instances_used"] == {"peckshield": "https://nitter.net"}
    assert result["failures"] == {}


def test_scan_records_instance_failures(monkeypatch) -> None:
    def boom(instances, handle, with_replies):
        raise RuntimeError("all instances down")

    monkeypatch.setattr(nitter, "fetch_account", boom)
    result = nitter.scan(
        accounts=["peckshield"],
        instances=["https://nitter.net"],
        since=nitter.parse_time("2026-06-10T00:00:00Z"),
        until=nitter.parse_time("2026-06-11T00:00:00Z"),
        with_replies=False,
        keep_all=True,
    )
    assert result["alert_count"] == 0
    assert "peckshield" in result["failures"]

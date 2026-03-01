"""Pytest fixtures for Naver Finance crawler tests."""

import pytest
import pandas as pd
from io import StringIO
import os


# Get the fixture directory path
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures', 'naver_finance')


def _parse_annual_df(html_content):
    """Parse HTML and extract annual dataframe, handling both single and multi-level columns."""
    dfs = pd.read_html(StringIO(html_content), match='주요재무정보')
    df = dfs[0]
    df.set_index(df.columns[0], inplace=True)
    
    # Extract annual performance data - handle both multi-index and single-level columns
    if isinstance(df.columns, pd.MultiIndex):
        # Multi-index columns from real Naver Finance HTML
        annual_df = df.xs('최근 연간 실적', axis=1, level=0)
        if hasattr(annual_df.columns, 'droplevel'):
            try:
                annual_df.columns = annual_df.columns.droplevel(1)
            except (IndexError, ValueError):
                pass
    else:
        # Single-level columns (from test fixtures)
        # Assume first 4 columns are annual data
        annual_cols = [c for c in df.columns if '분기' not in str(c) and 'E' not in str(c)][:4]
        if len(annual_cols) == 0:
            annual_cols = df.columns[:4]
        annual_df = df[annual_cols]
    
    return annual_df


@pytest.fixture
def sk_hynix_html():
    """Full fixture with all metrics (SK Hynix-like large cap)."""
    with open(os.path.join(FIXTURE_DIR, 'sk_hynix_full.html'), 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def sk_hynix_annual_df(sk_hynix_html):
    """Parsed annual dataframe from sk_hynix fixture."""
    return _parse_annual_df(sk_hynix_html)


@pytest.fixture
def samsung_missing_roe_html():
    """Fixture with missing ROE data."""
    with open(os.path.join(FIXTURE_DIR, 'samsung_missing_roe.html'), 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def samsung_annual_df(samsung_missing_roe_html):
    """Parsed annual dataframe from samsung fixture (missing ROE)."""
    return _parse_annual_df(samsung_missing_roe_html)


@pytest.fixture
def startup_negative_profit_html():
    """Fixture with negative operating profit (startup-like)."""
    with open(os.path.join(FIXTURE_DIR, 'startup_negative_profit.html'), 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def startup_annual_df(startup_negative_profit_html):
    """Parsed annual dataframe from startup fixture (negative profits)."""
    return _parse_annual_df(startup_negative_profit_html)


@pytest.fixture
def minimal_html():
    """Fixture with minimal data (only revenue and EPS available)."""
    with open(os.path.join(FIXTURE_DIR, 'minimal_data.html'), 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def minimal_annual_df(minimal_html):
    """Parsed annual dataframe from minimal fixture."""
    return _parse_annual_df(minimal_html)


@pytest.fixture
def large_cap_html():
    """Large cap fixture with all metrics (Samsung-like)."""
    with open(os.path.join(FIXTURE_DIR, 'large_cap.html'), 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def large_cap_annual_df(large_cap_html):
    """Parsed annual dataframe from large cap fixture."""
    return _parse_annual_df(large_cap_html)


@pytest.fixture
def mid_cap_partial_html():
    """Mid cap fixture with partial data (some metrics missing)."""
    with open(os.path.join(FIXTURE_DIR, 'mid_cap_partial.html'), 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def mid_cap_annual_df(mid_cap_partial_html):
    """Parsed annual dataframe from mid cap fixture."""
    return _parse_annual_df(mid_cap_partial_html)


@pytest.fixture
def small_cap_minimal_html():
    """Small cap fixture with minimal data (only basic metrics)."""
    with open(os.path.join(FIXTURE_DIR, 'small_cap_minimal.html'), 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def small_cap_annual_df(small_cap_minimal_html):
    """Parsed annual dataframe from small cap fixture."""
    return _parse_annual_df(small_cap_minimal_html)


@pytest.fixture
def loss_making_html():
    """Fixture for loss-making company (all profits negative)."""
    with open(os.path.join(FIXTURE_DIR, 'loss_making.html'), 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def loss_making_annual_df(loss_making_html):
    """Parsed annual dataframe from loss-making fixture."""
    return _parse_annual_df(loss_making_html)


@pytest.fixture
def newly_listed_html():
    """Fixture for newly listed company (only 1-2 years of data)."""
    with open(os.path.join(FIXTURE_DIR, 'newly_listed.html'), 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def newly_listed_annual_df(newly_listed_html):
    """Parsed annual dataframe from newly listed fixture."""
    return _parse_annual_df(newly_listed_html)


@pytest.fixture
def empty_html():
    """Empty HTML with no table data."""
    return """
    <html>
    <body>
        <div class="section cop_analysis">
            <p>No data available</p>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def malformed_html():
    """Malformed HTML that may cause parsing issues."""
    return """
    <html>
    <body>
        <div class="section cop_analysis">
            <table class="tb_type1">
                <tr><th>주요재무정보</th></tr>
                <tr><td>Invalid data</td></tr>
            </table>
        </div>
    </body>
    </html>
    """

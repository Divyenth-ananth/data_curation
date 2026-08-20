import sys
import re
from pathlib import Path
from typing import List, Dict, Any
import httpx
from bs4 import BeautifulSoup

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import RANKING_URL_2025, RANK_BAND_URLS_2025, HTTP_HEADERS, REQUEST_TIMEOUT


def scrape_top_100_rankings() -> List[Dict[str, Any]]:
    """
    Scrapes the top 100 NIRF Engineering rankings including sub-scores
    and PDF links for individual submitted institute data.
    """
    print(f"[Scraper] Fetching Top 100 Rankings from {RANKING_URL_2025}...")
    response = httpx.get(RANKING_URL_2025, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", id="tbl_overall")
    if not table:
        raise ValueError("Could not find table with id='tbl_overall' on ranking page.")

    rows = table.find("tbody").find_all("tr", recursive=False)
    records = []

    for row in rows:
        tds = row.find_all("td", recursive=False)
        if len(tds) < 6:
            continue

        inst_id = tds[0].text.strip()
        name = tds[1].contents[0].strip() if tds[1].contents else ""
        city = tds[2].text.strip()
        state = tds[3].text.strip()
        
        try:
            score = float(tds[4].text.strip())
        except ValueError:
            score = None
            
        rank = tds[5].text.strip()

        # Extract PDF Link
        pdf_url = None
        for a in tds[1].find_all("a", href=True):
            if ".pdf" in a["href"].lower():
                raw_href = a["href"].strip()
                if raw_href.startswith("http"):
                    pdf_url = raw_href
                else:
                    pdf_url = f"https://www.nirfindia.org/{raw_href.lstrip('/')}"
                break

        # Extract Sub-scores (TLR, RPC, GO, OI, PERCEPTION)
        sub_scores = {}
        sub_table = tds[1].find("table")
        if sub_table:
            th_cells = [th.text.strip().upper() for th in sub_table.find_all("th")]
            td_cells = [td.text.strip() for td in sub_table.find_all("td")]
            for th, td in zip(th_cells, td_cells):
                try:
                    val = float(td)
                except ValueError:
                    val = None
                if "TLR" in th:
                    sub_scores["tlr"] = val
                elif "RPC" in th:
                    sub_scores["rpc"] = val
                elif "GO" in th:
                    sub_scores["go"] = val
                elif "OI" in th:
                    sub_scores["oi"] = val
                elif "PERCEPTION" in th:
                    sub_scores["perception"] = val

        records.append({
            "institute_id": inst_id,
            "institute_name": name,
            "city": city,
            "state": state,
            "score": score,
            "rank": rank,
            "rank_band": "1-100",
            "tlr": sub_scores.get("tlr"),
            "rpc": sub_scores.get("rpc"),
            "go": sub_scores.get("go"),
            "oi": sub_scores.get("oi"),
            "perception": sub_scores.get("perception"),
            "pdf_url": pdf_url,
        })

    print(f"[Scraper] Successfully parsed {len(records)} Top 100 institutes.")
    return records


def scrape_rank_bands() -> List[Dict[str, Any]]:
    """
    Scrapes rank band tables (101-150, 151-200, 201-300).
    """
    all_band_records = []
    for band_name, band_url in RANK_BAND_URLS_2025.items():
        print(f"[Scraper] Fetching Rank Band {band_name} from {band_url}...")
        try:
            resp = httpx.get(band_url, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                print(f"[Scraper] Warning: Received status {resp.status_code} for {band_url}")
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            table = soup.find("table")
            if not table or not table.find("tbody"):
                continue

            rows = table.find("tbody").find_all("tr", recursive=False)
            for r in rows:
                tds = r.find_all("td", recursive=False)
                if len(tds) < 3:
                    continue
                name = tds[0].text.strip()
                city = tds[1].text.strip()
                state = tds[2].text.strip()
                all_band_records.append({
                    "institute_id": f"BAND-{band_name}",
                    "institute_name": name,
                    "city": city,
                    "state": state,
                    "score": None,
                    "rank": band_name,
                    "rank_band": band_name,
                    "tlr": None,
                    "rpc": None,
                    "go": None,
                    "oi": None,
                    "perception": None,
                    "pdf_url": None,
                })
        except Exception as e:
            print(f"[Scraper] Error fetching band {band_name}: {e}")

    print(f"[Scraper] Successfully parsed {len(all_band_records)} rank-band institutes.")
    return all_band_records


def scrape_all_rankings(include_bands: bool = True) -> List[Dict[str, Any]]:
    """
    Combined scraper for Top 100 and participating rank bands.
    """
    top_100 = scrape_top_100_rankings()
    if include_bands:
        bands = scrape_rank_bands()
        return top_100 + bands
    return top_100


if __name__ == "__main__":
    results = scrape_all_rankings(include_bands=True)
    print(f"Total entries: {len(results)}")

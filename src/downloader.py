import os
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import httpx
from tqdm.asyncio import tqdm_asyncio

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import (
    DOWNLOADS_DIR,
    TARGET_YEAR,
    TARGET_CATEGORY,
    HTTP_HEADERS,
    REQUEST_TIMEOUT,
    MAX_CONCURRENT_DOWNLOADS,
)


def get_pdf_download_folder() -> Path:
    folder = DOWNLOADS_DIR / str(TARGET_YEAR) / TARGET_CATEGORY
    folder.mkdir(parents=True, exist_ok=True)
    return folder


async def download_single_pdf(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    item: Dict[str, Any],
    dest_folder: Path,
) -> Dict[str, Any]:
    inst_id = item.get("institute_id", "UNKNOWN")
    pdf_url = item.get("pdf_url")

    if not pdf_url:
        return {"institute_id": inst_id, "status": "skipped", "file_path": None}

    # Clean file name
    clean_id = inst_id.replace("/", "_").replace("\\", "_")
    target_path = dest_folder / f"{clean_id}.pdf"

    # If already downloaded, skip
    if target_path.exists() and target_path.stat().st_size > 1024:
        return {"institute_id": inst_id, "status": "cached", "file_path": str(target_path)}

    async with semaphore:
        for attempt in range(1, 4):
            try:
                resp = await client.get(pdf_url, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT)
                if resp.status_code == 200 and len(resp.content) > 1024:
                    with open(target_path, "wb") as f:
                        f.write(resp.content)
                    return {"institute_id": inst_id, "status": "downloaded", "file_path": str(target_path)}
                else:
                    await asyncio.sleep(1.0 * attempt)
            except Exception as e:
                if attempt == 3:
                    return {"institute_id": inst_id, "status": f"error: {str(e)}", "file_path": None}
                await asyncio.sleep(1.0 * attempt)

    return {"institute_id": inst_id, "status": "failed", "file_path": None}


async def download_all_pdfs_async(rankings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Downloads all submitted institute PDFs concurrently with rate-limiting and progress display.
    """
    dest_folder = get_pdf_download_folder()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
    
    # Filter items that have a valid pdf_url
    items_to_download = [item for item in rankings if item.get("pdf_url")]
    print(f"[Downloader] Found {len(items_to_download)} institutes with PDF URLs.")
    print(f"[Downloader] Target download folder: {dest_folder}")

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
        tasks = [
            download_single_pdf(client, semaphore, item, dest_folder)
            for item in items_to_download
        ]
        results = await tqdm_asyncio.gather(*tasks, desc="Downloading NIRF PDFs")

    # Map downloaded paths back to original ranking records
    status_map = {res["institute_id"]: res for res in results}
    for item in rankings:
        inst_id = item.get("institute_id")
        if inst_id in status_map:
            item["local_pdf_path"] = status_map[inst_id]["file_path"]
            item["download_status"] = status_map[inst_id]["status"]
        else:
            item["local_pdf_path"] = None
            item["download_status"] = "no_url"

    downloaded_count = sum(1 for r in results if r["status"] in ("downloaded", "cached"))
    print(f"[Downloader] Finished. Ready: {downloaded_count}/{len(items_to_download)} files.")
    return rankings


def download_all_pdfs(rankings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for downloading PDFs.
    """
    return asyncio.run(download_all_pdfs_async(rankings))


if __name__ == "__main__":
    from src.scraper import scrape_top_100_rankings
    rankings = scrape_top_100_rankings()
    # Test download on first 5
    download_all_pdfs(rankings[:5])

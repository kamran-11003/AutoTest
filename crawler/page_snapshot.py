"""
Page Snapshot Manager
Stores page HTML and clickable elements for debugging filtering logic
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from playwright.async_api import Page
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class PageSnapshot:
    """Captures and stores page snapshots for debugging"""
    
    def __init__(self, output_dir: str = "data/snapshots"):
        """Initialize page snapshot manager"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots = []
        
        logger.info(f"PageSnapshot initialized (output: {output_dir})")
    
    async def capture_snapshot(
        self,
        page: Page,
        url: str,
        clickable_elements: List[Dict],
        filtered_elements: List[Dict],
        discovered_urls: List[str]
    ) -> str:
        """
        Capture full page snapshot with debugging info
        
        Args:
            page: Playwright page object
            url: Current page URL
            clickable_elements: All found clickables (before filtering)
            filtered_elements: Filtered clickables (after intelligent filtering)
            discovered_urls: URLs discovered via AVB
        
        Returns:
            Path to saved snapshot
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_url = url.replace('https://', '').replace('http://', '').replace('/', '_')[:50]
            filename = f"{timestamp}_{safe_url}"
            
            # Get page HTML
            html_content = await page.content()
            
            # Get page title
            title = await page.title()
            
            # Create snapshot data
            snapshot_data = {
                "url": url,
                "title": title,
                "timestamp": timestamp,
                "crawl_stats": {
                    "total_clickables": len(clickable_elements),
                    "after_filtering": len(filtered_elements),
                    "filtered_out": len(clickable_elements) - len(filtered_elements),
                    "reduction_percentage": round((1 - len(filtered_elements) / len(clickable_elements)) * 100, 2) if clickable_elements else 0,
                    "discovered_urls": len(discovered_urls)
                },
                "clickable_elements": {
                    "before_filtering": [
                        {
                            "tag": el.get("tag"),
                            "text": el.get("text", "")[:100],
                            "class": el.get("class", ""),
                            "id": el.get("id", ""),
                            "href": el.get("href", ""),
                            "confidence": el.get("confidence", "unknown")
                        }
                        for el in clickable_elements
                    ],
                    "after_filtering": [
                        {
                            "tag": el.get("tag"),
                            "text": el.get("text", "")[:100],
                            "class": el.get("class", ""),
                            "id": el.get("id", ""),
                            "href": el.get("href", "")
                        }
                        for el in filtered_elements
                    ],
                    "filtered_out": [
                        el for el in clickable_elements 
                        if el not in filtered_elements
                    ][:20]  # Limit to first 20 for readability
                },
                "discovered_urls": discovered_urls
            }
            
            # Save JSON metadata
            json_path = self.output_dir / f"{filename}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
            
            # Save HTML
            html_path = self.output_dir / f"{filename}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Add to snapshots list
            self.snapshots.append({
                "url": url,
                "json": str(json_path),
                "html": str(html_path)
            })
            
            logger.info(
                f"📸 Snapshot saved: {filename}\n"
                f"   ├─ Total clickables: {len(clickable_elements)}\n"
                f"   ├─ After filtering: {len(filtered_elements)} "
                f"({snapshot_data['crawl_stats']['reduction_percentage']}% reduction)\n"
                f"   └─ Discovered: {len(discovered_urls)} URLs"
            )
            
            return str(json_path)
        
        except Exception as e:
            logger.error(f"Error capturing snapshot: {e}")
            return ""
    
    def save_summary(self, output_path: str = None):
        """Save summary of all snapshots"""
        if not output_path:
            output_path = self.output_dir / "snapshots_summary.json"
        
        summary = {
            "total_snapshots": len(self.snapshots),
            "snapshots": self.snapshots
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"📋 Snapshot summary saved: {output_path}")
    
    def print_report(self):
        """Print a summary report of all snapshots"""
        print("\n" + "="*80)
        print("📸 PAGE SNAPSHOTS REPORT")
        print("="*80)
        
        for i, snapshot in enumerate(self.snapshots, 1):
            print(f"\n{i}. {snapshot['url']}")
            print(f"   JSON: {snapshot['json']}")
            print(f"   HTML: {snapshot['html']}")
        
        print(f"\n📁 Total snapshots: {len(self.snapshots)}")
        print(f"📂 Location: {self.output_dir}")
        print("="*80 + "\n")

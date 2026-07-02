from __future__ import annotations

from urllib.parse import quote_plus

from playwright.async_api import async_playwright


class BrowserTool:
    def __init__(self) -> None:
        self.playwright = None
        self.browser = None

    async def start(self) -> None:
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )

    async def stop(self) -> None:
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def search_site(self, site: str, query: str) -> list[dict]:
        if not self.browser:
            raise RuntimeError("BrowserTool.start() must be called before search_site().")

        page = await self.browser.new_page()
        await page.set_extra_http_headers(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
                )
            }
        )

        try:
            if "bestbuy" in site:
                return await self._search_bestbuy(page, query)
            if "walmart" in site:
                return await self._search_walmart(page, query)
            return []
        except Exception:
            return []
        finally:
            await page.close()

    async def get_page_content(self, url: str) -> str:
        if not self.browser:
            raise RuntimeError("BrowserTool.start() must be called before get_page_content().")

        page = await self.browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            return await page.evaluate(
                """() => {
                    const remove = document.querySelectorAll(
                        'script, style, nav, header, footer, aside, iframe'
                    );
                    remove.forEach((el) => el.remove());
                    return document.body.innerText.slice(0, 8000);
                }"""
            )
        except Exception:
            return ""
        finally:
            await page.close()

    async def _search_bestbuy(self, page, query: str) -> list[dict]:
        await page.goto(
            f"https://www.bestbuy.com/site/searchpage.jsp?st={quote_plus(query)}",
            wait_until="domcontentloaded",
            timeout=15000,
        )
        await page.wait_for_selector(".sku-item", timeout=8000)
        items = await page.query_selector_all(".sku-item")
        results = []

        for item in items[:5]:
            title_el = await item.query_selector(".sku-header a")
            price_el = await item.query_selector(".priceView-customer-price span")
            if not title_el:
                continue

            title = (await title_el.inner_text()).strip()
            href = await title_el.get_attribute("href")
            price_text = (await price_el.inner_text()).strip() if price_el else ""
            if href:
                results.append(
                    {
                        "title": title,
                        "url": f"https://www.bestbuy.com{href}" if href.startswith("/") else href,
                        "price_text": price_text,
                        "site": "bestbuy",
                    }
                )

        return results

    async def _search_walmart(self, page, query: str) -> list[dict]:
        await page.goto(
            f"https://www.walmart.com/search?q={quote_plus(query)}",
            wait_until="domcontentloaded",
            timeout=15000,
        )
        await page.wait_for_selector('[data-item-id]', timeout=8000)
        items = await page.query_selector_all('[data-item-id]')
        results = []

        for item in items[:5]:
            title_el = await item.query_selector('[itemprop="name"]')
            price_el = await item.query_selector('[itemprop="price"]')
            link_el = await item.query_selector('a[href*="/ip/"]')
            if not title_el or not link_el:
                continue

            title = (await title_el.inner_text()).strip()
            href = await link_el.get_attribute("href")
            price = await price_el.get_attribute("content") if price_el else ""
            if href:
                results.append(
                    {
                        "title": title,
                        "url": f"https://www.walmart.com{href}" if href.startswith("/") else href,
                        "price_text": f"${price}" if price else "",
                        "site": "walmart",
                    }
                )

        return results

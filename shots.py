from playwright.sync_api import sync_playwright
pages={"home":"/","gongura":"/recipes/pickles-and-chutneys/gongura-pachadi/"}
with sync_playwright() as p:
    b=p.chromium.launch()
    for name,url in pages.items():
        for dev,vp in {"desktop":(1366,900),"mobile":(390,844)}.items():
            pg=b.new_page(viewport={"width":vp[0],"height":vp[1]},device_scale_factor=2 if dev=="mobile" else 1)
            pg.goto("http://127.0.0.1:8000"+url,wait_until="load"); pg.wait_for_timeout(2000)
            pg.screenshot(path=f"screenshots/{name}-{dev}.png",full_page=True)
    b.close()

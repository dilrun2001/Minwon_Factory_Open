import re
import json
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

list_url = "https://eminwon.saha.go.kr/emwp/gov/mogaha/ntis/web/emwp/cns/action/EmwpCnslWebAction.do"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded",
}
tinyllama_data = []

for page in range(1, 276):
    print(f"📄 페이지 {page} 처리 중...")

    list_data = {
        "method": "selectCnslWebPage",
        "menu_id": "EMWPCnslWebInqL",
        "jndinm": "EmwpCnslWebEJB",
        "methodnm": "selectCnslWebPage",
        "context": "NTIS",
        "pageIndex": str(page),
        "pageSize": "20"
    }

    try:
        response = requests.post(list_url, data=list_data, headers=headers)
    except Exception as e:
        print(f"❌ 요청 실패: {e}")
        break

    if response.status_code != 200:
        print(f"❌ 페이지 {page} 요청 실패!")
        break

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table.table tbody tr")

    if not rows:
        print("⛔ 더 이상 데이터 없음! 중단합니다.")
        break

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            link_tag = cols[1].find("a")
            if not link_tag:
                continue

            onclick = link_tag.get("href", "")
            match = re.search(r"fncViewDtl\('(\d+)'", onclick)
            if not match:
                continue

            cnsl_qna_no = match.group(1)

            detail_data = {
                "method": "selectCnslWebShow",
                "jndinm": "EmwpCnslWebEJB",
                "methodnm": "selectCnslWebShow",
                "context": "NTIS",
                "cnsl_qna_no": cnsl_qna_no,
            }

            try:
                detail_resp = requests.post(list_url, data=detail_data, headers=headers)
            except Exception as e:
                print(f"❌ 상세페이지 요청 실패: {e}")
                continue

            if detail_resp.status_code != 200:
                continue

            detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
            tables = detail_soup.select("table.bbs-table-view")

            detail_title = ""
            detail_date = ""
            if tables:
                rows_detail = tables[0].find_all("tr")
                for tr in rows_detail:
                    ths = tr.find_all("th")
                    tds = tr.find_all("td")
                    for i in range(len(ths)):
                        th_text = ths[i].text.strip()
                        td_text = tds[i].text.strip() if i < len(tds) else ""
                        if th_text == "제목":
                            detail_title = td_text
                        elif th_text == "작성일":
                            detail_date = td_text

            question_text = tables[0].find_all("tr")[-1].get_text(separator="\n", strip=True) if len(tables) > 0 else ""
            answer_text = tables[1].find_all("tr")[-1].get_text(separator="\n", strip=True) if len(tables) > 1 else ""

            if "민원상세보기(원본)" in answer_text:
                iframe_tag = detail_soup.find("iframe", id="epeople")
                if iframe_tag:
                    iframe_src = iframe_tag.get("src")
                    if iframe_src:
                        iframe_url = "https://eminwon.saha.go.kr" + iframe_src
                        print(f"🌐 iframe url: {iframe_url}")

                        try:
                            options = webdriver.ChromeOptions()
                            options.add_argument("--headless")
                            driver = webdriver.Chrome(options=options)

                            driver.get(iframe_url)
                            time.sleep(2)

                            iframe_soup = BeautifulSoup(driver.page_source, "html.parser")
                            dd_tag = iframe_soup.find("dd", style=lambda s: s and "white-space:pre-wrap" in s)
                            if dd_tag:
                                answer_text = dd_tag.get_text(separator="\n", strip=True)
                                print("✅ Selenium에서 iframe 직접 진입 성공!")
                            else:
                                print("❌ iframe에서 dd 태그를 찾을 수 없음!")

                            driver.quit()
                        except Exception as e:
                            print(f"❌ Selenium iframe 접근 실패: {e}")

            if question_text.strip() and answer_text.strip():
                data_item = {
                    "instruction": question_text.strip(),
                    "output": answer_text.strip()
                }
                tinyllama_data.append(data_item)
                print(f"✅ 민원 수집: {detail_title} (작성일: {detail_date})")
            else:
                print("⚠️ 질문 또는 답변이 비어 있어 저장하지 않음")

# ✅ JSONL 저장
with open("data.jsonl", "w", encoding="utf-8") as f:
    for item in tinyllama_data:
        json_line = json.dumps(item, ensure_ascii=False)
        f.write(json_line + "\n")

print(f"🎉 총 {len(tinyllama_data)}개의 데이터가 data.jsonl에 저장되었습니다.")

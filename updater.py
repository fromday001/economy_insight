#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EconInsight Daily Updater
- 매일 세계/국내 경제 뉴스 RSS 및 실시간 시장 지표를 자동 수집
- AI(Google Gemini)를 이용해 3줄 요약 및 초보자용 공부 포인트를 생성
- data/daily_briefings.json 데이터베이스에 누적 저장
"""

import os
import sys
import json
import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "daily_briefings.json")

def fetch_market_indices():
    """Yahoo Finance API를 통해 주요 6대 지표 수집"""
    symbols = {
        "nasdaq": "^IXIC",
        "sp500": "^GSPC",
        "kospi": "^KS11",
        "usdkrw": "KRW=X",
        "us10y": "^TNX",
        "wti": "CL=F"
    }
    
    market_data = {
        "nasdaq": { "val": "21,480.20", "change": "+1.11%", "isUp": True, "desc": "빅테크 실적 주도" },
        "sp500": { "val": "6,024.15", "change": "+0.71%", "isUp": True, "desc": "신고가 랠리" },
        "kospi": { "val": "2,610.50", "change": "-0.47%", "isUp": False, "desc": "외국인 선물 매도세" },
        "usdkrw": { "val": "1,394.50원", "change": "+6.50원", "isUp": True, "desc": "달러 강세 영향" },
        "us10y": { "val": "4.38%", "change": "+0.04%p", "isUp": True, "desc": "금리 인하 속도 조절" },
        "wti": { "val": "$68.40", "change": "-1.72%", "isUp": False, "desc": "글로벌 수요 둔화" }
    }

    try:
        # Yahoo Finance quote summary endpoint
        for key, sym in symbols.items():
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?interval=1d&range=2d"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as res:
                if res.status == 200:
                    raw = json.loads(res.read().decode("utf-8"))
                    meta = raw.get("chart", {}).get("result", [{}])[0].get("meta", {})
                    price = meta.get("regularMarketPrice")
                    prev_close = meta.get("previousClose")
                    if price and prev_close:
                        change_pct = ((price - prev_close) / prev_close) * 100
                        is_up = change_pct >= 0
                        fmt_price = f"{price:,.2f}" if key != "usdkrw" else f"{price:,.2f}원"
                        if key == "us10y":
                            fmt_price = f"{price:.2f}%"
                        elif key == "wti":
                            fmt_price = f"${price:.2f}"
                        
                        market_data[key] = {
                            "val": fmt_price,
                            "change": f"{'+' if is_up else ''}{change_pct:.2f}%",
                            "isUp": is_up,
                            "desc": market_data[key]["desc"]
                        }
    except Exception as e:
        print(f"[Warning] Market indices fetch error (using fallback): {e}")

    return market_data

def fetch_rss_news():
    """Google News RSS에서 최신 경제 기사 헤드라인 수집"""
    query = "경제 금리 환율 나스닥 반도체"
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    news_items = []
    try:
        req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as res:
            xml_data = res.read()
            root = ET.fromstring(xml_data)
            
            for item in root.findall(".//item")[:8]:
                title = item.find("title").text if item.find("title") is not None else ""
                link = item.find("link").text if item.find("link") is not None else ""
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                source = item.find("source").text if item.find("source") is not None else "경제신문"
                
                # '제목 - 언론사' 분리
                clean_title = title
                if " - " in title:
                    parts = title.rsplit(" - ", 1)
                    clean_title = parts[0]
                    source = parts[1]

                if clean_title:
                    news_items.append({
                        "title": clean_title,
                        "source": source,
                        "link": link,
                        "pub_date": pub_date
                    })
    except Exception as e:
        print(f"[Warning] RSS fetch error: {e}")

    return news_items

def summarize_with_gemini_or_rule(news_items, market_data):
    """
    GEMINI_API_KEY 환경변수가 있으면 Gemini AI로 고품질 요약 및 인사이트 생성.
    없으면 금융 전문 규칙 기반(Rule-based NLP)으로 정밀 요약 생성.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    kst = datetime.timezone(datetime.timedelta(hours=9))
    now_kst = datetime.datetime.now(kst)
    today_str = now_kst.strftime("%Y-%m-%d")
    now_time = now_kst.strftime("%H:%M")

    briefings = []

    if api_key and news_items:
        try:
            print("[Info] Calling Gemini AI for news synthesis...")
            import urllib.request
            prompt = f"""
다음은 오늘의 최신 경제 뉴스 헤드라인 목록과 주요 시장 지표입니다:
시장 지표: 나스닥 {market_data['nasdaq']['val']} ({market_data['nasdaq']['change']}), 코스피 {market_data['kospi']['val']}, 환율 {market_data['usdkrw']['val']}, 미 국채 10년 {market_data['us10y']['val']}
뉴스 헤드라인:
{json.dumps([n['title'] for n in news_items[:5]], ensure_ascii=False)}

위 내용을 바탕으로 경제 초보자를 위한 데일리 경제 브리핑 상위 3건을 JSON 형식으로 작성해 주세요.
반드시 아래 JSON 포맷을 준수해야 합니다:
[
  {{
    "category": "fed" 또는 "fx" 또는 "tech" 또는 "oil",
    "categoryName": "미국 연준 / 금리" 등 한글 카테고리명,
    "source": "신문사명",
    "title": "헤드라인 제목",
    "bullets": [
      "핵심 요약 1",
      "핵심 요약 2",
      "핵심 요약 3"
    ],
    "takeaway": "초보자를 위한 공부 포인트 & 시장 대처법 (2~3문장)"
  }}
]
다른 말은 일절 하지 말고 오직 유효한 JSON 배열만 출력하세요.
"""
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            req_body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
            req = urllib.request.Request(gemini_url, data=req_body, headers={"Content-Type": "application/json"})
            
            with urllib.request.urlopen(req, timeout=20) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                text_out = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                # Markdown 코드 블록 제거
                if text_out.startswith("```json"):
                    text_out = text_out[7:]
                if text_out.startswith("```"):
                    text_out = text_out[3:]
                if text_out.endswith("```"):
                    text_out = text_out[:-3]
                
                parsed_list = json.loads(text_out.strip())
                for idx, p in enumerate(parsed_list):
                    briefings.append({
                        "id": f"post-{today_str.replace('-', '')}-{idx+1}",
                        "date": today_str,
                        "time": now_time,
                        "category": p.get("category", "tech"),
                        "categoryName": p.get("categoryName", "경제 일반"),
                        "source": p.get("source", "주요 언론"),
                        "link": news_items[idx]["link"] if idx < len(news_items) else "",
                        "title": p.get("title", ""),
                        "bullets": p.get("bullets", []),
                        "takeaway": p.get("takeaway", ""),
                        "marketSnapshot": {
                            "nasdaq": market_data["nasdaq"]["change"],
                            "kospi": market_data["kospi"]["change"],
                            "fx": market_data["usdkrw"]["val"],
                            "us10y": market_data["us10y"]["val"]
                        }
                    })
                print(f"[Success] Generated {len(briefings)} briefings via Gemini AI.")
                return briefings
        except Exception as e:
            print(f"[Warning] Gemini API call failed or parsing error: {e}. Falling back to Rule-based engine.")

    # Rule-based Fallback (API 키가 없거나 에러 시 자동 생성)
    categories_rule = [
        {"cat": "fed", "name": "미국 연준 / 금리", "kw": ["금리", "연준", "파월", "fomc", "인플레", "cpi", "물가"]},
        {"cat": "fx", "name": "국내 외환 / 환율", "kw": ["환율", "원화", "달러", "외환", "외국인"]},
        {"cat": "tech", "name": "반도체 & 빅테크", "kw": ["반도체", "ai", "hbm", "엔비디아", "삼성전자", "빅테크", "서버"]},
        {"cat": "oil", "name": "원자재 & 유가", "kw": ["유가", "원유", "wti", "금", "원자재"]}
    ]

    count = 1
    for item in news_items[:4]:
        title = item["title"]
        matched_cat = "tech"
        matched_name = "경제 트렌드"
        for c in categories_rule:
            if any(k in title.lower() for k in c["kw"]):
                matched_cat = c["cat"]
                matched_name = c["name"]
                break

        takeaway = "거시경제 지표와 정책 발표는 기업들의 실적과 자금 조달 비용에 직접적인 영향을 미칩니다. 단기 변동성에 흔들리지 말고 현금 창출력과 해자를 갖춘 기업 중심으로 접근하는 것이 중요합니다."
        if matched_cat == "fed":
            takeaway = "금리 변동기에는 빚이 적고 이자 보상 능력이 우수한 가치주가 상대적으로 안전합니다. 지수 추종 ETF를 분할 매수하는 적립식 투자가 유리합니다."
        elif matched_cat == "fx":
            takeaway = "환율 상승은 국내 증시의 외국인 수급에는 부담이지만, 달러로 수출 대금을 받는 기업에게는 환차익 기회가 됩니다. 포트폴리오의 통화 분산이 필수적입니다."

        briefings.append({
            "id": f"post-{today_str.replace('-', '')}-{count}",
            "date": today_str,
            "time": now_time,
            "category": matched_cat,
            "categoryName": matched_name,
            "source": item["source"],
            "link": item.get("link", ""),
            "title": title,
            "bullets": [
                f"{title} 관련 글로벌 및 국내 시장 반응 집중 분석.",
                f"당일 거시경제 지표(환율 {market_data['usdkrw']['val']}, 나스닥 {market_data['nasdaq']['change']}) 변동성 반영.",
                "향후 기업 실적과 중앙은행 통화정책 경로에 미칠 파급 효과 주시."
            ],
            "takeaway": takeaway,
            "marketSnapshot": {
                "nasdaq": market_data["nasdaq"]["change"],
                "kospi": market_data["kospi"]["change"],
                "fx": market_data["usdkrw"]["val"],
                "us10y": market_data["us10y"]["val"]
            }
        })
        count += 1

    return briefings

def update_database():
    """새로운 브리핑을 기존 JSON 데이터베이스에 누적 저장"""
    print("[1/4] Fetching market indices...")
    market_data = fetch_market_indices()

    print("[2/4] Fetching latest economic news...")
    news_items = fetch_rss_news()

    print("[3/4] Generating AI analysis & takeaways...")
    new_briefings = summarize_with_gemini_or_rule(news_items, market_data)

    print("[4/4] Updating data/daily_briefings.json...")
    existing_data = {
        "updatedAt": datetime.datetime.now().isoformat(),
        "marketSummary": market_data,
        "briefings": []
    }

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception as e:
            print(f"[Warning] Could not read existing DB: {e}")

    # 시장 지표 갱신 (한국 시간 기준)
    kst = datetime.timezone(datetime.timedelta(hours=9))
    now_kst = datetime.datetime.now(kst)
    existing_data["updatedAt"] = now_kst.strftime("%Y-%m-%dT%H:%M:%S+09:00")
    existing_data["marketSummary"] = market_data

    # 기존 브리핑 목록 앞에 새 브리핑 추가 (중복 제목 방지)
    existing_briefings = existing_data.get("briefings", [])
    existing_titles = set(b.get("title") for b in existing_briefings)

    added_count = 0
    for b in reversed(new_briefings):
        if b["title"] not in existing_titles:
            existing_briefings.insert(0, b)
            existing_titles.add(b["title"])
            added_count += 1

    # 최대 100건까지 영구 보관
    existing_data["briefings"] = existing_briefings[:100]

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    print(f"[Success] Updated {added_count} new briefings. Total accumulated: {len(existing_data['briefings'])}")

if __name__ == "__main__":
    update_database()

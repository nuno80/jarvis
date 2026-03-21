import sys, urllib.request, urllib.parse, re, json

def search(query):
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        results_blocks = re.findall(r'<a class="result__url" href="([^"]+)".*?>(.*?)</a>.*?<a class="result__snippet[^>]+>(.*?)</a>', html, re.DOTALL | re.IGNORECASE)
        
        output_data = {
            "query": query,
            "status": "success",
            "results": []
        }
        
        for link, title, snippet in results_blocks:
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            clean_snippet = re.sub(r'<[^>]+>', '', snippet).strip()
            clean_link = urllib.parse.unquote(link.strip())
            
            if clean_link.startswith('//duckduckgo.com/l/?'):
                match = re.search(r'uddg=([^&]+)', clean_link)
                if match: clean_link = urllib.parse.unquote(match.group(1))

            output_data["results"].append({
                "title": clean_title,
                "snippet": clean_snippet,
                "url": clean_link
            })
            
            if len(output_data["results"]) >= 4:
                break
                
        if len(output_data["results"]) == 0:
            output_data["status"] = "no_results_or_rate_limited"
            output_data["message"] = "DuckDuckGo blocked request. Fallback to Gemini deep_researcher suggested."

        print(json.dumps(output_data, indent=2, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"status": "error", "error_message": str(e)}, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "error_message": "Missing query argument."}, indent=2))
    else:
        search(" ".join(sys.argv[1:]))

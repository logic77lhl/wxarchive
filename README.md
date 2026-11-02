# wxarchive

> 缁欎竴涓井淇″叕浼楀彿閾炬帴锛屾妸瀹冨畬鏁村瓨鍒版湰鍦帮細Markdown + 绂荤嚎 HTML + 鍘熷浘锛屾寜骞存湀鏃ュ垎鏂囦欢澶广€?*涓嶉渶瑕佺櫥褰曪紝涓嶉渶瑕佹祻瑙堝櫒銆?*

[![PyPI](https://img.shields.io/badge/pypi-wxarchive-blue)](https://pypi.org/project/wxarchive/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://github.com/logic77lhl/wxarchive/actions/workflows/ci.yml/badge.svg)](https://github.com/logic77lhl/wxarchive/actions/workflows/ci.yml)

```bash
wxarchive "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=4020951985321934849" -o ./宸ョ▼濉戞枡
```

```
宸ョ▼濉戞枡/
鈹溾攢 _index.csv
鈹斺攢 2025/2025-06/2025-06-07_鍥藉唴PPS鍙戝睍鍘嗙▼涓庣幇鐘跺垎鏋?
   鈹溾攢 original.html    鍘熸枃瀹屾暣 DOM锛堝幓鑴氭湰锛夛紝鍥剧墖淇濈暀鍘熷澶栭摼
   鈹溾攢 index.html       鍥剧墖宸叉湰鍦板寲锛屽弻鍑诲嵆鍙绾块槄璇?   鈹溾攢 article.md       姝ｆ枃 Markdown锛屽彲鐩存帴缂栬緫
   鈹溾攢 meta.json        鏍囬 / 浣滆€?/ 鏃堕棿 / 鍘熷垱 / 鎽樿 / 鎵€灞炲悎闆?   鈹斺攢 images/001.jpg
```

---

## 鐗规€?
- **涓€涓摼鎺ユ悶瀹?*锛氳嚜鍔ㄨ瘑鍒€屽崟绡囨枃绔犮€嶅拰銆屽悎闆?涓撴爮銆嶏紝鍚堥泦鑷姩缈婚〉鎷垮叏閲忋€?- **鍘熸枃淇濈湡**锛氬悓鏃朵繚瀛樺師鏂?DOM 涓庤浆鎹㈠悗鐨?Markdown锛屽浘鐗囨寜椤哄簭钀藉湴锛屽崰浣嶅浘杩囨护銆侀噸澶嶅浘鍘婚噸銆?- **绂荤嚎鍙**锛氱敓鎴愮殑 `index.html` 涓嶄緷璧栫綉缁滐紝鏍峰紡鍐呰仈锛屾墜鏈轰笂涔熻兘鐪嬨€?- **鍙柇鐐圭画浼?*锛氫腑閫?Ctrl+C 鎴栨柇缃戯紝閲嶈窇鑷姩璺宠繃宸插畬鎴愶紝鍙ˉ澶辫触鐨勩€?- **涓嶆墦鎵版湇鍔″櫒**锛氶粯璁ゆ瘡绡囬殢鏈洪棿闅?1.2~2.8 绉掞紝鍗曠嚎绋嬶紝灏介噺涓嶈Е鍙戦鎺с€?- **瀵?agent 鍙嬪ソ**锛氳嚜甯?[SKILL.md](skills/wxarchive/SKILL.md)锛宱pencode / Claude Code / Cursor 瑁呬笂灏辫兘鐢ㄣ€?
## 瀹夎

```bash
pip install wxarchive
# 鎴栬€呬粠婧愮爜
git clone https://github.com/logic77lhl/wxarchive.git
cd wxarchive && pip install -e .
```

## 鐢ㄦ硶

```bash
# 1) 鍏堣瘯 3 绡?wxarchive "<閾炬帴>" -o ./out --limit 3

# 2) 鍏ㄩ噺涓嬭浇
wxarchive "<閾炬帴>" -o ./out

# 3) 鍙湅鐪嬫湁澶氬皯绡囥€侀兘鏄粈涔?wxarchive "<閾炬帴>" --list

# 4) 椤虹潃鏂囩珷閲岀殑鍚堥泦锛屾妸鍚岃处鍙峰叾浠栦笓鏍忎篃鎶撲簡
wxarchive "<閾炬帴>" -o ./out --follow-albums --max-albums 20
```

### 鍙傛暟

| 鍙傛暟 | 榛樿 | 璇存槑 |
|---|---|---|
| `url` | 鈥?| 鏂囩珷鎴栧悎闆嗛摼鎺ワ紝鍙紶澶氫釜 |
| `--out, -o` | `./wxarchive_out` | 淇濆瓨鏍圭洰褰?|
| `--limit N` | 0锛堜笉闄愶級 | 鏈€澶氫笅杞?N 绡?|
| `--delay a,b` | `1.2,2.8` | 姣忕瘒闂撮殧绉掓暟鍖洪棿 |
| `--no-images` | 鍏?| 涓嶄笅杞藉浘鐗?|
| `--no-original` | 鍏?| 涓嶄繚瀛?`original.html` |
| `--follow-albums` | 鍏?| 鎵╁睍鎶撳彇鏂囩珷鎵€灞炵殑鍏朵粬鍚堥泦 |
| `--max-albums N` | 10 | 鎵╁睍涓婇檺 |
| `--list` | 鍏?| 鍙垪鏍囬 |
| `--retry-failed` | 鍏?| 閲嶈瘯姝ゅ墠澶辫触鐨勬潯鐩?|

## 浣滀负 agent skill 浣跨敤

鎶?`skills/wxarchive/` 鏁翠釜鐩綍鎷峰埌浣犵殑 agent 鎶€鑳界洰褰曞嵆鍙細

| 宸ュ叿 | 鏀剧疆浣嶇疆 |
|---|---|
| opencode | `~/.config/opencode/skills/wxarchive/` |
| Claude Code | `~/.claude/skills/wxarchive/` |
| Cursor / 鍏朵粬 | 椤圭洰鍐?`.agents/skills/wxarchive/`锛堟寜浣犵殑绾﹀畾锛?|

涔嬪悗鐩存帴瀵?agent 璇淬€屾妸杩欎釜閾炬帴涓嬭浇涓嬫潵銆嶏紝瀹冧細鑷繁璋冪敤 `wxarchive`銆?
涔熷彲浠ュ畬鍏ㄤ笉鐢?skill锛岀洿鎺ヨ agent 鎵ц锛?
```bash
wxarchive "<URL>" -o "<鐩綍>"
```

## 宸ヤ綔鍘熺悊锛堜篃鏄俯杩囩殑鍧戯級

| 闂 | 瑙ｆ硶 |
|---|---|
| 鏂囩珷椤电粡甯歌繑鍥炪€屾湭鐭ラ敊璇?/ 澶辨晥鐨勯獙璇侀〉闈€?| URL 杩藉姞 `&scene=27`锛屽苟鐢ㄦ墜鏈哄井淇?UA |
| 鍚堥泦缈婚〉 | `mp/appmsgalbum?action=getalbum&album_id=...&f=json`锛?0 鏉?椤碉紝鐢?`begin_msgid`+`begin_itemidx` 缁炕 |
| 姝ｆ枃琚噿鍔犺浇 | 鍙?`#js_content`锛屾妸 `img[data-src]` 杩樺師鎴?`src` |
| 鍥剧墖闃茬洍閾?| 涓嬭浇鏃跺甫 `Referer: https://mp.weixin.qq.com/` |
| 1脳1 鍗犱綅鍥?/ 閲嶅浜岀淮鐮?| 灏忎簬 1KB 涓㈠純锛屽悓鏂?md5 鍘婚噸 |
| 椤甸潰 3.7MB 澶崰绌洪棿 | 瀛樺師鏂囨椂鍘绘帀 `script/style/link`锛屽崟绡囬檷鍒扮害 100KB |
| 寰俊 HTML 杞?Markdown 鍑虹幇绌?`###`銆乣2. 1.` | 杞崲鍚庡仛閽堝鎬ф竻鐞?|

## 宸茬煡闄愬埗

- **鍙鐩栧悎闆?涓撴爮鍐呯殑鏂囩珷**銆傚叕浼楀彿娌℃湁鍏紑鐨勩€屽叏閮ㄥ巻鍙叉秷鎭€嶆帴鍙ｏ紝涓嶅湪浠讳綍鍚堥泦涓殑鏂囩珷闇€瑕佺櫥褰曟€侊紙`uin` / `key` / `pass_ticket`锛夋墠鑳芥灇涓俱€?- **鎷夸笉鍒伴槄璇婚噺 / 鐐硅禐 / 鍦ㄧ湅**锛氳繖浜涜蛋 JS 鎺ュ彛锛岄潤鎬侀〉闈㈤噷娌℃湁銆?- 浠樿垂鏂囩珷銆佸凡鍒犻櫎鏂囩珷銆佽鎶樺彔鐨勩€屽垎浜瀷銆嶅唴瀹规棤娉曚笅杞芥鏂囥€?- 寰俊椋庢帶闅忔椂鍙兘鍙樺寲锛屽閬囧ぇ閲忓け璐ヨ闄嶄綆棰戠巼鎴栫◢鍚庡啀璇曘€?
## 鍚堣澹版槑

鏈」鐩粎鐢ㄤ簬**涓汉瀛︿範銆佸浠戒笌绂荤嚎闃呰**銆傛枃绔犵増鏉冨綊鍘熶綔鑰呭強鍏紬鍙锋墍鏈夛紝浜屾鍙戝竷銆佸晢鐢ㄣ€佹壒閲忔惉杩愰渶鑾峰緱鎺堟潈銆傝閬靛畧寰俊骞冲彴瑙勫垯涓庡綋鍦版硶寰嬶紝鍥犱娇鐢ㄦ湰椤圭洰浜х敓鐨勪换浣曞悗鏋滅敱浣跨敤鑰呰嚜琛屾壙鎷呫€?
## 寮€鍙?
```bash
pip install -e ".[dev]"
ruff check .
pytest -q
```

## License

[MIT](LICENSE)

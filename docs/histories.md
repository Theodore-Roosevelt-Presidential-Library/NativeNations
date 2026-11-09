# Histories (draft standard)

Short history summaries for nations and peoples, written in the Library's own words.

- **Status:** every summary is `draft` until reviewed through HistorianPanel and the Library's Indigenous content routing (for now, HistorianPanel; a named human reviewer is still to be chosen). Pages show a draft label until then.
- **Sources, in order:** the nation's own website and publications → tribal colleges and tribal historic preservation offices → state historical societies and encyclopedias (e.g. Encyclopedia of the Great Plains, MNopedia, Oklahoma Historical Society) → NPS and Smithsonian NMAI → peer-reviewed scholarship. Wikipedia may be used to find leads only; never as a sole source, and its text is never copied or closely paraphrased (CC BY-SA).
- **Every factual sentence** must trace to at least one listed source; dates, numbers and treaty names need two independent sources or are left out.
- **Voice:** TRPL style guide. Present tense for nations today; never describe a living nation as vanished. Use the names nations use for themselves. No quotes of any kind unless verified. No sacred or ceremonial details, no burial or massacre-site directions. Hard chapters (removal, boarding schools, massacres, termination) are stated plainly and factually without graphic detail.
- **Length:** nations 120–220 words; peoples 150–260 words.
- **File format:** `data/histories/nations/{id}.json` or `data/histories/peoples/{id}.json`:
  `{"id", "summary", "sources": [{"name","url"}], "status": "draft", "written", "notes"}`

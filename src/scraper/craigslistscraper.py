import craigslistscraper as cs
import json

search = cs.Search(
    query = "subaru brz",
    city = "SanFrancisco",
    category = "sby"
)

status = search.fetch()
if status != 200:
    raise Exception(f"Unable to fetch some search with status <{status}>.")

if len(search.ads) > 20: search.ads = search.ads[:20]
print(f"{len(search.ads)} ads found!")
data = []
for ad in search.ads:
    status = ad.fetch()
    if status != 200:
        print(f"Unable to fetch ad '{ad.title}' with status <{status}>.")
        continue

    if "subaru brz" in ad.title.lower():
        data.append(ad.to_dict())

print(json.dumps(data, indent=4))
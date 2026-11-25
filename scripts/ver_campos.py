import json
from pathlib import Path

d = json.loads(Path("amostra/pncp_itens_amostra.json").read_text(encoding="utf-8"))
compra = d[2]  # dispensa com resultado

item = compra["itens"]["dados"][0]
res = compra["resultados"]["dados"]
res = res[0] if isinstance(res, list) else res

print("ITEM:")
print(json.dumps(item, ensure_ascii=False, indent=1))
print("RESULTADO:")
print(json.dumps(res, ensure_ascii=False, indent=1))
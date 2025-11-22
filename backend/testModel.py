import argparse
import json
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
MODEL_DIR = os.path.join(PARENT_DIR, "data", "models", "finetuned_t5_model")
MAX_INPUT_LEN = 256
MAX_OUTPUT_LEN = 300

# ...existing code...

def run_with_input(input_text, structured=False, model_dir=MODEL_DIR, max_out_len=MAX_OUTPUT_LEN):
    """
    Rulează procesul de generare pentru un text (sau listă de texte) și returnează rezultatul.
    - input_text: str sau list[str]
    - structured: if True returnează structurat (JSON normalizat), altfel text generat
    - returnează dict sau list[dict]
    """
    tokenizer, model, device = load_model(model_dir=model_dir)

    if isinstance(input_text, list):
        inputs = [f"Completează fișa medicală: {t}" for t in input_text]
    else:
        inputs = [f"Completează fișa medicală: {input_text}"]

    if structured:
        res = generate_structured(tokenizer, model, device, inputs, max_out_len)
        # dacă a fost un singur text, returnăm un singur obiect
        return res if len(res) > 1 else (res[0] if res else {})
    else:
        preds = generate_texts(tokenizer, model, device, inputs, max_out_len)
        outs = [{"generated_text": p} for p in preds]
        return outs if len(outs) > 1 else outs[0]

# ...existing code...

def load_model(model_dir=MODEL_DIR):
    tokenizer = T5Tokenizer.from_pretrained(model_dir)
    model = T5ForConditionalGeneration.from_pretrained(model_dir)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    return tokenizer, model, device

def generate_texts(tokenizer, model, device, inputs, max_out_len=MAX_OUTPUT_LEN):
    enc = tokenizer(inputs, return_tensors="pt", padding=True, truncation=True, max_length=MAX_INPUT_LEN)
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.no_grad():
        outs = model.generate(
            **enc,
            max_length=max_out_len,
            num_beams=4,
            early_stopping=True,
        )
    return [tokenizer.decode(o, skip_special_tokens=True, clean_up_tokenization_spaces=True) for o in outs]

def _try_fix_and_parse_json(s):
    s = s.strip()
    if '{' in s and '}' in s:
        start = s.find('{')
        end = s.rfind('}')
        s = s[start:end+1]
    # common fixes: single -> double quotes
    if "'" in s and '"' not in s:
        s = s.replace("'", '"')
    # remove trailing commas before closing brackets/braces
    s = s.replace(",]", "]").replace(",}", "}")
    try:
        return json.loads(s)
    except Exception:
        return None

def generate_structured(tokenizer, model, device, inputs, max_out_len=MAX_OUTPUT_LEN):
    results = []
    for inp in inputs:
        # Modificarea promptului pentru a cere modelului doar JSON valid cu cele 4 câmpuri cerute
        prompt = (inp + "\n\nRăspunsul trebuie să fie strict JSON valid cu următoarele chei:\n"
                "boala (string) - numele bolii identificate,\n"
                "medicamente_recomandate (list of objects with keys: nume, doza, administrare) - tratamentul recomandat,\n"
                "investigatii_recomandate (list of strings) - investigații suplimentare necesare,\n"
                "recomandari_suplimentare (list of strings) - recomandări suplimentare pentru pacient.\n"
                "Exemplu: {\"boala\": \"astm bronșic\", "
                "\"medicamente_recomandate\": [{\"nume\": \"Salbutamol\", \"doza\": \"100 mcg\", \"administrare\": \"inhalator\"}], "
                "\"investigatii_recomandate\": [\"spirometrie\", \"radiografie toracică\"], "
                "\"recomandari_suplimentare\": [\"evitați expunerea la praf\", \"monitorizare simptome\"]}\n"
                "Returnează doar JSON valid, fără explicații.")

        enc = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=MAX_INPUT_LEN)
        enc = {k: v.to(device) for k, v in enc.items()}
        with torch.no_grad():
            out = model.generate(
                **enc,
                max_length=max_out_len,
                num_beams=5,  # Folosim mai multe raze pentru a îmbunătăți generarea
                early_stopping=True,
                do_sample=False,  # Nu folosim sampling pentru a controla mai strict generarea
            )
        
        # Decodifică rezultatul generat
        text = tokenizer.decode(out[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)

        # Încearcă să convertești rezultatul în JSON
        parsed = _try_fix_and_parse_json(text) or {}

        # Normalizează structura pentru a conține întotdeauna cheile așteptate
        normalized = {
            "boala": parsed.get("boala") if parsed.get("boala") is not None else None,
            "medicamente_recomandate": parsed.get("medicamente_recomandate") if isinstance(parsed.get("medicamente_recomandate"), list) else [],
            "investigatii_recomandate": parsed.get("investigatii_recomandate") if isinstance(parsed.get("investigatii_recomandate"), list) else [],
            "recomandari_suplimentare": parsed.get("recomandari_suplimentare") if isinstance(parsed.get("recomandari_suplimentare"), list) else [],
        }

        results.append(normalized)

    return results


def load_inputs_from_json(path="data.json", limit=None):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    inputs = []
    raw_filtered = []
    for item in data:
        if "input" in item:
            inputs.append(f"Completează fișa medicală: {item['input']}")
            raw_filtered.append(item)
            if limit and len(inputs) >= limit:
                break
    return inputs, raw_filtered

def main():
    parser = argparse.ArgumentParser(description="Testează modelul T5 finetuned.")
    parser.add_argument("--text", "-t", nargs="+", help="Text(e) de intrare pentru generare (escape spacing automat).")
    parser.add_argument("--from-json", "-j", action="store_true", help="Folosește intrările din data.json")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Număr maxim de exemple din JSON (implicit 10).")
    parser.add_argument("--structured", "-s", action="store_true", help="Generează output structurat (JSON) cu cheile dorite.")
    parser.add_argument("--out-file", "-o", help="Salvează output-ul JSON într-un fișier (implicit stdout).")
    args = parser.parse_args()

    tokenizer, model, device = load_model()

    outputs = []

    if args.text:
        inputs = [" ".join(args.text)]
        if args.structured:
            res = generate_structured(tokenizer, model, device, inputs)
            outputs = res
        else:
            preds = generate_texts(tokenizer, model, device, inputs)
            outputs = [{"generated_text": p} for p in preds]
    elif args.from_json:
        inputs, raw = load_inputs_from_json(limit=args.limit)
        if not inputs:
            print("Nu s-au găsit intrări în data.json (cheia 'input').")
            return
        if args.structured:
            res = generate_structured(tokenizer, model, device, inputs)
            # păstrează și datele originale pentru referință, fără câmp raw
            for item, r in zip(raw, res):
                # r is a normalized dict from generate_structured; ensure exact structure
                out_obj = {
                    "boala": r.get("boala") if r and r.get("boala") is not None else None,
                    "medicamente_recomandate": r.get("medicamente_recomandate") if r and isinstance(r.get("medicamente_recomandate"), list) else [],
                    "investigatii_recomandate": r.get("investigatii_recomandate") if r and isinstance(r.get("investigatii_recomandate"), list) else [],
                    "recomandari_suplimentare": r.get("recomandari_suplimentare") if r and isinstance(r.get("recomandari_suplimentare"), list) else [],
                }
                outputs.append(out_obj)
    else:
        txt = input("Introdu textul de test (Enter pentru a ieși): ").strip()
        if not txt:
            return
        inp = f"Completează fișa medicală: {txt}"
        if args.structured:
            res = generate_structured(tokenizer, model, device, [inp])[0]
            outputs = [res]
        else:
            pred = generate_texts(tokenizer, model, device, [inp])[0]
            outputs = [{"generated_text": pred}]

    # afișare / salvare
    if args.out_file:
        with open(args.out_file, "w", encoding="utf-8") as fo:
            json.dump(outputs, fo, ensure_ascii=False, indent=4)
        print(f"Output salvat în {args.out_file}")
    else:
        print(json.dumps(outputs, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()


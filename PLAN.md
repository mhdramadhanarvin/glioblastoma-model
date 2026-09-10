# Plan: From RAG Pipeline to Publishable Glioblastoma Model

**Goal:** a tiny, publicly accessible model on Hugging Face with specialized glioblastoma knowledge, distilled from the 1000 PDFs in `pdfs/`. Audience: anyone wanting to learn about glioblastoma, plus research and education use. Dataset published alongside.

**Status:** the current project cannot reach this goal as built. It is a *retrieval* system, not a *model*. Roughly 30% of the needed work exists — the PDF-ingest half. The model half does not exist, and the ingest half has a data-corrupting bug that must be fixed before anything downstream is worth training on.

**Timeline: ~2–3 days, $0.** All three compute needs are settled (§3): `gemma-4-26b` generates the data, Google Colab's free tier trains the model, this machine does everything else.

Nothing in this plan has been applied. No files were modified.

---

## 1. Verification: what this project actually does

Measured on disk, not from the docs.

| Component | State | Serves the goal? |
|---|---|---|
| `pdfs/` | **1000 PDFs**, 1988–2026, peak 2018–2021 | Yes — this is the asset |
| `src/pdf_extractor.py` | Works, but **corrupts 80% of output** (§2) | Yes, after fix |
| `data/markdown/` | 147 of 1000 extracted (14.7%), 652K words | Partial |
| `src/knowledge_indexer.py` | Works; chunk 2000/300 | **No** — indexes for search, produces no weights |
| `src/rag_query.py` | Works; `RetrievalQA` k=5 over `mistral` | **No** — but becomes the eval baseline (§5) |
| `data/vectorstore/` | **0 embeddings** — never built | n/a |
| `config.py` | Dead code, nothing imports it | No |
| 8 doc/status files | Stale, aspirational, wrong line numbers | No |
| `config/`, `models/`, `notebooks/` | Empty | No |
| Training stack | **Not installed** — no torch, transformers, peft, trl, datasets | Moves to Colab (§3) |

### The core gap

The goal says "tiny model … upload into Hugging Face." What exists is retrieval-augmented generation over a 4.4GB `mistral:latest` served by Ollama.

The difference is decisive:

- **RAG** keeps knowledge *outside* the model, in `data/vectorstore/`. Nothing is learned. There is no artifact to upload — a Chroma DB plus a pointer to someone else's 7B model is not a model.
- **A publishable model** carries the knowledge *in its weights*. It is a self-contained download that runs without your PDFs, your vectorstore, or your Ollama server.

The RAG pipeline is not wasted, but it is not on the path either. Its value is as an **evaluation baseline** (§5). Keep it, repurpose it.

### Second gap: 6M tokens is not pretraining data

All 1000 PDFs come to roughly **6.0M tokens** (measured: 4,465 words/doc average, extrapolated, ×1.35). Pretraining a small model from scratch needs 10–100 **billion** tokens — three to four orders of magnitude more.

Not a problem; it settles the method. **Fine-tune an existing small base model with LoRA.** Pretraining from scratch is off the table.

---

## 2. Blocker: the extraction bug

`src/pdf_extractor.py:26` calls `page.extract_text()` with default settings. On two-column academic PDFs this loses inter-word spaces:

```
Glioblastomamultiforme(GBM)isthemostaggressivetypeofbraintumor.Molecularhet-
```

Measured over the 147 extracted files, counting runs of 25+ letters with no space:

- **117 / 147 files (80%) affected**
- Worst file: 1,438 mashed runs
- Only 19 / 147 files clean

Fatal for the goal. Train on this and the model learns to emit unspaced word salad. Every downstream step inherits it.

**Cause:** pdfplumber's default `x_tolerance=3` is too wide for tight academic typesetting; it merges characters across word gaps.

**Fix:** `extract_text(x_tolerance=1)`. Verified on a 12-PDF random sample: **377 mashed runs → 0. 100% eliminated.** Character yield also rose (3,561 → 4,006 on the test page), so real text was being lost, not just spaces. `layout=True` does *not* fix it (still 37 runs) — do not use it.

Second, smaller issue: the title heuristic at `pdf_extractor.py:52` takes the first line over 10 characters, yielding journal furniture instead of titles — `RESEARCHARTICLE`, `PLOS GENETICS`, `METHODS AND RESOURCES`. About a third are unusable, which now matters directly because published-dataset attribution needs real titles (§6).

**All 147 existing markdown files must be re-extracted.** Not salvageable by post-processing — the spaces are gone, and re-inserting them requires word-segmentation inference that will corrupt medical terminology.

---

## 3. Compute: three machines, each doing what it is good at

| Job | Where | Cost | Time |
|---|---|---|---|
| Extraction, provenance, filtering, eval, publishing | **This machine** | $0 | hours |
| QA-pair generation (the teacher) | **`gemma-4-26b`** via tunnel | $0 | ~2.6h |
| LoRA training | **Google Colab free T4** | $0 | ~1.5h |

### The teacher: `gemma-4-26b`, already running

Served under vLLM on a remote box, reachable here through an SSH tunnel at `http://localhost:8000/v1` (confirmed — `ss` shows sshd holding :8000). Measured, not assumed:

| Test | Result |
|---|---|
| `/v1/models` | Responds. `google/gemma-4-26B-A4B-it`, `max_model_len: 8192` |
| Single request | ~100 tok/s, correct MGMT answer in 0.9s |
| 16 concurrent | **835 tok/s** aggregate, 16/16 succeeded |
| 32 concurrent | **1287 tok/s** aggregate, 32/32 succeeded |

At 1287 tok/s the entire QA dataset generates in **~2.6 hours**. This is a stronger teacher than anything you could self-host for this project, and it costs nothing.

**Why gemma cannot be the published model.** Verified directly against the endpoint:

```
"allow_fine_tuning": false
/v1/fine_tuning/jobs  -> HTTP 404
/v1/fine-tunes        -> HTTP 404
```

vLLM is an *inference* server — it serves tokens from frozen weights and contains no training code path. This is architectural, not a permission someone can flip. Beyond that: 26B is roughly a 52GB download, which is not "tiny"; and the weights are Google's, on someone else's server, so publishing them would be republishing gemma rather than creating a glioblastoma model.

**What you get instead:** gemma's knowledge transfers into your small model through the training data it writes. That is the whole point of teacher–student distillation, and it is the correct way to use this endpoint.

Two constraints to respect, since the box is shared and not yours to reconfigure:
- **`max_model_len` is 8192.** Prompt + completion must fit. Chunk at ~2000 chars (~600 tokens) and this is comfortable.
- **It is someone else's service.** Cap concurrency at 32 (measured-good), retry with backoff, and checkpoint per document so a busy or restarted server never costs completed work.

### Training: Google Colab free tier

Training requires a GPU. This machine has none — an **i7-1165G7, 4 physical cores, laptop-class**, with 3.0GB RAM free of 15GB. Measured comparison for the same LoRA job:

| Where | Config | Time | Cost |
|---|---|---|---|
| **Colab free T4** | 25K ex, 3 epochs, seq 2048 | **~1.7h** | **$0** |
| **Colab free T4** | 15K ex, 2 epochs | **~0.7h** | **$0** |
| This machine, best case | 8K ex, 2 epochs, seq 512, r=8 | **22.5h** | $0 |
| This machine, full config | 25K ex, 3 epochs | 120h+ | $0 |

Colab free is **20–30× faster than local CPU for an identical result**, at the same price. Local CPU training is therefore not in this plan; it exists only as a note in §7.

Transfers are trivial — measured: dataset JSONL for 25K rows is **~37MB** up, and what comes back is a **~40MB** adapter, a **~1.2GB** merged model, and a **~400MB** GGUF. 115GB free here, so no storage concern.

**Colab free-tier limits to design around** — these shape `train.py`, so they are requirements, not trivia:
- Sessions are capped (roughly 12h, often less) and can be reclaimed at any time when GPUs are in demand.
- **Therefore: checkpoint to Google Drive every ~200 steps, and make the notebook resumable from the last checkpoint.** A disconnect must cost minutes, not the run. This is the single most important detail of Phase 4.
- T4 is 16GB and does **not** support bf16 — use **fp16** with gradient checkpointing. A 0.6B LoRA fits with room to spare.
- Mount Drive at the start; write checkpoints, adapter, and logs there, never to the ephemeral local disk.

### Base model: Qwen3-0.6B

| Base | Params | License | Verdict |
|---|---|---|---|
| **Qwen3-0.6B** | 0.6B | **Apache 2.0** | **Recommended** |
| Qwen3-1.7B | 1.7B | Apache 2.0 | Optional second variant — fits Colab free, ~2.5h |
| Llama-3.2-1B | 1.2B | Llama Community | Rejected — license conditions |
| SmolLM2-360M | 0.36B | Apache 2.0 | Fallback only |

Reasoning:

- **Apache 2.0 is the deciding factor.** You publish a model *and* a dataset for public reuse. Llama's community license carries naming and acceptable-use conditions that propagate to your release and add friction for exactly the "anyone" audience you named. Apache 2.0 does not.
- **Strongest base at this size** on reasoning and technical text — what a biomedical corpus demands.
- **Genuinely tiny.** ~1.2GB fp16, ~400MB at Q4. Runs on CPU, in-browser, on a phone. That is what "publicly accessible for everyone" means in practice.
- **Same family at 1.7B**, so both variants share tokenizer and chat template — one card, one usage snippet. Worth training if the first run goes smoothly; Colab free handles it.

---

## 4. Target architecture

```
pdfs/ (1000)
   │
   ├─ [FIX] extract x_tolerance=1 ──→ data/markdown/  (1000 clean .md)   [this machine]
   │                                        │
   │                                        ├─→ [KEEP] index → vectorstore → RAG
   │                                        │        (evaluation baseline, §5)
   │                                        │
   │                                        ├─→ [NEW] Crossref resolve → data/metadata.json
   │                                        │
   │                                        └─→ [NEW] QA gen via gemma-4-26b endpoint
   │                                                 │            (~2.6h, 32-way concurrent)
   │                                             data/dataset/ (JSONL + per-row attribution)
   │                                                 │
   │                                             [NEW] filter → 15-25K pairs
   │                                                 │
   │                                    ── upload 37MB ──→ [NEW] Colab LoRA train (~1.5h)
   │                                                 │              │
   │                                                 └──── adapter ─┘
   │                                                 │
   │                                             [NEW] eval vs base + RAG
   │                                                 │
   │                                             [NEW] publish → HF (model + dataset)
```

Existing modules stay untouched except the extractor fix and title heuristic. Everything new lands in new files.

---

## 5. Steps

### Phase 1 — Fix extraction, build the corpus *(this machine, ~2h)*

**1.1 Fix the space bug**
`src/pdf_extractor.py:26`: `page.extract_text()` → `page.extract_text(x_tolerance=1)`.

**1.2 Fix the title heuristic**
Replace "first line >10 chars" with: skip journal furniture (`RESEARCH ?ARTICLE`, `PLOS`, `Perspectives`, `METHODS AND RESOURCES`, all-caps under 30 chars), prefer the longest line in the first 15 containing a lowercase letter, fall back to the PDF filename stem — which already carries year and title. Titles feed dataset attribution now, so this is no longer cosmetic.

**1.3 Add a quality gate**
New method on `PDFExtractor`: reject a document with >5 mashed runs (25+ letters, no space), under 500 words, or no extractable text. Write rejects to `data/rejected.json` with reasons. This guard is what stops the §2 bug recurring silently.

**1.4 Re-extract everything**
Delete all 147 existing `.md` (corrupt). Re-run over all 1000 PDFs. 30–60 min.

**Gate:** ≥900 of 1000 pass. Read 5 random outputs end to end and confirm clean prose. **Do not proceed until this holds** — every later phase inherits this text.

---

### Phase 2 — Resolve provenance *(this machine, ~4h)*

Needed because you are publishing the dataset. Attribution cannot be scraped from the extracted text — measured: only **107/147 docs carry a detectable license statement**, and while 129/147 contain DOIs, those total **2,586 DOIs** corpus-wide, overwhelmingly *references* rather than each paper's own. Regex cannot tell them apart.

**2.1 Resolve against Crossref**
New file `src/resolve_metadata.py`. Query the Crossref REST API (free, no key) by title + year parsed from each filename. Retrieve authoritative DOI, title, authors, journal, year, license URL. Cache to `data/metadata.json`. Fall back to OpenAlex on misses. Be polite: mailto in the User-Agent, a few requests/sec.

**2.2 Classify reuse rights**
Bucket per paper from the resolved license: CC-BY / CC-BY-SA (redistributable with attribution), CC-BY-NC (non-commercial), other-or-unknown (do not republish source text).

Publisher mix measured on the extracted sample is encouraging — Cancers/MDPI 456 hits, PLOS Genetics 125, Neuro-Oncology 122, PLOS Comp Bio 110, eLife 27, PLOS ONE 19, BMC 15, Scientific Reports 13, Frontiers 13 — all open-access venues. Bucket per paper anyway; do not infer from venue.

**2.3 Flag unresolved for manual review**
Expect 5–15% needing a hand. A short list is fine; publishing unattributed text is not.

**Gate:** every paper contributing to the published dataset has a resolved DOI and known license.

---

### Phase 3 — Build the training dataset *(this machine + gemma, ~2.6h run)*

The phase that does not exist yet and matters most. Model quality is dataset quality.

**3.1 Format**
Instruction-tuning JSONL, one object per line:
```json
{"messages":[{"role":"system","content":"..."},{"role":"user","content":"..."},{"role":"assistant","content":"..."}],
 "source_doi":"10.xxxx/yyyy","source_title":"...","license":"CC-BY-4.0"}
```
Standard for TRL's `SFTTrainer`. Provenance rides along per row so the published dataset is attributable at row level.

**3.2 Generate against the gemma endpoint**
New file `src/dataset_builder.py`. Plain `httpx` + `asyncio` against `http://localhost:8000/v1/chat/completions` — no LangChain, no Ollama needed here. For each clean markdown doc, chunk to ~2000 chars and request 3–5 grounded QA pairs per chunk.

Engineering requirements, given it is a shared server:
- **32-way concurrency**, semaphore-bounded (measured good: 1287 tok/s, 32/32 success).
- **Retry with exponential backoff** on timeout, 429, 5xx.
- **Checkpoint after every document** to `data/dataset/raw/` so a restart resumes rather than redoes.
- **Request JSON and validate it**; discard malformed rather than repairing.
- Keep prompt + completion under 8192 tokens.

Prompt must enforce: answers drawn only from the chunk, no outside knowledge, **no "according to the provided text" phrasing** (it pollutes the model's voice and makes it sound broken when used without retrieved context), factual and specific.

Because the audience includes non-specialists, deliberately spread the register:

- **Plain-language explainers** ("What is glioblastoma?", "Why is it hard to treat?") — target ~25% of pairs
- Definitions and terminology (MGMT, IDH, EGFR, TMZ)
- Mechanisms and pathways
- Treatment and standard of care
- Prognosis and biomarkers
- Study findings and methodology — for the research audience

A model that answers only in journal register fails half your stated audience.

Expected yield: 1000 docs × ~15 chunks × 4 pairs ≈ **40–60K raw pairs** in ~2.6h.

**3.3 Filter hard**
New file `src/dataset_filter.py`. Drop: answers under 20 words or over 400; answers containing "the text does not", "not mentioned", "as stated above"; near-duplicate questions (normalized similarity); residual mashed runs; QA whose answer has no lexical overlap with its source chunk (hallucination signal).

Expect to keep **50–70%**. A filtered 25K beats a raw 60K.

**3.4 Hold out a test set**
Split **by source document, not by row** — 90/5/5 train/val/test. Row-level splitting leaks the same paper into train and test and makes eval numbers meaningless.

**Gate:** ≥15K filtered pairs. Hand-read 20 and confirm each is supported by its source chunk.

---

### Phase 4 — Train on Colab *(~1.5h)*

**4.1 Write the notebook**
New file `train_colab.ipynb` (kept in-repo so it is versioned and reproducible). Cells:

1. `pip install -q transformers peft trl datasets accelerate bitsandbytes`
2. Mount Google Drive — **all** checkpoints, adapters, and logs go there
3. Upload or pull the 37MB dataset JSONL
4. Load Qwen3-0.6B, attach LoRA, train
5. Merge adapter into base, save to Drive
6. Download adapter + merged model

**4.2 Config**
LoRA r=32, alpha=64, dropout 0.05, targeting all attention and MLP projections. lr 2e-4 cosine with warmup, 3 epochs, per-device batch 4 + grad-accum 8 (effective 32), **fp16** (T4 has no bf16), seq_len 2048, packing on, gradient checkpointing on.

**4.3 Survive disconnection — the one thing that must not be skipped**
Colab free reclaims GPUs without warning. Therefore:
- `save_steps=200`, `save_total_limit=3`, `output_dir` on Drive
- On start, detect the latest checkpoint and pass `resume_from_checkpoint`
- Keep the run under ~2h so it fits a single session comfortably

Get this right and a disconnect costs minutes. Get it wrong and it costs the run — repeatedly.

**4.4 Merge and (optionally) train the 1.7B**
Merge the adapter into base weights and save standalone, so users need no PEFT install. Keep the adapter too (~40MB) — worth publishing separately. If the 0.6B run went cleanly, run Qwen3-1.7B on the same config (~2.5h on T4) and publish both sizes.

**Gate:** validation loss below base on the same set, and clean spaced prose (the §2 regression check).

---

### Phase 5 — Evaluate honestly *(this machine, ~4h)*

Skipping this makes the HF upload a liability rather than a contribution. Publishing a medical model with unmeasured accuracy is the one genuinely irresponsible outcome available here — and with a general-public audience more so, because those readers cannot catch the model's mistakes themselves.

**5.1 Build the eval**
New file `eval.py`. On the held-out test set from 3.4, score: base 0.6B, tuned 0.6B, base + RAG, tuned + RAG. This is where the existing `rag_query.py` earns its keep.

Metrics:
- **(a)** Loss/perplexity on held-out text
- **(b)** Keyword recall on questions with known answers — MGMT methylation, IDH status, temozolomide dosing, standard-of-care sequence (maximal safe resection → RT + concurrent TMZ → adjuvant TMZ), median survival
- **(c)** 50-question manual read, scored 1–5 for factual correctness against source PDFs
- **(d)** *Because of the audience:* 15 plain-language questions a patient or student would actually ask, scored for correctness **and** for being understandable without a biology degree

**5.2 Check the expected failure modes**
Small fine-tunes regress predictably. Test each: catastrophic forgetting (general non-medical questions, confirm coherence), fabricated citations and numbers, degenerate repetition, and — critical for a public audience — whether it confidently answers what it should decline (individual prognosis, "should I take this drug").

**5.3 Decide against a real bar**
Ship only if the tuned model beats base on domain questions *and* has not collapsed on general ones. If it loses to base+RAG on factual accuracy — normal for a sub-1B model on a knowledge-heavy domain — say so plainly in the model card. That result is honest and still worth publishing.

**Gate:** measurable improvement over base on domain questions, no catastrophic forgetting, no confident answers to individual-medical-advice prompts.

---

### Phase 6 — Publish *(this machine, ~4h)*

**6.1 Publish the dataset**
Using the Phase 2 buckets:

- **CC-BY / CC-BY-SA:** publish QA pairs with full per-row attribution (DOI, title, journal, license). Include a short grounding excerpt (1–2 sentences, quoted) rather than the full source chunk — enough to verify an answer, short enough to stay clearly fair-use rather than republication.
- **CC-BY-NC:** hold out of the main dataset to keep it permissive, and note the exclusion. Or ship as a separate NC-licensed split.
- **Unknown or restrictive:** exclude from the dataset. They can still inform the model weights.

Dataset card must state: source count and year range, that pairs were **generated by `gemma-4-26B-A4B-it`** — so teacher errors are baked in and the data is not human-verified — the filtering applied, the document-level split, and per-row licensing. Ship `src/dataset_builder.py` and `src/dataset_filter.py` so anyone can reproduce or extend it.

**6.2 Write the model card**
The most important artifact after the weights. State: base model and license, training data provenance and generation method, eval numbers **including where it loses**, corpus recency ceiling (§7.3), and intended use.

**Non-negotiable, given a general-public audience:** an explicit statement that this is a research and education tool — **not** a clinical decision-support system, not for diagnosis, treatment decisions, or individual prognosis — and that outputs must be verified against primary literature. Include known failure modes and a line directing anyone facing an actual diagnosis to their oncology team. **This belongs at the top of the card, not buried at the bottom.**

**6.3 Upload**
`hf` CLI. Model, adapter, dataset, cards, eval results, generation scripts, `train_colab.ipynb`. Tag `medical`, `glioblastoma`, `neuro-oncology`, `qwen3`, `question-answering`.

**6.4 Add GGUF quant**
Convert to GGUF (Q4_K_M) so it runs in Ollama and llama.cpp — ~400MB for the 0.6B, runs on any laptop. That is what "accessible for everyone" means in practice. An ONNX export additionally enables in-browser inference via transformers.js with no install at all.

---

## 6. Effort

| Phase | Where | Work | Wall clock |
|---|---|---|---|
| 1 — Fix extraction | This machine | 1 line + 2 methods | 1h work, 1h run |
| 2 — Provenance | This machine | 1 new file | 3h work, 1h run |
| 3 — Dataset | This machine + gemma | 2 new files | 5h work, **2.6h generation** |
| 4 — Train | **Colab free** | 1 notebook | 2h work, **~1.5h run** |
| 5 — Eval | This machine | 1 new file | 4h work + manual scoring |
| 6 — Publish | This machine | 2 cards | 4h |

**Total: ~2–3 days. Cost: $0.**

Nothing on the critical path costs money or waits on hardware you do not have.

---

## 7. Where this could fail

Stated plainly so they are decisions, not surprises.

1. **A sub-1B model may not beat base + RAG on factual recall.** Likely, honestly. Small models are weak at memorizing dense factual detail. Mitigation: publish both — the fine-tune for fluent domain language and offline use, the RAG recipe for maximum accuracy. Say which is which in the card.
2. **Teacher errors propagate.** `gemma-4-26b` answered the MGMT test question correctly and fluently, but it will still make mistakes and your model will learn them. Mitigation: aggressive filtering (3.3), grounding checks, manual audit of 20+ pairs, and disclosure in both cards that the data is model-generated and not human-verified.
3. **Corpus skew toward 2018–2021.** The year histogram peaks there, with only 45 papers from 2024–2026. The model will underweight recent developments. Mitigation: state the recency ceiling in the model card.
4. **Method skew toward computational work.** Many corpus titles are systems biology, network analysis, radiomics, PDE models. The model will be stronger on research methodology than clinical practice. Mitigation: be explicit about intended use; do not present it as a clinical tool.
5. **Two dependencies you do not control.** The gemma endpoint could restart mid-generation; Colab could reclaim the GPU mid-training. Both are handled by the same discipline — checkpoint constantly, resume automatically (3.2, 4.3). If Colab free becomes unusable, a rented L40S hour is ~$0.50 and finishes in 32 minutes; local CPU is 22h+ and is the last resort, not the fallback.
6. **Public audience raises the stakes on every error above.** A researcher spots a wrong claim; a worried family member may not. This is the argument for the plain-language eval track (5.1d), the decline-to-answer test (5.2), and a prominent disclaimer (6.2) — not optional extras given who this is for.

---

## 8. Decisions locked

| Question | Answer |
|---|---|
| Audience | General public + research/education |
| Base model | **Qwen3-0.6B** (Apache 2.0); Qwen3-1.7B optional second variant |
| Teacher | **`gemma-4-26b`** at `localhost:8000/v1`, 32-way concurrent, ~2.6h for full dataset |
| Training | **Google Colab free T4**, LoRA, fp16, Drive-checkpointed and resumable |
| Dataset | **Published**, per-row attribution, CC-BY rows only |
| Corpus rights | All 1000 PDFs cleared, no paywalled sources |
| Cost | **$0** |

Every compute question is now settled. Phase 1 — the extractor fix and re-extraction of all 1000 PDFs — is the blocker for everything downstream and is ready to run.

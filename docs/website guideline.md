Dokumen Eksekusi: Revamp Website RAG Variance Explainer untuk Analis
Versi: 1.0
Tujuan: Mengubah website dari “penjelasan proyek riset” menjadi “halaman yang langsung dipahami analis keuangan”, tanpa menghilangkan detail teknis.
Output: Dokumen ini bisa langsung dipakai sebagai acuan desain, penulisan konten, dan implementasi teknis.

1. Ringkasan Eksekutif & Tujuan
1.1 Masalah Saat Ini
Pengunjung (analis) tidak langsung paham apa manfaat alat ini.

Istilah teknis (RAG, variance explainer, workflow) mendominasi.

Tidak ada contoh output end-to-end yang bisa dilihat.

Pesan “No approved case yet” membuat kesan produk belum siap pakai.

1.2 Tujuan Revamp
Dalam 10 detik pertama, analis mengerti: “Ini alat untuk menjelaskan kenapa angka keuangan berubah, dengan kutipan dari laporan SEC.”

Dalam 30 detik, analis melihat contoh output (pertanyaan → jawaban → kutipan → verifikasi).

Detail metodologi tetap tersedia, tapi tersembunyi di lapisan kedua (progressive disclosure).

Membangun kepercayaan melalui transparansi verifikasi dan limitasi.

1.3 Metrik Keberhasilan
Bounce rate turun (target: < 50%).

Waktu di halaman > 1 menit.

Klik ke contoh interaktif > 30% pengunjung.

Feedback kualitatif: “Saya mengerti ini buat apa” dari minimal 3 analis.

2. Target Audiens & Persona
Persona	Kebutuhan	Level Teknis	Yang Dicari
Analis Ekuitas / Kredit	Cepat menemukan penjelasan variance dari filing	Rendah–menengah	Output, kutipan, trust
Analis Riset Junior	Belajar cara membaca MD&A dan menghubungkan driver	Rendah	Contoh, panduan
Manajer Investasi	Validasi tesis investasi	Rendah	Ringkasan, sumber
Engineer / Researcher	Memahami metodologi, evaluasi	Tinggi	Detail arsitektur, failure modes
Fokus utama: Analis Ekuitas/Kredit. Engineer adalah audiens sekunder.

3. Prinsip Desain & Konten
Analyst-first language – Gunakan istilah finance, bukan AI. “RAG” hanya di bagian Under the hood.

Progressive disclosure – Informasi penting di atas, detail di expandable/accordion atau halaman terpisah.

Show, don’t tell – Tampilkan contoh output nyata (walaupun ilustratif) daripada menjelaskan workflow.

Trust by design – Setiap klaim harus punya kutipan, status verifikasi, dan limitasi.

No dead ends – Selalu ada CTA: coba contoh, lihat method, hubungi.

Mobile-first – Banyak analis membaca di ponsel/tablet.

Aksesibilitas – Kontras cukup, navigasi keyboard, alt text.

4. Information Architecture (Sitemap & Navigasi)
4.1 Struktur Halaman
text
/ (Landing Page)
├── #example (Contoh Interaktif)
├── #how-it-works (Cara Kerja Singkat)
├── #trust (Trust & Limitations)
├── /method (Halaman Metodologi untuk Engineer)
├── /about (Tentang Proyek & Tim)
└── /contact (Request a Filing Case / Feedback)
4.2 Navigasi Utama
Logo / Nama Proyek (kiri)

Menu: Example | How it works | Trust | Method | About (kanan)

CTA kanan: “Try an example” (button primary)

4.3 Navigasi Mobile
Hamburger menu, CTA sticky di bawah: “Try an example”.

5. Struktur Halaman Utama (Landing Page)
Setiap section dilengkapi: Tujuan, Layout, Copy, Komponen.

Section 1: Hero
Tujuan: Menjawab “ini buat apa?” dalam 10 detik.

Layout:

Kiri: Headline + subheadline + 2 CTA + trust badges.

Kanan: Mockup kartu contoh output (mini).

Background: netral, aksen biru/hijau.

Copy (English):

Headline:
Understand what moved in the financials—with citations from the filing.

Subheadline:
Ask why a metric changed. Get a concise explanation pulled from the company’s own 10-K/10-Q language, with the exact quote, section, and page so you can verify it.

CTA Primary: Try an illustrative example
CTA Secondary: See how it works

Trust badges:
✅ Citation-backed • ✅ Evidence panel • ✅ Not investment advice

Versi Indonesia (jika target lokal):

Headline:
Pahami penyebab perubahan metrik keuangan—dengan kutipan dari laporan SEC.

Subheadline:
Ajukan pertanyaan seperti “kenapa gross margin turun?” dan dapatkan penjelasan ringkas dari MD&A serta catatan kaki, lengkap dengan kutipan, section, dan halaman agar bisa diverifikasi.

CTA: Coba contoh ilustratif | Lihat cara kerjanya

Komponen:

Hero component

Badge untuk trust indicators

Button primary/secondary

MiniExampleCard (menampilkan pertanyaan + jawaban 1 baris + kutipan mini)

Section 2: Problem (Pain Points)
Tujuan: Mengasosiasikan diri dengan masalah analis.

Layout: 3 kolom kartu.

Copy:

Why variance analysis is slow today

Filings are long. MD&A explanations are buried in hundreds of pages.

Manual search is time-consuming. Cross-referencing footnotes and tables takes hours.

Hard to audit. Copy-pasting quotes risks losing the source link.

We built a way to ask a question and get a filing-backed answer—with the evidence attached.

Komponen: FeatureCard dengan icon.

Section 3: Contoh Interaktif (Example)
Tujuan: Menunjukkan output end-to-end. Ini section paling penting.

Layout:

Dua kolom di desktop: kiri form pertanyaan & contoh pertanyaan, kanan panel output.

Di mobile: stacked.

Komponen:

QuestionSelector – dropdown / chips contoh pertanyaan:

“Why did gross margin decline in Q3?”

“What drove the increase in SG&A?”

“Why did operating cash flow change?”

AskButton – “Explain with citations”

AnswerPanel – menampilkan:

Driver summary (2–3 baris)

Evidence excerpt (blockquote)

Citation (filing type, section, page, link)

Verification status (badges: Source retrieved ✓, Quote matches ✓, Answer grounded ✓, Human approved ⏳)

Limitations note (contoh: “This example is illustrative and not investment advice.”)

ExampleDisclaimer – banner kecil di atas panel: “Illustrative example — not investment advice.”

Copy untuk contoh (mock data):

Question: Why did gross margin decline in Q3?

Answer: Management cites higher input costs and an unfavorable product mix as the primary drivers of the gross margin decline.

Evidence:

“Gross margin decreased 120 basis points primarily due to higher commodity costs and unfavorable product mix, partially offset by pricing actions.”
— 10-Q, MD&A, p. 42

Verification:
✅ Source retrieved from SEC EDGAR
✅ Quote matches filing text
✅ Answer grounded in quote
⏳ Human review pending (illustrative only)

Section 4: What You Get
Tujuan: Menjelaskan output secara ringkas.

Layout: 4 kartu fitur.

Copy:

What you get

Driver summary — A short explanation of what management says drove the change.

Quoted evidence — The exact excerpt from the filing, not a paraphrase.

Source link — Filing type, section, page, and URL to verify.

Verification status — See which checks passed and what’s still pending.

Komponen: FeatureCard dengan icon.

Section 5: How It Works (Simple)
Tujuan: Menjelaskan alur tanpa jargon.

Layout: 3 langkah horizontal dengan panah.

Copy:

How it works

Ask a question — In plain English, about a metric that changed.

We search the filing — MD&A, footnotes, and tables are scanned for relevant explanations.

Get a cited answer — A concise summary with the exact quote and a link to the source.

Under the hood: retrieval-augmented generation (RAG) with evidence verification. [Read the method →]

Komponen: StepCard + link ke /method.

Section 6: Trust & Limitations
Tujuan: Membangun kepercayaan dan mengelola ekspektasi.

Layout: Dua kolom: “What we check” dan “What we don’t do”.

Copy:

Trust & limitations

What we check

Quote matches the filing text.

Answer is grounded in the quoted excerpt.

Source is linked to the original SEC document.

Human review status is shown.

What we don’t do

We don’t provide investment advice.

We don’t guarantee completeness of all drivers.

We don’t replace your own due diligence.

This is an illustrative prototype. Approved real-filing cases will be added as they pass review.

Komponen: CheckList dan CrossList.

Section 7: For Engineers / Method (Teaser)
Tujuan: Menyediakan jalur untuk audiens teknis tanpa mengganggu analis.

Layout: Banner dengan CTA ke /method.

Copy:

For engineers & researchers
Dive into the retrieval pipeline, evidence verification, evaluation metrics, and failure modes.
[Read the method →]

Section 8: Final CTA
Tujuan: Mendorong aksi.

Layout: Center-aligned, background aksen.

Copy:

Ready to see it in action?
Try the illustrative example or request a filing case for review.
[Try an example] [Request a case]

Section 9: Footer
Tujuan: Navigasi sekunder & legal.

Copy:

RAG Variance Explainer — Illustrative research prototype.
Not investment advice.
[Method] [About] [Contact] [GitHub]

6. Halaman Pendukung
6.1 /method — Metodologi untuk Engineer
Tujuan: Detail teknis lengkap.

Struktur:

Overview — Arsitektur high-level (diagram).

Retrieval — Chunking, embedding, MD&A parsing, table extraction.

Generation — Prompt design, grounding, citation extraction.

Verification — Quote matching, entailment check, human review.

Evaluation — Metrics, benchmark, failure modes.

Limitations & Roadmap.

Appendix — Data schema, API, code snippets.

6.2 /about — Tentang Proyek
Isi:

Latar belakang proyek.

Tim / kontributor.

Status (prototype, roadmap).

Cara berkontribusi.

6.3 /contact — Request a Filing Case
Isi:

Form: Nama, Email, Perusahaan/Filing yang ingin dianalisis, Pertanyaan.

Atau link ke Typeform/Tally.

Copy: “Request a filing case for review. We’ll add approved cases to the example library.”

7. Design System
7.1 Warna
Primary: #2563EB (biru) — CTA, link.

Secondary: #10B981 (hijau) — verifikasi positif.

Warning: #F59E0B (kuning) — pending status.

Neutral: #F9FAFB (background), #111827 (text), #6B7280 (secondary text).

Border: #E5E7EB.

7.2 Tipografi
Font: Inter (sans-serif) untuk UI, JetBrains Mono untuk code.

Headline: 48px/56px bold (desktop), 32px/40px (mobile).

Subheadline: 20px/28px regular.

Body: 16px/24px.

Caption: 14px/20px.

7.3 Spacing
Skala 4px: 4, 8, 12, 16, 24, 32, 48, 64, 96.

Section padding: 64px vertikal (desktop), 40px (mobile).

7.4 Komponen
Button: primary (biru solid), secondary (outline), ghost.

Card: border 1px, radius 12px, shadow subtle.

Badge: rounded-full, small text, warna sesuai status.

Blockquote: border-left 4px biru, background #F3F4F6, padding 16px.

Accordion: untuk progressive disclosure.

Tabs: untuk “Analyst view” vs “Engineer view” (opsional).

7.5 Aksesibilitas
Kontras minimal 4.5:1.

Focus ring visible.

Alt text untuk semua gambar.

Navigasi keyboard untuk interactive example.
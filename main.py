import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import zipfile
import io

st.set_page_config(page_title="PDF Summarizer", page_icon="📄")
st.title("📄 AI PDF Summarizer")
st.write("Upload satu atau banyak file PDF sekaligus — AI akan merangkum semuanya dalam Bahasa Indonesia!")

API_KEY = os.environ.get("GEMINI_API_KEY", "TARO DI SINI API KEY NYA")
genai.configure(api_key=API_KEY)

def baca_pdf(file):
    pembaca = PdfReader(file)
    teks = ""
    for halaman in pembaca.pages:
        teks += halaman.extract_text() or ""
    return teks

def rangkum_dengan_ai(teks, nama_file):
    model_ai = genai.GenerativeModel("gemini-2.5-flash")
    instruksi = f"""
    Nama dokumen: {nama_file}
    
    Tolong baca teks berikut ini, kemudian buatkan rangkumannya secara detail 
    dalam Bahasa Indonesia yang baik dan mudah dipahami.
    Sertakan:
    1. Ringkasan utama (2-3 kalimat)
    2. Poin-poin penting
    3. Kesimpulan
    
    Ini teksnya:
    {teks}
    """
    jawaban = model_ai.generate_content(instruksi)
    return jawaban.text

daftar_file_pdf = st.file_uploader(
    "Pilih satu atau banyak File PDF",
    type=["pdf"],
    accept_multiple_files=True
)

if daftar_file_pdf:
    st.info(f"✅ {len(daftar_file_pdf)} file siap dirangkum")

    if st.button("🚀 Rangkum Semua PDF"):

        semua_hasil = {}

        for file_pdf in daftar_file_pdf:
            with st.spinner(f"Merangkum: {file_pdf.name}..."):
                try:
                    teks = baca_pdf(file_pdf)

                    if not teks.strip():
                        st.warning(f"⚠️ {file_pdf.name} tidak bisa dibaca (mungkin PDF scan/gambar)")
                        continue

                    hasil = rangkum_dengan_ai(teks, file_pdf.name)
                    semua_hasil[file_pdf.name] = hasil

                    # Tampilkan hasil per file
                    with st.expander(f"📄 Hasil: {file_pdf.name}", expanded=True):
                        st.write(hasil)
                        st.download_button(
                            label=f"⬇️ Download rangkuman {file_pdf.name}",
                            data=hasil,
                            file_name=f"rangkuman_{file_pdf.name}.txt",
                            mime="text/plain",
                            key=file_pdf.name  # key unik supaya tombol tidak bentrok
                        )

                except Exception as e:
                    st.error(f"❌ Gagal merangkum {file_pdf.name}: {e}")

        if len(semua_hasil) > 1:
            st.success(f"🎉 Selesai! {len(semua_hasil)} file berhasil dirangkum.")

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for nama, isi in semua_hasil.items():
                    zip_file.writestr(f"rangkuman_{nama}.txt", isi)
            zip_buffer.seek(0)

            st.download_button(
                label="⬇️ Download SEMUA Rangkuman (.zip)",
                data=zip_buffer,
                file_name="semua_rangkuman.zip",
                mime="application/zip"
            )
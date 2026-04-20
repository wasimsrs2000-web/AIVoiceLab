import streamlit as st
import os
import struct
import google.generativeai as genai
from google.genai import types

# ✅ WAV convert function (IMPORTANT)
def convert_to_wav(audio_data):
    sample_rate = 24000
    num_channels = 1
    bits_per_sample = 16

    data_size = len(audio_data)
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,
        1,
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        data_size
    )

    return header + audio_data


st.title("🎤 AI Voice Generator")

API_KEY = os.getenv("GEMINI_API_KEY")

text_input = st.text_area("Enter your text:")

if st.button("Generate Voice"):
    if not API_KEY:
        st.error("API Key not found ❌")
    elif not text_input.strip():
        st.warning("Please enter text ⚠️")
    else:
        client = genai.Client(api_key=API_KEY)

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=text_input)],
            ),
        ]

        config = types.GenerateContentConfig(
            response_modalities=["audio"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Zephyr"
                    )
                )
            ),
        )

        audio_bytes = b""

        for chunk in client.models.generate_content_stream(
            model="gemini-3.1-flash-tts-preview",
            contents=contents,
            config=config,
        ):
            if chunk.parts and chunk.parts[0].inline_data:
                audio_bytes += chunk.parts[0].inline_data.data

        if audio_bytes:
            wav_audio = convert_to_wav(audio_bytes)  # ✅ अब error नहीं आएगा
            st.success("Voice Generated ✅")
            st.audio(wav_audio, format="audio/wav")
        else:
            st.error("Voice generate nahi hui ❌")

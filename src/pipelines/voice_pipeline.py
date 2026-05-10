import streamlit as st
import librosa
import io
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav

@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()

def create_voice_embeddings(audio_bytes):
    try:

        encoder = load_voice_encoder()

        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        wav = preprocess_wav(audio)
        embeddings = encoder.embed_utterance(wav)
        return embeddings.tolist()
    
    except Exception as e:
        st.error('voice recog error')
        return None
    
def identify_student(new_embedding, candidate_dict, threshold=0.65):
    if new_embedding is None or not candidate_dict:
        return None, 0.0
    
    best_sid = None
    best_score = -1.0

    for sid, stored_embedding in candidate_dict.items():
        if stored_embedding:
            similarity = np.dot(new_embedding, stored_embedding)

            if similarity >= best_score:
                best_score = similarity
                best_sid = sid

    if best_score >= threshold:
        return best_sid, best_score
    
    return None, best_score


def process_bulk_audio(audio_bytes, candidate_dict, threshold = 0.65):
    try:

        encoder = load_voice_encoder()

        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        segments = librosa.effects.split(audio, top_db=20)

        identified_results = {}

        for start, end in segments:
            if (start - end) < sr * 0.5:
                continue
            segment_audio = audio[start:end]

            wav = preprocess_wav(segment_audio)
            embedding = encoder.embed_utterance(wav)

            sid, score = identify_student(embedding, candidate_dict, threshold)

            if sid:
                if sid not in identified_results or score > identified_results[sid]:
                    identified_results[sid] = score

        return identified_results
    except Exception as e:
        st.error('bulk process error')
        return {}

    


    

import streamlit as st
import pandas as pd
import numpy as np
from datasketch import MinHash, MinHashLSH
from rapidfuzz import fuzz
import io
import time
from concurrent.futures import ThreadPoolExecutor

# Configuration
MAX_ROWS_TO_PROCESS = 300000  # Increased limit
SIMILARITY_THRESHOLD = 0.8
CHUNK_SIZE = 20000  # Larger chunks for better performance
MALE_FRAUD_FLAG = True  # Configurable gender-based flagging

# Initialize session state for progress tracking
if 'progress' not in st.session_state:
    st.session_state.progress = 0

def update_progress(step):
    """Update progress bar"""
    st.session_state.progress = step
    # st.rerun()

def preprocess_data(df):
    """Clean and optimize data for analysis"""
    # Basic cleaning
    df = df.dropna(subset=['fullName']).copy()
    
    # Handle gender if column exists
    if 'gender' in df.columns:
        df['gender'] = df['gender'].str.lower().str.strip().fillna('unknown')
        df['gender'] = np.where(df['gender'].isin(['male', 'female', 'other']), 
                              df['gender'], 'unknown')
    
    # Standardize text fields
    df['accountNumber'] = df['accountNumber'].astype(str).str.strip()
    df['name_lower'] = df['fullName'].str.lower().str.strip()
    
    # Deduplicate identical records
    df = df.drop_duplicates(subset=['name_lower', 'accountNumber'])
    
    return df

def create_minhash(text, num_perm=64):
    """Create MinHash signature for a text (optimized with fewer permutations)"""
    mh = MinHash(num_perm=num_perm)
    # Use first 3 words for faster hashing (adjust based on your name patterns)
    for word in text.split()[:3]:
        mh.update(word.encode('utf8'))
    return mh

def build_lsh_index(df, threshold):
    """Build LSH index for fast approximate matching"""
    lsh = MinHashLSH(threshold=threshold, num_perm=64)
    minhashes = {}
    
    # Build index in chunks
    for i in range(0, len(df), CHUNK_SIZE):
        chunk = df.iloc[i:i+CHUNK_SIZE]
        for idx, row in chunk.iterrows():
            mh = create_minhash(row['name_lower'])
            minhashes[idx] = mh
            lsh.insert(idx, mh)
        update_progress(i/len(df)*50)  # 50% of progress for indexing
    
    return lsh, minhashes

def verify_matches(df, lsh, minhashes, threshold):
    """Verify matches with exact similarity calculation"""
    results = []
    total = len(df)
    
    for i, (idx, row) in enumerate(df.iterrows()):
        # Get approximate matches from LSH
        matches = lsh.query(minhashes[idx])
        
        # Detailed verification only for potential matches
        for match_idx in matches:
            if match_idx != idx:  # Skip self-matches
                match_row = df.loc[match_idx]
                
                # Calculate exact similarity
                similarity = fuzz.ratio(row['name_lower'], match_row['name_lower'])/100
                same_account = row['accountNumber'] == match_row['accountNumber']
                
                # Apply threshold
                if similarity >= threshold or same_account:
                    risk_score = min(100, int(
                        (similarity * 40) + 
                        (60 if same_account else 0) + 
                        (80 if MALE_FRAUD_FLAG and row.get('gender') == 'male' else 0))
                    )
                    
                    results.append({
                        'original_id': idx,
                        'original_name': row['fullName'],
                        'original_account': row['accountNumber'],
                        'original_gender': row.get('gender', 'unknown'),
                        'match_name': match_row['fullName'],
                        'match_account': match_row['accountNumber'],
                        'match_gender': match_row.get('gender', 'unknown'),
                        'similarity': similarity,
                        'same_account': same_account,
                        'risk_score': risk_score,
                        'fraud_reasons': ', '.join(filter(None, [
                            f"Name similarity ({similarity:.0%})" if similarity >= threshold else None,
                            "Same account" if same_account else None,
                            "Male applicant" if MALE_FRAUD_FLAG and row.get('gender') == 'male' else None
                        ]))
                    })
        
        # Update progress
        if i % 1000 == 0:
            update_progress(50 + (i/total)*50)  # Second 50% of progress
    
    return pd.DataFrame(results)

def process_data(df, threshold):
    """End-to-end optimized processing pipeline"""
    # Step 1: Preprocessing
    update_progress(0)
    df = preprocess_data(df)
    
    # Step 2: Build LSH index
    lsh, minhashes = build_lsh_index(df, threshold)
    
    # Step 3: Verify matches
    results = verify_matches(df, lsh, minhashes, threshold)
    
    update_progress(100)
    return results

def main():
    st.set_page_config(
        page_title="Ultra-Fast Fraud Detection", 
        page_icon="⚡", 
        layout="wide"
    )
    
    # Custom CSS for performance (avoids rerendering)
    st.markdown("""
    <style>
        div.block-container { padding-top: 1rem; }
        #MainMenu, .stDeployButton { visibility: hidden; }
        .stProgress > div > div > div { background-color: #2563eb; }
        [data-testid="stStatusWidget"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    st.title("⚡ Ultra-Fast Loan Fraud Detection")
    st.caption("Optimized for large datasets (200K+ rows)")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Customer Data (CSV or Excel)",
        type=['csv', 'xlsx'],
        help="Requires 'fullName' and 'accountNumber' columns. 'gender' column optional."
    )

    if not uploaded_file:
        st.info("👆 Please upload a file to begin analysis")
        return

    # User controls
    with st.expander("⚙️ Settings", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            threshold = st.slider(
                "Name similarity threshold", 
                0.5, 1.0, SIMILARITY_THRESHOLD, 0.05,
                help="Higher values require closer name matches"
            )
        with col2:
            min_risk = st.slider(
                "Minimum risk score", 
                0, 100, 50,
                help="Filter out lower-risk matches"
            )
    
    # Process data when button clicked
    if st.button("🚀 Start Analysis", type="primary"):
        # Read file
        try:
            st.info("Reading file...")
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Validate columns
            if 'fullName' not in df.columns or 'accountNumber' not in df.columns:
                st.error("❌ File must contain 'fullName' and 'accountNumber' columns")
                return
                
            # Limit rows if needed
            if len(df) > MAX_ROWS_TO_PROCESS:
                st.warning(f"⚠️ Processing first {MAX_ROWS_TO_PROCESS:,} rows of {len(df):,}")
                df = df.iloc[:MAX_ROWS_TO_PROCESS]
            
            # Initialize progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process data
            start_time = time.time()
            results = process_data(df, threshold)
            processing_time = time.time() - start_time
            
            # Display results
            st.success(f"✅ Processed {len(df):,} records in {processing_time:.1f} seconds")
            progress_bar.empty()
            
            if results.empty:
                st.success("✅ No potential fraud matches found")
            else:
                # Summary stats
                st.warning(f"🚨 Found {len(results):,} potential fraud matches")
                
                # Show top high-risk matches
                high_risk = results[results['risk_score'] >= min_risk]
                if not high_risk.empty:
                    st.dataframe(
                        high_risk.sort_values('risk_score', ascending=False).head(50),
                        column_config={
                            "risk_score": st.column_config.ProgressColumn(
                                "Risk Score",
                                format="%d",
                                min_value=0,
                                max_value=100,
                            )
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                
                # Export functionality
                csv = results.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Full Results",
                    data=csv,
                    file_name="fraud_matches.csv",
                    mime="text/csv"
                )
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return

    # Progress updates
    if st.session_state.progress > 0:
        st.progress(st.session_state.progress)
        st.caption(f"Processing: {st.session_state.progress:.0f}% complete")

if __name__ == "__main__":
    main()
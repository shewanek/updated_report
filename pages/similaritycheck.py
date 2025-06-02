import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
from collections import defaultdict
import io

def similarity_ratio(a, b):
    """Calculate similarity between two strings (0-1)"""
    if pd.isna(a) or pd.isna(b) or not a or not b:
        return 0.0
    return SequenceMatcher(None, str(a).lower().strip(), str(b).lower().strip()).ratio()

def find_similar_names(df, threshold=0.8):
    """Find groups of similar names with account numbers"""
    groups = defaultdict(list)
    names = df['fullName'].tolist()
    account_numbers = df['accountNumber'].tolist()
    
    for i, (name1, acc1) in enumerate(zip(names, account_numbers)):
        group = {
            'name': name1,
            'accounts': [acc1],
            'similar_names': []
        }
        
        for j, (name2, acc2) in enumerate(zip(names[i+1:], account_numbers[i+1:]), start=i+1):
            # Check for both name similarity AND matching account numbers
            if similarity_ratio(name1, name2) >= threshold or acc1 == acc2:
                group['similar_names'].append({
                    'name': name2,
                    'account': acc2,
                    'similarity': similarity_ratio(name1, name2),
                    'same_account': acc1 == acc2
                })
                
        if group['similar_names']:
            groups[name1] = group
            
    return groups

def main():
    st.set_page_config(page_title="Loan Fraud Detection", page_icon="🔍", layout="wide")
    
    # Custom CSS
    st.markdown("""
    <style>
        div.block-container { padding-top: 1rem; }
        #MainMenu, .stDeployButton { visibility: hidden; }
        .stButton button {
            background-color: #000000;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 16px;
            cursor: pointer;
        }
        .stButton button:hover {
            background-color: #00bfff;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("🔍 Loan Application Fraud Detection")
    st.subheader("Upload customer data to detect similar names and matching account numbers")

    # File upload
    uploaded_file = st.file_uploader(
        "Upload Customer Data (CSV or Excel)",
        type=['csv', 'xlsx'],
        help="File should contain 'fullName' and 'accountNumber' columns"
    )

    if not uploaded_file:
        st.info("👆 Please upload a file to begin analysis")
        return

    # Read file
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Validate required columns
        if 'fullName' not in df.columns or 'accountNumber' not in df.columns:
            st.error("❌ File must contain both 'fullName' and 'accountNumber' columns")
            return
            
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return

    # Clean data
    df = df.dropna(subset=['fullName']).copy()
    df['accountNumber'] = df['accountNumber'].astype(str).str.strip()

    # User controls
    col1, col2 = st.columns(2)
    with col1:
        threshold = st.slider("Name similarity threshold", 0.5, 1.0, 0.8, 0.05,
                            help="Higher values require closer name matches")
    with col2:
        show_all = st.checkbox("Show all potential matches", False,
                             help="Include cases with just matching account numbers")

    # Process data
    similar_groups = find_similar_names(df, threshold)

    # Display results
    if not similar_groups:
        st.success("✅ No potential fraud matches found")
    else:
        st.warning(f"🚨 Found {len(similar_groups)} potential fraud cases")
        
        for group_name, group_data in similar_groups.items():
            with st.expander(f"Potential Fraud Group: {group_name}", expanded=False):
                # Create results table
                results = [{
                    'Name': group_name,
                    'Account': group_data['accounts'][0],
                    'Similarity': '100%',
                    'Same Account': 'Original'
                }]
                
                for match in group_data['similar_names']:
                    if show_all or match['similarity'] >= threshold:
                        results.append({
                            'Name': match['name'],
                            'Account': match['account'],
                            'Similarity': f"{match['similarity']*100:.1f}%",
                            'Same Account': '✅' if match['same_account'] else '❌'
                        })
                
                st.dataframe(pd.DataFrame(results), hide_index=True)

    # Export functionality
    if similar_groups:
        if st.button("📝 Export Results to CSV"):
            export_data = []
            for group_name, group_data in similar_groups.items():
                for match in group_data['similar_names']:
                    export_data.append({
                        'Original Name': group_name,
                        'Original Account': group_data['accounts'][0],
                        'Matched Name': match['name'],
                        'Matched Account': match['account'],
                        'Name Similarity': match['similarity'],
                        'Accounts Match': match['same_account']
                    })
            
            output = io.StringIO()
            pd.DataFrame(export_data).to_csv(output, index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=output.getvalue(),
                file_name="fraud_matches.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
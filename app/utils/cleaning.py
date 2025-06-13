from bs4 import BeautifulSoup
import pandas as pd

def clean_html_text(html):
    if not isinstance(html, str):
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return "\n".join([line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()])

def clean_dataframe(df):
    mask = (df["class"] == "traction.communication.MailMessage") | \
           (df["class"] == "traction.communication.FormClientData")
    df.loc[mask, "text"] = df.loc[mask, "text"].apply(clean_html_text)
    df["sender_type"] = df["user_id"].apply(lambda x: "agent" if pd.isna(x) else "client")
    return df

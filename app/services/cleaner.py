from bs4 import BeautifulSoup
import pandas as pd

def clean_html_text(html):
    if not isinstance(html, str):
        return ""
    soup = BeautifulSoup(html, "html.parser")
    raw_text = soup.get_text(separator="\n")
    clean_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    return "\n".join(clean_lines)

def clean_text_column(df):
    mask = df["class"].isin(["traction.communication.MailMessage", "traction.communication.FormClientData"])
    df.loc[mask, "text"] = df.loc[mask, "text"].apply(clean_html_text)
    return df

"""Simple file info for upload"""
import os
import base64

excel_file = r"c:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\MARKETING_TEAM\outputs\leads\Houston_Cyber_CTOs_Leads.xlsx"

with open(excel_file, 'rb') as f:
    content = f.read()
    b64 = base64.b64encode(content).decode('utf-8')

print("EXCEL FILE INFO:")
print(f"Name: Houston_Cyber_CTOs_Leads.xlsx")
print(f"Size: {len(content)} bytes")
print(f"Base64 length: {len(b64)} characters")
print(f"Target folder: 1G5AQYEcKv_kKUMfr8QgPVAlkcMjvhEB_")
print("\nBase64 content (first 100 chars):")
print(b64[:100])

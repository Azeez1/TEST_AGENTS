"""
Send AI Breakthrough Newsletter - November 2025
"""
import sys
import os

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from send_html_newsletter import send_html_newsletter

def main():
    # Newsletter details
    to_email = "sabaazeez12@gmail.com"
    cc_email = "aoseni@duxvitaecapital.com"
    subject = "This $5T milestone just changed AI forever"
    html_file = "outputs/newsletters/ai_breakthrough_november_2025.html"

    print("=" * 70)
    print("Sending AI Breakthrough Newsletter - November 2025")
    print("=" * 70)
    print()
    print(f"To: {to_email}")
    print(f"CC: {cc_email}")
    print(f"Subject: {subject}")
    print(f"HTML File: {html_file}")
    print()
    print("Sending...")
    print()

    try:
        message_id = send_html_newsletter(
            to_email=to_email,
            subject=subject,
            html_content=html_file,
            cc=cc_email
        )

        print()
        print("=" * 70)
        print("[SUCCESS] Newsletter sent successfully!")
        print("=" * 70)
        print()
        print(f"Message ID: {message_id}")
        print()
        print("Newsletter Details:")
        print("  - Title: The AI Infrastructure Wars Have Begun")
        print("  - Focus: November 2025 AI developments")
        print("  - Topics:")
        print("    • NVIDIA's $5 trillion valuation")
        print("    • OpenAI-NVIDIA 10 GW partnership")
        print("    • DeepSeek's efficiency revolution")
        print("    • AI agents moving from demo to deployment")
        print("  - Recipients confirmed: Both email addresses")
        print()

    except Exception as e:
        print()
        print("=" * 70)
        print("[ERROR] Newsletter sending failed")
        print("=" * 70)
        print()
        print(f"Error: {str(e)}")
        print()
        sys.exit(1)

if __name__ == "__main__":
    main()

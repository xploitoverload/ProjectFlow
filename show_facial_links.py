#!/usr/bin/env python3
"""
Generate and display the current facial ID setup links
Run this to get your current hidden token and all setup URLs
"""

from app import create_app

def display_facial_id_links():
    """Display all facial ID links with current hidden token"""
    app = create_app()
    token = app.config.get('HIDDEN_ADMIN_TOKEN')
    
    print("\n" + "="*80)
    print("🔐 FACIAL ID AUTHENTICATION - YOUR SETUP LINKS")
    print("="*80)
    
    print(f"\n📌 YOUR HIDDEN ADMIN TOKEN:")
    print(f"   {token}")
    print(f"\n   ⚠️  Keep this secret! It grants access to your admin panel.\n")
    
    base_url = f"http://localhost:5000/secure-mgmt-{token}"
    
    links = {
        "Setup Guide (Start Here!)": "/facial-setup-guide",
        "": None,
        "SETUP STEPS (Do in Order):": None,
        "1. Setup 2FA First": f"{base_url}/setup-2fa",
        "2. Enroll Your Face": f"{base_url}/setup-facial-id",
        "3. Verify Facial Works": f"{base_url}/verify-facial-id",
        "4. Test Facial Login": f"{base_url}/facial-login",
        "": None,
        "MANAGEMENT:": None,
        "Facial Settings": f"{base_url}/facial-id-settings",
        "2FA Verify": f"{base_url}/verify-2fa",
    }
    
    print("📱 QUICK LINKS:\n")
    for label, url in links.items():
        if url is None:
            if label:
                print(f"\n{label}")
            continue
        
        if url.startswith("http"):
            print(f"  • {label:<30} {url}")
        else:
            print(f"  • {label:<30} http://localhost:5000{url}")
    
    print("\n" + "="*80)
    print("✅ NEXT STEPS:")
    print("="*80)
    print("""
1. VISIT SETUP GUIDE:
   → http://localhost:5000/facial-setup-guide
   (This page shows all links and has copy buttons)

2. FOLLOW THE 4 STEPS:
   → Setup 2FA (scan QR code with authenticator app)
   → Enroll Face (capture 3-5 face images)
   → Verify Facial (confirm it works with selfie)
   → Test Facial Login (login using just your face + 2FA)

3. THAT'S IT!
   → You now have biometric admin authentication
   → No passwords needed
   → Maximum security
""")
    
    print("="*80)
    print("💾 QUICK REFERENCE:\n")
    
    print("Your Hidden Token (keep secret):")
    print(f"  {token}\n")
    
    print("Setup Guide URL (bookmark this):")
    print(f"  http://localhost:5000/facial-setup-guide\n")
    
    print("Direct Facial Setup URL:")
    print(f"  {base_url}/setup-facial-id\n")
    
    print("Direct Facial Login URL:")
    print(f"  {base_url}/facial-login\n")
    
    print("="*80)
    print("🎯 TIPS:\n")
    print("  • Good lighting helps face detection")
    print("  • Position face in center of frame")
    print("  • Remove sunglasses and heavy makeup")
    print("  • Authenticator app alternatives: Google Authenticator, Authy, Microsoft Authenticator")
    print("  • Save your 2FA backup codes somewhere safe")
    print("  • You can still login with password + 2FA if facial fails")
    print("="*80 + "\n")

if __name__ == '__main__':
    display_facial_id_links()

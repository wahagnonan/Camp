import os
import django
import sys
from datetime import date
from django.conf import settings
from django.urls import resolve, reverse

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'upgc.settings')
django.setup()

def verify_urls():
    print("Verifying URL configuration...")
    
    # 1. Check 'aujourdhui/'
    try:
        url = reverse('emploi-jour')
        print(f"URL for 'emploi-jour': {url}")
        match = resolve(url)
        print(f"Resolved to view: {match.func.view_class.__name__}")
        if url == '/aujourdhui/':
            print("SUCCESS: 'aujourdhui/' URL is correct.")
        else:
            print(f"WARNING: Unexpected URL: {url}")
    except Exception as e:
        print(f"ERROR resolving 'emploi-jour': {e}")

    # 2. Check '<int:jour>/<int:mois>/<int:annee>/'
    try:
        # Test with 16/02/2026
        url = reverse('emploi-date', kwargs={'jour': 16, 'mois': 2, 'annee': 2026})
        print(f"URL for 'emploi-date' (16/2/2026): {url}")
        match = resolve(url)
        print(f"Resolved to view: {match.func.view_class.__name__}")
        print(f"Captured kwargs: {match.kwargs}")
        
        # New expected format: /16/2/2026/
        if url == '/16/2/2026/' or url == '/16/02/2026/':
             print("SUCCESS: Date URL format is correct.")
        else:
             print(f"WARNING: Unexpected URL format: {url}")

    except Exception as e:
        print(f"ERROR resolving 'emploi-date': {e}")

if __name__ == "__main__":
    verify_urls()

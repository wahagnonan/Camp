import os
import django
import sys
from datetime import date

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'upgc.settings')
django.setup()

from core.models import Cours
from core.scraping import ExtracteurUPGC

def verify():
    print("Starting verification of scraper...")
    
    # 1. Clear existing data to be sure
    # Cours.objects.all().delete()
    initial_count = Cours.objects.count()
    print(f"Initial course count: {initial_count}")
    
    # 2. Run scraper logic
    try:
        extracteur = ExtracteurUPGC()
        # Fetch for today or a specific date if today is weekend/empty?
        # Let's try today first
        today = date.today()
        print(f"Fetching for date: {today}")
        
        data = extracteur.recuperer_emploi_du_temps(zone=2, date_cible=today)
        print(f"Scraper returned {len(data)} items.")
        
        # 3. Save to DB (simulating view logic)
        saved_count = 0
        for item in data:
            Cours.objects.update_or_create(
                jour=item['jour'],
                horaire=item['horaire'],
                ressource=item['ressource'],
                defaults={
                    'type_cours': item['type_cours'],
                    'enseignant': item['enseignant'],
                    'intitule': item['intitule'],
                    'niveau': item['niveau'],
                    'salle': item['salle']
                }
            )
            saved_count += 1
            
        print(f"Saved {saved_count} items to database.")
        
        # 4. Verify DB count
        final_count = Cours.objects.count()
        print(f"Final course count: {final_count}")
        
        if len(data) > 0:
            print("SUCCESS: Scraper found data.")
            # Print sample
            print("Sample data:", data[0])
        else:
            print("WARNING: Scraper returned no data. This might be normal if there are no classes today/this week.")
            
    except Exception as e:
        print(f"ERROR: Verification failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()

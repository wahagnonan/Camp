import os
import django
import sys
from datetime import date

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'upgc.settings')
django.setup()

from core.models import Cours
from core.serializers import CoursSerializer

def verify_serialization():
    print("Verifying serialization fix...")
    
    # 1. Fetch existing objects verify they can be serialized
    count = Cours.objects.count()
    print(f"Checking serialization for {count} objects in DB...")
    
    objects = Cours.objects.all()
    try:
        serializer = CoursSerializer(objects, many=True)
        data = serializer.data
        # Accessing .data property triggers serialization logic
        print(f"Successfully serialized {len(data)} items.")
        
        # Check for empty fields in data
        empty_niveau = sum(1 for item in data if not item.get('niveau'))
        print(f"Items with empty 'niveau': {empty_niveau}")
        
        if len(data) > 0:
            print("Sample item:", data[0])
            
        print("SUCCESS: Serialization works.")
        
    except Exception as e:
        print(f"ERROR: Serialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_serialization()

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'kasbi.settings'
try:
    import django
    django.setup()
    print("Django setup OK")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

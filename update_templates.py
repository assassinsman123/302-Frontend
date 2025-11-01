"""
Template Updater - Add AJAX support from app.py context
Run: python update_templates.py
"""
import os

TEMPLATES_DIR = "Templates"
TEMPLATES = [
    "Dashboard.html", "Products.html", "Messages.html", "Upload.html",
    "Wishlist.html", "review.html", "ItemMessage.html", "SellerMessage.html",
    "YourListings.html", "CustomerSupport.html", "Admin.html", "Reminder.html",
    "ForgotPassword.html", "ResetPassword.html"
]

HEAD_ADD = '  {{ ajax_style|safe }}\n  {{ jquery_script|safe }}'
BODY_ADD = '  {{ ajax_script|safe }}'

def update_template(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'ajax_script' in content:
            print(f"  ⏭️  {os.path.basename(filepath)} already updated")
            return False
        
        if '</head>' in content:
            content = content.replace('</head>', HEAD_ADD + '\n</head>')
        else:
            print(f"  ⚠️  No </head> in {os.path.basename(filepath)}")
            return False
        
        if '</body>' in content:
            content = content.replace('</body>', BODY_ADD + '\n</body>')
        else:
            print(f"  ⚠️  No </body> in {os.path.basename(filepath)}")
            return False
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ {os.path.basename(filepath)}")
        return True
    except Exception as e:
        print(f"  ❌ {os.path.basename(filepath)}: {e}")
        return False

print("="*50)
print("Template Updater - Adding AJAX from app.py")
print("="*50)
updated = 0
for template in TEMPLATES:
    filepath = os.path.join(TEMPLATES_DIR, template)
    if update_template(filepath):
        updated += 1

print("="*50)
print(f"✅ Updated: {updated} templates")
print("="*50)
print("\nAll AJAX code is in app.py - No external files needed!")
print("Restart Flask and test your app.")


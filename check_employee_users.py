"""
Diagnostic script to check and fix employee user accounts in Horilla.
This script will:
1. List all employees
2. Check if they have associated user accounts
3. Create user accounts for employees without them
4. Display login credentials

Run this script with: python manage.py shell < check_employee_users.py
Or: python manage.py shell -c "exec(open('check_employee_users.py').read())"
"""

from employee.models import Employee
from django.contrib.auth.models import User, Permission

def check_and_create_users():
    print("\n" + "="*70)
    print("HORILLA EMPLOYEE USER ACCOUNT DIAGNOSTIC")
    print("="*70 + "\n")
    
    employees = Employee.objects.all()
    
    if not employees.exists():
        print("❌ No employees found in the system.")
        return
    
    print(f"📊 Found {employees.count()} employee(s) in the system\n")
    
    employees_without_users = []
    employees_with_users = []
    
    for emp in employees:
        print("-" * 70)
        print(f"Employee: {emp.employee_first_name} {emp.employee_last_name or ''}")
        print(f"Email: {emp.email}")
        print(f"Phone: {emp.phone}")
        print(f"Badge ID: {emp.badge_id or 'N/A'}")
        print(f"Active: {'Yes' if emp.is_active else 'No'}")
        
        if emp.employee_user_id:
            print(f"✅ User Account: EXISTS (Username: {emp.employee_user_id.username})")
            print(f"   User Active: {'Yes' if emp.employee_user_id.is_active else 'No'}")
            print(f"   User ID: {emp.employee_user_id.id}")
            employees_with_users.append(emp)
        else:
            print("❌ User Account: MISSING")
            employees_without_users.append(emp)
        
        print()
    
    print("="*70)
    print(f"\n📈 SUMMARY:")
    print(f"   Employees with user accounts: {len(employees_with_users)}")
    print(f"   Employees WITHOUT user accounts: {len(employees_without_users)}")
    
    if employees_without_users:
        print("\n" + "="*70)
        print("🔧 CREATING MISSING USER ACCOUNTS...")
        print("="*70 + "\n")
        
        for emp in employees_without_users:
            try:
                username = emp.email
                password = emp.phone
                
                # Check if user with this username already exists
                existing_user = User.objects.filter(username=username).first()
                
                if existing_user:
                    print(f"⚠️  User '{username}' already exists. Linking to employee...")
                    emp.employee_user_id = existing_user
                    emp.save()
                    print(f"✅ Linked existing user to {emp.employee_first_name}")
                else:
                    print(f"Creating user for: {emp.employee_first_name} {emp.employee_last_name or ''}")
                    
                    user = User.objects.create_user(
                        username=username,
                        email=username,
                        password=password,
                    )
                    
                    emp.employee_user_id = user
                    
                    # Add default permissions
                    try:
                        change_ownprofile = Permission.objects.get(codename="change_ownprofile")
                        view_ownprofile = Permission.objects.get(codename="view_ownprofile")
                        user.user_permissions.add(view_ownprofile, change_ownprofile)
                    except Permission.DoesNotExist:
                        print("   ⚠️  Default permissions not found, skipping...")
                    
                    emp.save()
                    
                    print(f"✅ User created successfully!")
                    print(f"   Username: {username}")
                    print(f"   Password: {password}")
                    print()
                    
            except Exception as e:
                print(f"❌ Error creating user for {emp.email}: {str(e)}")
                print()
    
    print("\n" + "="*70)
    print("📋 LOGIN CREDENTIALS FOR ALL EMPLOYEES:")
    print("="*70 + "\n")
    
    employees = Employee.objects.all()
    for emp in employees:
        if emp.employee_user_id:
            print(f"Employee: {emp.employee_first_name} {emp.employee_last_name or ''}")
            print(f"   Username: {emp.email}")
            print(f"   Password: {emp.phone}")
            print(f"   User Active: {'Yes' if emp.employee_user_id.is_active else 'No'}")
            print()
    
    print("="*70)
    print("\n💡 NOTES:")
    print("   - Employees login with their EMAIL as username")
    print("   - The password is their PHONE NUMBER (exactly as stored)")
    print("   - Make sure both employee and user accounts are 'active'")
    print("   - If login still fails, check for typos in email/phone")
    print("="*70 + "\n")

# Run the diagnostic
check_and_create_users()

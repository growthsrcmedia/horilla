"""
Django management command to check and fix employee user accounts.
Run with: python manage.py check_employee_credentials
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from employee.models import Employee


class Command(BaseCommand):
    help = 'Check employee user accounts and display/create login credentials'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("HORILLA EMPLOYEE USER ACCOUNT DIAGNOSTIC"))
        self.stdout.write("="*70 + "\n")
        
        employees = Employee.objects.all()
        
        if not employees.exists():
            self.stdout.write(self.style.ERROR("❌ No employees found in the system."))
            return
        
        self.stdout.write(f"📊 Found {employees.count()} employee(s) in the system\n")
        
        employees_without_users = []
        employees_with_users = []
        
        for emp in employees:
            self.stdout.write("-" * 70)
            self.stdout.write(f"Employee: {emp.employee_first_name} {emp.employee_last_name or ''}")
            self.stdout.write(f"Email: {emp.email}")
            self.stdout.write(f"Phone: {emp.phone}")
            self.stdout.write(f"Badge ID: {emp.badge_id or 'N/A'}")
            self.stdout.write(f"Employee Active: {'Yes' if emp.is_active else 'No'}")
            
            if emp.employee_user_id:
                self.stdout.write(self.style.SUCCESS(
                    f"✅ User Account: EXISTS (Username: {emp.employee_user_id.username})"
                ))
                self.stdout.write(f"   User Active: {'Yes' if emp.employee_user_id.is_active else 'No'}")
                self.stdout.write(f"   User ID: {emp.employee_user_id.id}")
                
                # Check if user can authenticate
                user = emp.employee_user_id
                self.stdout.write(f"   Has usable password: {'Yes' if user.has_usable_password() else 'No'}")
                
                employees_with_users.append(emp)
            else:
                self.stdout.write(self.style.ERROR("❌ User Account: MISSING"))
                employees_without_users.append(emp)
            
            self.stdout.write("")
        
        self.stdout.write("="*70)
        self.stdout.write(f"\n📈 SUMMARY:")
        self.stdout.write(f"   Employees with user accounts: {len(employees_with_users)}")
        self.stdout.write(f"   Employees WITHOUT user accounts: {len(employees_without_users)}")
        
        if employees_without_users:
            self.stdout.write("\n" + "="*70)
            self.stdout.write(self.style.WARNING("🔧 CREATING MISSING USER ACCOUNTS..."))
            self.stdout.write("="*70 + "\n")
            
            for emp in employees_without_users:
                try:
                    username = emp.email
                    password = emp.phone
                    
                    # Check if user with this username already exists
                    existing_user = User.objects.filter(username=username).first()
                    
                    if existing_user:
                        self.stdout.write(self.style.WARNING(
                            f"⚠️  User '{username}' already exists. Linking to employee..."
                        ))
                        emp.employee_user_id = existing_user
                        Employee.objects.filter(pk=emp.pk).update(employee_user_id=existing_user)
                        self.stdout.write(self.style.SUCCESS(
                            f"✅ Linked existing user to {emp.employee_first_name}"
                        ))
                    else:
                        self.stdout.write(
                            f"Creating user for: {emp.employee_first_name} {emp.employee_last_name or ''}"
                        )
                        
                        user = User.objects.create_user(
                            username=username,
                            email=username,
                            password=password,
                        )
                        
                        # Add default permissions
                        try:
                            change_ownprofile = Permission.objects.get(codename="change_ownprofile")
                            view_ownprofile = Permission.objects.get(codename="view_ownprofile")
                            user.user_permissions.add(view_ownprofile, change_ownprofile)
                        except Permission.DoesNotExist:
                            self.stdout.write(self.style.WARNING(
                                "   ⚠️  Default permissions not found, skipping..."
                            ))
                        
                        Employee.objects.filter(pk=emp.pk).update(employee_user_id=user)
                        
                        self.stdout.write(self.style.SUCCESS("✅ User created successfully!"))
                        self.stdout.write(f"   Username: {username}")
                        self.stdout.write(f"   Password: {password}")
                        self.stdout.write("")
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"❌ Error creating user for {emp.email}: {str(e)}"
                    ))
                    self.stdout.write("")
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("📋 LOGIN CREDENTIALS FOR ALL EMPLOYEES:"))
        self.stdout.write("="*70 + "\n")
        
        employees = Employee.objects.select_related('employee_user_id').all()
        for emp in employees:
            if emp.employee_user_id:
                self.stdout.write(self.style.HTTP_INFO(
                    f"Employee: {emp.employee_first_name} {emp.employee_last_name or ''}"
                ))
                self.stdout.write(f"   👤 Username: {emp.email}")
                self.stdout.write(f"   🔑 Password: {emp.phone}")
                self.stdout.write(f"   ✓  Employee Active: {'Yes' if emp.is_active else 'NO - INACTIVE!'}")
                self.stdout.write(f"   ✓  User Active: {'Yes' if emp.employee_user_id.is_active else 'NO - INACTIVE!'}")
                self.stdout.write("")
        
        self.stdout.write("="*70)
        self.stdout.write("\n💡 IMPORTANT NOTES:")
        self.stdout.write("   - Login username: Employee's EMAIL address")
        self.stdout.write("   - Login password: Employee's PHONE NUMBER (exactly as shown above)")
        self.stdout.write("   - Both employee AND user must be 'Active' for login to work")
        self.stdout.write("   - Check for spaces or formatting in phone numbers")
        self.stdout.write("   - Username and password are CASE SENSITIVE")
        self.stdout.write("="*70 + "\n")

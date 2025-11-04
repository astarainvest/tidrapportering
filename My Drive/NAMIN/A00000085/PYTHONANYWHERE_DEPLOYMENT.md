# PythonAnywhere Deployment Instructions

## Files to Upload
1. Upload all files to your PythonAnywhere account:
   - app.py
   - wsgi.py
   - requirements.txt
   - templates/ (entire folder)
   - static/ (entire folder)
   - instance/ (entire folder, if exists)

## Deployment Steps

### 1. Upload Files
- Go to your PythonAnywhere Dashboard
- Click on "Files" tab
- Navigate to /home/yourusername/mysite/ (replace 'yourusername' with your actual username)
- Upload all the files and folders listed above

### 2. Install Dependencies
- Go to "Consoles" tab
- Open a Bash console
- Navigate to your project directory:
  ```bash
  cd /home/yourusername/mysite
  ```
- Install dependencies:
  ```bash
  pip3.11 install --user -r requirements.txt
  ```

### 3. Configure WSGI File
- Edit wsgi.py file and replace 'yourusername' with your actual PythonAnywhere username
- The path should be: /home/yourusername/mysite

### 4. Set up Web App
- Go to "Web" tab in your PythonAnywhere dashboard
- Click "Add a new web app"
- Choose "Manual configuration" 
- Select Python 3.11
- Set the source code path to: /home/yourusername/mysite
- Set the WSGI configuration file to: /home/yourusername/mysite/wsgi.py

### 5. Initialize Database
- In the Bash console, run:
  ```bash
  cd /home/yourusername/mysite
  python3.11 -c "from app import app, db; app.app_context().push(); db.create_all()"
  ```

### 6. Create Admin User (Optional)
- Run in Bash console:
  ```bash
  python3.11 -c "from app import app, db, User; from werkzeug.security import generate_password_hash; app.app_context().push(); admin = User(name='Admin', email='admin@example.com', password_hash=generate_password_hash('admin123'), is_admin=True); db.session.add(admin); db.session.commit(); print('Admin user created')"
  ```

### 7. Reload Web App
- Go back to "Web" tab
- Click "Reload" button
- Your app will be available at: https://yourusername.pythonanywhere.com

## Important Notes
- Replace 'yourusername' with your actual PythonAnywhere username in all paths
- Free accounts have limitations on external internet access
- The database will be created automatically on first run
- Check the error log if something goes wrong (available in Web tab)

## Default Login
After creating admin user:
- Email: admin@example.com  
- Password: admin123

Change these credentials immediately after first login!
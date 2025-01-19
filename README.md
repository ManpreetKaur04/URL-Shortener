# URL Shortener with Expiry and Analytics

## **Overview**
This project implements a URL Shortener system using Python and Flask. The system provides core URL shortening functionality, link expiration, and analytics tracking. The application uses SQLite for data storage and is designed to be modular and extensible.

---

## **Features**

1. **Core Functionality:**
   - Create unique shortened URLs for any valid long URL.
   - Base URL: `http://127.0.0.1:5000/<short_url>`.

2. **Expiry:**
   - Allow users to set an expiration time for shortened URLs (default: 24 hours).
   - Expired URLs no longer redirect to the original URL.

3. **Analytics:**
   - Track the number of times each shortened URL is accessed.
   - Log access timestamp and IP address.

4. **Storage:**
   - Original URL, shortened URL, creation timestamp, expiration timestamp, password (if applicable), and name.
   - Analytics data: shortened URL, access timestamp, and IP address.

5. **Password Protection:**
   - Optionally password-protect shortened URLs.

6. **CLI or API:**
   - REST API endpoints:
     - `POST /shorten`: Create a shortened URL.
     - `GET /<short_url>`: Redirect to the original URL (if not expired).
     - `GET /analytics/<short_url>`: Retrieve analytics for a specific shortened URL.

---

## **Setup Instructions**

### **1. Prerequisites**
- Python 3.7+
- Flask
- SQLite

### **2. Installation**
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python app.py
   ```
   This will create the SQLite database (`url_shortener.db`) with the necessary tables.

### **3. Running the Application**
1. Start the Flask development server:
   ```bash
   flask run
   ```
2. Access the application at `http://127.0.0.1:5000/`.

---

## **Usage Instructions**

### **1. Shorten a URL**
- Navigate to the main dashboard (`/`).
- Enter the long URL, optional expiration time (in hours), and optional password.
- Click "Shorten" to generate a shortened URL.

### **2. Redirect to Original URL**
- Use the generated short URL (`http://127.0.0.1:5000/<short_url>`).
- If the link is expired or password-protected, appropriate messages will be displayed.

### **3. View Analytics**
- Navigate to `/analytics/<short_url>` to view:
  - Number of accesses.
  - Access timestamps and IP addresses.

### **4. Password-Protected URLs**
- If a password is set, the system will prompt for password validation before redirecting to the original URL.

---

## **API Endpoints**

### **POST /shorten**
- **Description:** Create a shortened URL.
- **Request Body:**
  ```json
  {
    "url": "<original_url>",
    "expiry_hours": 24,  
    "password": "<optional_password>",
    "name": "<optional_name>"
  }
  ```
- **Response:**
  ```json
  {
    "short_url": "http://127.0.0.1:5000/<short_url>"
  }
  ```

### **GET /<short_url>**
- **Description:** Redirect to the original URL (if valid).
- **Response:**
  - 302 Redirect to original URL.
  - 404 Error if the URL is not found.
  - 410 Error if the URL is expired.

### **GET /analytics/<short_url>**
- **Description:** Retrieve analytics data for the specified short URL.
- **Response:**
  ```json
  {
    "analytics": [
      {
        "timestamp": "2025-01-01T12:00:00",
        "ip_address": "192.168.1.1"
      },
      ...
    ]
  }
  ```

---

## **Database Structure**

### **1. `urls` Table**
| Column         | Type         | Description                         |
|----------------|--------------|-------------------------------------|
| `id`           | INTEGER      | Primary key.                        |
| `original_url` | TEXT         | Original long URL.                  |
| `short_url`    | TEXT         | Unique shortened URL identifier.    |
| `created_at`   | DATETIME     | Timestamp when the URL was created. |
| `expires_at`   | DATETIME     | Expiration timestamp.               |
| `password`     | TEXT (NULL)  | Optional password for protection.   |
| `name`         | TEXT         | Optional name for the URL.          |

### **2. `analytics` Table**
| Column         | Type         | Description                         |
|----------------|--------------|-------------------------------------|
| `id`           | INTEGER      | Primary key.                        |
| `short_url`    | TEXT         | Associated shortened URL.           |
| `access_time`  | DATETIME     | Timestamp of the access.            |
| `ip_address`   | TEXT         | IP address of the client.           |

---

## **Modular Design**
The project structure is modular, enabling easy feature extensions. Key modules:
- **Database Operations:** Functions for interacting with SQLite.
- **URL Operations:** Logic for generating and managing short URLs.
- **Analytics Operations:** Functions for logging and retrieving analytics data.

---

## **Troubleshooting**
- **Error:** "URL not found" or "URL expired."
  - Check if the short URL exists and is not expired.
- **Error:** "Password required."
  - Verify the password matches the one set during creation.
- **Debugging:**
  - Use Flask's debug mode to identify issues:
    ```bash
    flask run --debug
    ```


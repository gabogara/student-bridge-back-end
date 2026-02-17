# Student Bridge

![Game Gems Library](https://i.postimg.cc/CKQDdM5X/Screenshot-2026-02-15-at-10-32-34-AM.png)

**StudentBridge** is a full-stack community resource platform that allows users to discover, create, and verify essential resources such as food, housing, health, and education services. The platform includes geolocation mapping, and verification workflows to ensure data reliability.

---

## Links

- **Live App:** ([Netlify](https://student-bridge-dep.netlify.app/))
- **Frontend GitHub Repository:** ([Github](https://github.com/gabogara/student-bridge-front-end.git))
- **Planning:** ([Trello](https://trello.com/b/sXX6cen2/project-4-studentbridge))

---
## Tech Stack

### Frontend
- React
- React Router
- Mapbox GL
- CSS / Flexbox

### Backend
- Flask
- PostgreSQL
- JWT Authentication
- REST API
- Psycopg2

## Features

- **User Authentication**: Registration and login with JWT authentication
- **Resource Management**: Full CRUD functionality for resources
- **Verification System**: Nested verification system for resource validation
- **Category Filtering**: Filter resources by type (food, housing, health, education)
- **Interactive Mapping**: Mapbox integration with geocoded resource locations
- **Secure Access**: Protected routes and conditional UI rendering
- **Data Integrity**: Backend validation and relational integrity

## Data Modeling

The application uses a relational schema with the following entities:

- **Users**: Store user account information
- **Resources**: Community resources with location and category data
- **Verifications**: Validation records for resource accuracy
- **Saves**: User-saved resources for quick access

The `student_bridge.sql` file contains:
- Table definitions for Users, Resources, Verifications, and Saves
- ENUM type definitions
- Foreign key constraints

## Entity Relationship Diagram (ERD)
![ERD](https://i.postimg.cc/4dhtYRpK/proj4-(2).jpg)

---

## Backend Setup

The backend repository contains the Flask API and database configuration.

### Installation

1. **Clone the backend repository**
```bash
   git clone https://github.com/gabogara/student-bridge-back-end.git
   cd student-bridge-back-end
```

2. **Install Python dependencies**
   
   Using pipenv:
```bash
   pipenv install
   pipenv shell
```

3. **Set up the PostgreSQL database**

   1. Run the SQL script:

      ```bash
      psql -U your_user -d postgres -f student_bridge_db.sql
      ```

   2. Verify the tables were created:

      ```bash
      psql -d student_bridge_db -c "\dt"
      ```


4. **Configure environment variables**
   
   Create a `.env` file in the root directory:
```env
    JWT_SECRET=secret_string
    POSTGRES_USERNAME=your_user_name
    POSTGRES_PASSWORD=your_password
    POSTGRES_DATABASE="student_bridge_db"
    MAPBOX_ACCESS_TOKEN=your_mapbox_token
```

5. **Start the Flask server**
```bash
   python3 app.py
```

The API will be running at [http://localhost:5000](http://localhost:5000)

---

## API Routes Overview

### Authentication
- `POST /auth/sign-up` — Create a new user and return a JWT token
- `POST /auth/sign-in` — Sign in an existing user and return a JWT token

### Resources
- `GET /resources` — List all resources (includes verification data when available)
- `GET /resources/:resourceId` — Get a single resource by ID
- `POST /resources` — Create a new resource *(protected)*
- `PUT /resources/:resourceId` — Update a resource *(owner only)*
- `DELETE /resources/:resourceId` — Delete a resource *(owner only)*

### Verifications
- `POST /resources/:resourceId/verifications` — Create (or update) a verification for a resource
- `PUT /resources/:resourceId/verifications/:verificationId` — Update a verification *(owner only)*
- `DELETE /resources/:resourceId/verifications/:verificationId` — Delete a verification *(owner only)*

**Verification status values:**
- `Active`
- `Temporarily Closed`
- `No Longer Available`
- `Info Needs Update`


All protected routes require a valid JWT token.

---

## Frontend Repository
The frontend repository for this project can be found here:  
[Frontend](https://github.com/gabogara/student-bridge-front-end)

---
## Future Improvements

- Build an admin dashboard with analytics (most verified resources, user activity, category trends).
- Add pagination and performance optimizations for large datasets.
- Implement automated verification scoring based on community feedback.
- Enable image uploads for resources with secure cloud storage integration.
- Implement full **moderator role** support using the `is_moderator` flag in the `users` table to enable moderator-only actions (approve/reject verifications, hide/remove resources, and manage reported content).

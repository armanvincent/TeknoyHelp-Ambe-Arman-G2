# TeknoyHelp: Teknoys helping Teknoys

TeknoyHelp is a Django web application for CIT-U students. A student posts a campus errand with a reward, another student accepts it, and both track it from posting until the reward is confirmed.

## Tech stack
- Django (templates for the frontend)
- PostgreSQL on Supabase
- Bootstrap 5

## Features

### Standard features
- Account registration with validation and hashed passwords
- Login and logout
- Role-based dashboards (Member and Admin)
- User profile (view and edit)

### Core feature: Errand Requests
- Members post errands with a category, description, location, deadline and reward
- Browse, search, filter (category, reward range) and sort open errands
- Edit or delete your own open errands
- Accept an errand, withdraw, mark it completed
- The owner confirms the reward to close the errand
- My Requests and My Tasks pages show history with status filters
- Admin can view and delete any errand and sees system statistics

### Errand flow
Open -> In progress -> Awaiting confirmation -> Reward confirmed

## Roles
| Role | Access |
|---|---|
| Member | Post, browse, accept and track errands |
| Admin | Dashboard statistics, manage and delete errands |

## Setup
1. Clone the repository:
   `git clone <repo-url>` then `cd <repo-folder>`
2. Create and activate a virtual environment (Windows CMD):
   `python -m venv venv` then `venv\Scripts\activate`
3. Install packages: `pip install -r requirements.txt`
4. Create a `.env` file in the main folder (see `.env.example`) with your Supabase database values.
5. Create the tables: `python manage.py migrate`
6. Create an admin: `python manage.py createsuperuser`
7. Run the server: `python manage.py runserver`
8. Open http://127.0.0.1:8000

## Branches
- `main`: stable code
- `develop`: integration branch
- `feature/errand-posting`, `feature/errand-workflow`, `feature/documentation`

## Author
Ambe, Arman Vincent - G2
### Conference Management

Conference Management System

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app conference_management
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/conference_management
pre-commit install
```

# Conference Management System

A fully functional Conference Management System built on the **Frappe Framework**, showcasing advanced Python development principles and seamless integration with Frappe's features. This system adheres to Frappe's best practices and guidelines, providing a robust solution for managing conferences effectively.

---

## Features

- **Doctypes**: Define, structure, and manage your data efficiently.
- **Custom API Endpoints**: For seamless integration with external systems.
- **Business Logic**: Custom server-side scripts to handle complex workflows.
- **Dynamic Reports**: Easily generate and customize reports.
- **Custom UI**: User-friendly and responsive interfaces using Frappe's templating tools.
- **Client-Side Scripts**: Enhance interactivity with JavaScript customizations.

---

## Prerequisites

To run this system, ensure you have the following installed:

- **MariaDB**: Version 10.6.6 or higher
- **Python**: Version 3.10, 3.11, or 3.12
- **Node.js**: Version 18 or 20
- **Redis**: Version 6
- **Yarn**: Version 1.12 or higher
- **pip**: Version 20 or higher
- **wkhtmltopdf**: For PDF generation

Follow the [Frappe Installation Guide](https://frappeframework.com/docs/user/en/installation) for detailed steps.

---

## Setup

### 1. Navigate to Your Bench Directory
Change into your bench directory using the following command:
```bash
cd frappe-bench
```

### 2. Create a New Site:
Run the following command to create a new site:

```bash
bench new-site conference.localhost
```

### 3. Install the App:
Install the Conference Management System application on the newly created site:

```bash
bench --site conference.localhost install-app conference_management
```

### 4. Run Migrations:
To create the necessary DocTypes in the Frappe UI, run migrations:

```bash
bench --site conference.localhost migrate
```

### 5. Start Bench:
Start the development server to access the application:

```bash
bench start
```

### 6. Access the Application:
Open your browser and navigate to:

```bash
http://conference.localhost:8000
```

---

## Business Logic and Scripts

### DocTypes Used:
The Frappe app is built around several core DocTypes, each designed to manage different aspects of the conference management system. Here’s how the logic is implemented across the following DocTypes:

### Conferences
![image](https://github.com/user-attachments/assets/4ca61806-8c7c-43ad-b105-c30758bbe5a6)

- **The Conference DocType** holds general information about a conference, including the name, start and end dates, and conference schedule.
- **Business Logic**: Ensures that all session times fall within the conference’s start and end time.

### Session
![image](https://github.com/user-attachments/assets/c502c8f6-29c7-46b1-b565-624eaa6d9fc7)

- **The Session DocType** stores the session details, including session name, speaker, start time, and end time.
- **Business Logic**:
  - Ensures no session overlaps with another session in the same conference.
  - Verifies that the session start time is earlier than the end time.
  - Ensures that sessions fall within the conference’s time frame.

### Attendee
![image](https://github.com/user-attachments/assets/daffb696-5dcb-4d81-9ed5-33505ea47bcc)

- **The Attendee DocType** contains information about individuals attending the conference, including their name, email, and the sessions they’re registered for.
- **Business Logic**:
  - If an attendee registers for a session that overlaps with another session they are already registered for, an alert is shown.
  - Preferences for sessions are stored for each attendee.

### Preference
![image](https://github.com/user-attachments/assets/a4bf4714-1671-423d-bf05-98124f611e2f)

- **The Preference DocType** represents an attendee's preferences for sessions. It links to the sessions that an attendee prefers to attend.
- **Business Logic**:
  - This DocType is used to send personalized session recommendations based on the attendee's preferences.

### Registration
![image](https://github.com/user-attachments/assets/2e1741f7-af37-44f9-9fef-f5adf2f9b568)

- **The Registration DocType** tracks which sessions an attendee has registered for and their payment status.
- **Business Logic**:
  - Verifies whether a session has reached its seat capacity before allowing a new registration.
  - Updates the payment status when a registration payment is processed. This could include integrating a mock payment function to simulate the payment process.
  - The mock payment function randomly determines the payment status with a 70% chance of success (marked as "Paid") and a 30% chance of failure or pending status (marked as "Failed" or "Pending").

### Apilog
![image](https://github.com/user-attachments/assets/06eac140-7f0a-46af-b5c4-e9b784ba3d7f)

- **The Apilog DocType** logs API requests and responses, especially for tracking session recommendations and attendee actions.
- **Business Logic**:
  - Logs API calls process, ensuring that system interactions are tracked for debugging and audit purposes.
```
```
## Conference Management API Documentation

### 1. Fetch Upcoming Conferences Api
![image](https://github.com/user-attachments/assets/5f376082-225e-4b66-84be-6e13bae2829a)

**API Endpoint:**
- **URL:** `http://conference.local:8000/upcomingConferencesApi1` (access it using local server after bench start)
- **Method:** GET
- **Description:** Fetch a list of all upcoming conferences along with their sessions. This can be accessed via the local server and the UI is created using Jinja templates to display available conferences and their sessions.

**Request Body (JSON):**
```json
Empty
```
**Postman API:**
- **API Endpoint:** `http://conference.local:8000/api/method/getupcomingConference`
- **Method:** GET
- **Description:** Use this API to fetch a list of all upcoming conferences and sessions.

![image](https://github.com/user-attachments/assets/097d094f-80cc-4a37-b4ce-a9403920e74d)

**Request Example:**
```http
GET /api/method/getupcomingConference HTTP/1.1
Host: conference.local:8000
```

**Response Example:**
```json
{
    "message": {
        "conferences": [
            {
                "conference_name": "Tally World",
                "start_date": "2024-11-21",
                "end_date": "2024-11-25",
                "status": "Upcoming",
                "sessions": [
                    {
                        "session_name": "BG",
                        "speaker": "BG",
                        "start_time": "2024-11-21 13:20:46",
                        "end_time": "2024-11-21 15:20:46"
                    },
                    {
                        "session_name": "GST",
                        "speaker": "BG",
                        "start_time": "2024-11-21 14:05:28",
                        "end_time": "2024-11-21 14:10:28"
                    },
                    {
                        "session_name": "Intro",
                        "speaker": "BG",
                        "start_time": "2024-11-22 13:16:49",
                        "end_time": "2024-11-22 16:32:59"
                    }
                ]
            },
            {
                "conference_name": "dss",
                "start_date": "2024-11-23",
                "end_date": "2024-11-26",
                "status": "Upcoming",
                "sessions": []
            },
            {
                "conference_name": "New conference",
                "start_date": "2024-11-23",
                "end_date": "2024-11-29",
                "status": "Upcoming",
                "sessions": [
                    {
                        "session_name": "first",
                        "speaker": "ds",
                        "start_time": "2024-11-23 14:05:05",
                        "end_time": "2024-11-24 14:05:05"
                    },
                    {
                        "session_name": "two",
                        "speaker": "fff",
                        "start_time": "2024-11-28 14:05:54",
                        "end_time": "2024-11-28 15:05:54"
                    },
                    {
                        "session_name": "gff",
                        "speaker": "y",
                        "start_time": "2024-11-28 20:45:30",
                        "end_time": "2024-11-28 23:45:30"
                    }
                ]
            },
            {
                "conference_name": "h1",
                "start_date": "2024-11-24",
                "end_date": "2024-11-29",
                "status": "Upcoming",
                "sessions": [
                    {
                        "session_name": "hh1",
                        "speaker": "d",
                        "start_time": "2024-11-24 04:53:25",
                        "end_time": "2024-11-24 07:53:25"
                    },
                    {
                        "session_name": "hh22",
                        "speaker": "ee",
                        "start_time": "2024-11-25 04:53:52",
                        "end_time": "2024-11-25 07:53:52"
                    }
                ]
            },
            {
                "conference_name": "cc1",
                "start_date": "2024-11-24",
                "end_date": "2024-11-29",
                "status": "Upcoming",
                "sessions": [
                    {
                        "session_name": "ss1",
                        "speaker": "stanch",
                        "start_time": "2024-11-24 04:38:33",
                        "end_time": "2024-11-24 09:38:33"
                    },
                    {
                        "session_name": "ss2",
                        "speaker": "Tally",
                        "start_time": "2024-11-24 04:39:05",
                        "end_time": "2024-11-25 09:39:05"
                    }
                ]
            },
            {
                "conference_name": "no 1",
                "start_date": "2024-11-24",
                "end_date": "2024-11-29",
                "status": "Upcoming",
                "sessions": [
                    {
                        "session_name": "s 1",
                        "speaker": "stanch",
                        "start_time": "2024-11-24 04:25:29",
                        "end_time": "2024-11-24 09:25:29"
                    },
                    {
                        "session_name": "s2",
                        "speaker": "tally",
                        "start_time": "2024-11-25 04:26:15",
                        "end_time": "2024-11-26 04:26:15"
                    },
                    {
                        "session_name": "s3",
                        "speaker": "bg",
                        "start_time": "2024-11-25 04:26:58",
                        "end_time": "2024-11-25 04:26:58"
                    }
                ]
            },
            {
                "conference_name": "Stanch solutions",
                "start_date": "2024-11-24",
                "end_date": "2024-11-30",
                "status": "Upcoming",
                "sessions": [
                    {
                        "session_name": "ssss1",
                        "speaker": "director",
                        "start_time": "2024-11-24 05:04:19",
                        "end_time": "2024-11-24 07:04:19"
                    },
                    {
                        "session_name": "ssss2",
                        "speaker": "BG",
                        "start_time": "2024-11-24 05:04:59",
                        "end_time": "2024-11-25 07:03:59"
                    }
                ]
            },
            {
                "conference_name": "new one",
                "start_date": "2024-11-25",
                "end_date": "2024-11-29",
                "status": "Upcoming",
                "sessions": [
                    {
                        "session_name": "fd",
                        "speaker": "fdvgfgf",
                        "start_time": "2024-11-25 09:41:33",
                        "end_time": "2024-11-25 12:41:33"
                    },
                    {
                        "session_name": "sdd",
                        "speaker": "ewer",
                        "start_time": "2024-11-26 09:42:02",
                        "end_time": "2024-11-26 14:42:02"
                    }
                ]
            },
            {
                "conference_name": "Stanch.io",
                "start_date": "2024-11-26",
                "end_date": "2024-11-30",
                "status": "Upcoming",
                "sessions": [
                    {
                        "session_name": "Stanch sess",
                        "speaker": "stanch founder",
                        "start_time": "2024-11-27 18:02:00",
                        "end_time": "2024-11-28 18:02:00"
                    },
                    {
                        "session_name": "Business dev",
                        "speaker": "engineering manager",
                        "start_time": "2024-11-29 07:47:31",
                        "end_time": "2024-11-29 10:47:31"
                    },
                    {
                        "session_name": "Finance",
                        "speaker": "Stanch Director",
                        "start_time": "2024-11-29 20:45:17",
                        "end_time": "2024-11-29 22:53:17"
                    }
                ]
            }
        ]
    }
}
```

---

### 2. Session Registration API
![image](https://github.com/user-attachments/assets/2435aee5-1e22-47e3-a469-18df8f04c441)

**Postman API:**
- **API Endpoint:** `http://conference.local:8000/api/method/add_attendee_and_register`
- **Method:** POST
- **Description:** Accepts attendee and session details in the request payload and registers them for a conference session, before Conferences and the Sessions needs to be created.

**Request Body (JSON):**
```json
{
    "attendee": {
        "attendee_name": "shashi",   
        "email": "newstudent@gmail.com",
        "phone_number": "1234567890",
        "organization": "Stanch.io"
    },
    "preferences": [
        {
            "session": "Finance"
        },
        {
            "session": "Business dev"
        },
        {
            "session": "GST"
        }
    ],
    "registration": {
        "conference": "Stanch.io",
        "session": "Business dev"
    }
}
```

**Response Example:**
```json
{
    "message": {
        "status": "success",
        "message": "Attendee added and registration completed successfully.",
        "payment_status": "Pending"
    }
}
```

---

### 3. Payment Simulation API
![image](https://github.com/user-attachments/assets/303ced19-0234-4656-8c9a-1d25d4d43aa7)

**Postman API:**
- **API Endpoint:** `http://conference.local:8000/api/method/process_mock_payment`
- **Method:** POST
- **Description:** Simulate payment processing for a registration ID and return the payment status.

**Request Body (JSON):**
```json
{
  "attendee_email": "helloStanch@gmail.com",
  "session_name": "Business dev",
  "payment_status": ""
}
```

**Response Example:**
```json
{
    "message": {
        "status": "success",
        "message": "Payment successfully processed for Session: Business dev (Registration ID: Stanch.io-Business dev-newstudent@gmail.com)",
        "payment_status": "Paid"
    }
}
or
{
    "message": {
        "status": "success",
        "message": "Payment failed for Session: Business dev (Registration ID: Stanch.io-Business dev-newstudent@gmail.com). Please try again.",
        "payment_status": "Failed"
    }
}
or
{
    "message": {
        "status": "success",
        "message": "Payment is pending. If amount is deducted, we will update the status. Otherwise, you will receive a refund.",
        "payment_status": "Pending"
    }
}
```

---

### 4. Search Conferences and Sessions
![image](https://github.com/user-attachments/assets/7ff7d29a-72c4-4352-bfca-414147a281ab)

**API Endpoint:**
- **URL:** `http://conference.local:8000/SearchconferenceSessionApi1` (access it using the local dev server)
- **Method:** GET
- **Description:** Allows searching for conferences and sessions by keywords in the name or description. This can be accessed via the local server UI created with Jinja templates.

**Search functionality:**
When searching for a conference or session using keywords, it will fetch relevant results from the API. If no results are found, a proper message will be shown.

**Request Example:**
```http
GET /SearchconferenceSessionApi1?query=AI HTTP/1.1
Host: conference.local:8000
```

**Response Example:**
```json
[
    {
        "conference_name": "Tech Summit 2024",
        "sessions": [
            {
                "session_name": "AI Innovations",
                "speaker": "John Doe",
                "start_time": "2024-12-01 10:00:00",
                "end_time": "2024-12-01 11:00:00"
            }
        ]
    }
]
```

---

### 5. Get Recommendations for an Attendee Api
![image](https://github.com/user-attachments/assets/de550d1a-ab47-4384-9465-ed8c93ec0982)

**Postman API:**
- **API Endpoint:** `http://conference.local:8000/api/method/get_recommendations`
- **Method:** POST
- **Description:** Fetch recommended sessions for an attendee based on their preferences.

**Request Body (JSON):**
```json
{
    "attendee_email": "helloStanch@gmail.com"
}
```

**Response Example:**
```json
{
    "message": {
        "message": {
            "attendee": "shashi",
            "conferences": [
                {
                    "conference_name": "New conference",
                    "start_date": "2024-11-23",
                    "end_date": "2024-11-29",
                    "status": "Upcoming",
                    "sessions": [
                        {
                            "session_name": "two",
                            "speaker": "fff",
                            "start_time": "2024-11-28 14:05:54",
                            "end_time": "2024-11-28 15:05:54",
                            "session_fee": 400.0
                        }
                    ],
                    "speakers": [
                        "fff"
                    ]
                },
                {
                    "conference_name": "Stanch.io",
                    "start_date": "2024-11-26",
                    "end_date": "2024-11-30",
                    "status": "Upcoming",
                    "sessions": [
                        {
                            "session_name": "Finance",
                            "speaker": "Stanch Director",
                            "start_time": "2024-11-29 20:45:17",
                            "end_time": "2024-11-29 22:53:17",
                            "session_fee": 500.0
                        },
                        {
                            "session_name": "Business dev",
                            "speaker": "engineering manager",
                            "start_time": "2024-11-29 07:47:31",
                            "end_time": "2024-11-29 10:47:31",
                            "session_fee": 0.0
                        }
                    ],
                    "speakers": [
                        "engineering manager",
                        "Stanch Director"
                    ]
                },
                {
                    "conference_name": "Tally World",
                    "start_date": "2024-11-21",
                    "end_date": "2024-11-25",
                    "status": "Upcoming",
                    "sessions": [
                        {
                            "session_name": "GST",
                            "speaker": "BG",
                            "start_time": "2024-11-21 14:05:28",
                            "end_time": "2024-11-21 14:10:28",
                            "session_fee": 0.0
                        },
                        {
                            "session_name": "BG",
                            "speaker": "BG",
                            "start_time": "2024-11-21 13:20:46",
                            "end_time": "2024-11-21 15:20:46",
                            "session_fee": 0.0
                        },
                        {
                            "session_name": "Intro",
                            "speaker": "BG",
                            "start_time": "2024-11-22 13:16:49",
                            "end_time": "2024-11-22 16:32:59",
                            "session_fee": 0.0
                        }
                    ],
                    "speakers": [
                        "BG"
                    ]
                },
                {
                    "conference_name": "Stanch solutions",
                    "start_date": "2024-11-24",
                    "end_date": "2024-11-30",
                    "status": "Upcoming",
                    "sessions": [
                        {
                            "session_name": "ssss2",
                            "speaker": "BG",
                            "start_time": "2024-11-24 05:04:59",
                            "end_time": "2024-11-25 07:03:59",
                            "session_fee": 200.0
                        }
                    ],
                    "speakers": [
                        "BG"
                    ]
                },
                {
                    "conference_name": "no 1",
                    "start_date": "2024-11-24",
                    "end_date": "2024-11-29",
                    "status": "Upcoming",
                    "sessions": [
                        {
                            "session_name": "s3",
                            "speaker": "bg",
                            "start_time": "2024-11-25 04:26:58",
                            "end_time": "2024-11-25 04:26:58",
                            "session_fee": 0.0
                        }
                    ],
                    "speakers": [
                        "bg"
                    ]
                }
            ]
        }
    }
}
```

---

### 6. Scheduler for Daily Email Recommendations
```json
    cmd --> bench --site conference.local console
    from conference_management.conference_management.scheduler import daily_task_scheduler
    daily_task_scheduler()
```
**Functionality:**
A scheduler is set up to run daily, fetching the recommended sessions for each attendee based on their preferences. The system then sends an email containing the recommended sessions.

---
## 7. Conference Report

**Screenshot:**
![image](https://github.com/user-attachments/assets/cf8f02ae-b78e-4969-ba67-ed238606714d)

**Purpose:**
The Conference Report provides insights into:
- Total attendees for each conference.
- Number of sessions conducted per conference.

**Features:**
- Displays a tabular format of conference name, attendee, registration, and session counts.
- A bar chart visualization for quick data interpretation.

**How to Use:**
- Access the report under `Reports > Conference reports` in the Frappe Desk.

---

## 8. Session Analysis Report

**Screenshot:**
![image](https://github.com/user-attachments/assets/fb88178f-1468-4a26-b65f-e7b2b3b3b779)

**Purpose:**
The Session Analysis Report provides insights into:
- Session-wise total registrations and remaining capacity.
- Revenue generated from each session based on paid registrations.

**Features:**
- Displays both tabular data and a bar chart for visual representation.
- Helps conference managers track session popularity and revenue.

---
## Error Handling and Logging:

**Screenshot:**
![image](https://github.com/user-attachments/assets/f899ad15-4082-4c76-aabd-d288c26f200d)

### 1. Improved User Experience
- **Users receive meaningful feedback for every action**, ensuring clarity and transparency.

### 2. System Monitoring
- **Logs provide a comprehensive view of system activity**, allowing developers to monitor API usage and identify issues.

### 3. Quick Debugging
- **Detailed logs with timestamps help trace issues quickly** during failures or inconsistencies.

## Some more screenshots of validation and records
![image](https://github.com/user-attachments/assets/104deffe-83cd-4124-b1a5-26f0f0930b63)
![image](https://github.com/user-attachments/assets/24ecb6d0-e149-4949-9bb0-3052d064230d)
![image](https://github.com/user-attachments/assets/c94386e4-ee98-4448-b4b6-af6ea9c361cb)
![image](https://github.com/user-attachments/assets/e145b5c5-30b7-4c3f-8ce7-73b3dc700055)
![image](https://github.com/user-attachments/assets/dfea9813-84db-4dcf-9606-c6f462337559)
![image](https://github.com/user-attachments/assets/1a4f395f-491e-4fba-9ed7-3d045d368bc3)
![image](https://github.com/user-attachments/assets/03fae989-7438-41df-b157-8a25cf0420ba)

```

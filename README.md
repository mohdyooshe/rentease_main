# RentEase - Peer-to-Peer Electronics Rental Platform

RentEase is a full-stack web application that allows users to rent premium electronics from people around them or list their own gear to earn money passively.

## Features
- **Two User Roles**: 'Owner' and 'Renter'.
- **Glassmorphism Design**: Stunning dark UI with frosted glass panels, neon accents, and animated backgrounds.
- **Live Search & Filters**: Renters can instantly search available gear by title or category.
- **Dynamic Rent Calculator**: Renters pick start and end dates, and the total cost is automatically calculated.
- **Order Management**: Owners can review, accept, or reject incoming rental requests.
- **Secure Authentication**: Raw SQL PyMySQL backend with `werkzeug` password hashing and Flask Sessions.
- **Image Uploads**: Owners can upload thumbnails of their items, saved securely to the server.

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- MySQL Server

### 2. Install Dependencies
Create a virtual environment and install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Database Setup
1. Create a `.env` file in the root directory and add your MySQL credentials:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=rentease
   SECRET_KEY=your_secret_key
   ```
2. Run the provided SQL schema script to initialize the tables:
   ```bash
   mysql -u root -p < schema.sql
   ```

### 4. Run the Application
Start the Flask development server:
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000/`.

## Application Routes

### Public
- `/` - Homepage (Index)
- `/signup` - Create a new Owner or Renter account
- `/login` - Log in to an existing account
- `/logout` - Clear session and log out

### Renter Restricted
- `/browse` - Browse all available items
- `/rent/<int:item_id>` - (POST) Submit a rental request
- `/renter/dashboard` - View renter statistics
- `/renter/orders` - View order history and status

### Owner Restricted
- `/owner/dashboard` - View listed inventory and earnings stats
- `/owner/add_item` - Publish a new item
- `/owner/requests` - Review pending incoming rental requests
- `/owner/request/<int:request_id>/<action>` - (POST) Accept or reject a request

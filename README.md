![image](https://github.com/AdarshPBaiju/Ecommerce-with-payment/assets/161452962/58e1524c-f451-40a1-9986-dd9ace60c464)# Ecomm Project



This is an e-commerce project built using Django 5.0.3. The project includes multiple applications like accounts, brand, category, store, carts, and orders to manage various aspects of an online store.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Applications](#applications)
- [Features](#features)
- [Usage](#usage)

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/AdarshPBaiju/Ecommerce-with-payment.git
    cd Ecommerce-with-payment
    ```

2. **Create a virtual environment**:
    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment**:
    - On Windows:
        ```bash
        venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

4. **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5. **Set up environment variables**:
    Create a `.env` file in the project root directory and add the following environment variables:
    ```plaintext
    SECRET_KEY=your_secret_key
    DEBUG=True
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=your_db_host
    EMAIL_HOST=your_email_host
    EMAIL_PORT=your_email_port
    EMAIL_HOST_USER=your_email_host_user
    EMAIL_HOST_PASSWORD=your_email_host_password
    EMAIL_USE_TLS=True
    DEFAULT_FROM_EMAIL=your_default_from_email
    TWILIO_ACCOUNT_SID=your_twilio_account_sid
    TWILIO_AUTH_TOKEN=your_twilio_auth_token
    TWILIO_PHONE_NUMBER=your_twilio_phone_number
    ```

6. **Apply migrations**:
    ```bash
    python manage.py migrate
    ```

7. **Create a superuser**:
    ```bash
    python manage.py createsuperuser
    ```

8. **Collect static files**:
    ```bash
    python manage.py collectstatic
    ```

## Configuration

Ensure that the following settings are configured correctly in `ecomm/settings.py`:

- `ALLOWED_HOSTS` includes your development and production hosts.
- `DATABASES` settings are correctly set to your database configurations.
- SMTP configuration is set up for sending emails.
- Twilio settings are configured for SMS notifications.

## Running the Project

1. **Start the development server**:
    ```bash
    python manage.py runserver
    ```

2. **Access the application**:
    Open your web browser and navigate to `http://127.0.0.1:8000`.

## Applications

- **accounts**: Manages user authentication and profiles.
- **brand**: Manages product brands.
- **category**: Manages product categories.
- **store**: Manages the product catalog.
- **carts**: Manages shopping carts.
- **orders**: Manages customer orders.

## Features

- User registration and authentication.
- Product catalog with categories and brands.
- Shopping cart management.
- Order processing and management.
- Admin interface for managing the store.
- Email notifications for various events.
- SMS notifications using Twilio.

## Usage

1. **Admin Interface**:
    Access the admin interface at `http://127.0.0.1:8000/admin` using the superuser credentials.

2. **User Registration and Login**:
    Users can register and log in to the platform to manage their profiles and place orders.

3. **Product Management**:
    Admins can add, update, and delete products, brands, and categories through the admin interface.

4. **Order Management**:
    Users can place orders and view their order history. Admins can manage orders through the admin interface.

![Home Page](https://media.licdn.com/dms/image/D562DAQFFFbHf26pjhg/profile-treasury-image-shrink_1920_1920/0/1712985491525?e=1717592400&v=beta&t=NRnPXy1wc42M0a5rK6-BdkjEEo0NJL4rKVnXP7sIHLk)


Home Page

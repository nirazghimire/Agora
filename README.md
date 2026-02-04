# Agora - Buy.Sell.Connect

A full-stack e-commerce web application supporting multiple user roles: **Buyers**, **Sellers**, and **Admin** where buyers can purchase and return products. Sellers manage products and receive payments. Admins handle approvals and oversight.

## Tech Stack

- **Frontend**: Next.js + TypeScript  
  - React Server Components  
  - Tailwind CSS + Shadcn/ui 
  - NextAuth.js / Auth.js (for authentication)  

- **Backend**: Django  
  - Django REST Framework Simple JWT (token authentication)  

- **Database**: PostgreSQL

## Features

### Authentication & Roles
- Role-based access: Buyer, Seller, Admin
- Registration + Login + Logout
- Admin approval workflow for new sellers and products
- JWT-based authentication

### Buyer Features
- Product search (full-text + filters)
- Product comparison
- Shopping cart & checkout
- Order history
- Product returns / refund requests

### Seller Features
- Add / edit / delete products
- Manage inventory & pricing
- View sales analytics
- Payouts via integrated payment gateway

### Admin Features
- Approve / block users & products
- Moderate content & reviews
- Platform-wide analytics & logs

### Team Members

- Ayush Dhungana (ad2431)
- Niraj Ghimire (ng733)


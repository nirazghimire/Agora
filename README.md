# Agora Marketplace

## Overview
Agora is a role-based e-commerce platform inspired by the fundamental mechanics of eBay, designed to facilitate a streamlined marketplace experience. Built on a sturdy foundation using Django 5 and PostgreSQL, the application orchestrates dynamic interactions between distinct user personas—buyers, sellers, and administrators. Our system emphasizes a secure, role-restricted environment that handles everything from product discovery to secure checkout and post-purchase support.

## Core Architecture and Technology
The platform is powered by a modern, reliable stack:
- **Backend Framework:** Django 5 drives the core logic, managing intricate workflows and relational data.
- **Frontend Presentation:** Utilizing Django's robust templating engine combined with Vanilla CSS and JavaScript, we deliver a clean, responsive user interface without relying on heavy frontend frameworks.
- **Data Management:** A robust PostgreSQL database serves as our persistent storage, carefully configured via environment variables to ensure state predictability and security across deployments.
- **Asset Handling:** Django's native media storage seamlessly manages user-uploaded content, such as product imagery.
- **Security:** We deeply integrate Django's authentication system, extending it with critical role-based access controls (RBAC) to segment functionality appropriately across different user types.

## The Marketplace Ecosystem

The Agora platform thrives on the interaction between three key roles, each possessing a tailored suite of capabilities designed to empower their specific goals within the marketplace.

### The Buyer Experience
Buyers are the core of the marketplace. Upon secure registration and login, buyers are granted access to browse a curated catalog of approved products. They can seamlessly manage their potential purchases through an intuitive cart system, allowing for quantity adjustments and easy removal. The checkout process is streamlined, currently fixed to United States shipping, converting carts into finalized orders safely. Post-purchase, buyers retain access to a comprehensive order history and are empowered to initiate single-use return requests with provided reasons, ensuring consumer confidence.

### The Seller Operations
Sellers drive the inventory of Agora. This role provides the necessary tools to establish a storefront within the platform. Upon authentication, sellers can generate detailed product listings, which enter an unapproved state pending administrative review. Once products hit the marketplace, sellers have access to comprehensive sales histories. Crucially, sellers maintain control over their post-sales support, with the ability to review, approve, reject, or mark as received/refunded any return requests initiated by buyers on their specific items.

### Platform Administration
Administrators serve as the moderators and operators of the Agora ecosystem. Accessible only via a secured, restricted-role dashboard, administrators ensure the quality and safety of the platform. They hold the critical responsibility of reviewing new product listings, with the authority to approve, reject, or revoke visibility at any time. Furthermore, administrators manage the user base directly, holding the power to view user statistics and enforce community guidelines by banning or unbanning buyer and seller accounts as necessary.

## Key Workflows and Constraints

The integrity of Agora is maintained through strictly enforced workflows and business rules.

- **Role Isolation:** The system is heavily siloed. Buyers cannot access seller tools, sellers are restricted from the buyer-specific checkout flow, and the administrative dashboard is fiercely protected against non-admin access.
- **Product Lifecycle:** For a product to be visible to buyers, it must not only be created but explicitly approved by an admin, and the listing seller must have an active, unbanned account.
- **Return Protocol:** Returns are strictly managed. Only the original purchasing buyer can initiate a return, and they may only do so once per ordered item. Correspondingly, only the specific seller of that item can process the return request.
- **Security First:** Critical actions—such as authentication state changes, checkout processes, and return initiations—are backed by rigorous server-side validation. All state-mutating requests (POST) are fortified with CSRF protection.


## Recently Implemented Features (Completed)
- **Product Reviews & Ratings:** Integrated a comprehensive, buyer-only rating and review system for products they have purchased.
- **Direct Product Comparisons:** A dedicated, stateful `/compare/` tool allowing buyers to compare up to 3 products side-by-side.
- **Seller RSS Feed:** A live syndication feed broadcasting recent sales explicitly for each seller.
- **Explicit Rejection Feedback:** Administrative tools to mark products as rejected and securely attach rejection reasons visible to the listing seller.

## Scope and Future Roadmap

While Agora provides a complete end-to-end marketplace experience, certain features remain outside our current scope and are earmarked for future iterations:
- The development of a comprehensive, public-facing RESTful API.
- Integration of live payment gateways for automated payout processing.

## Project Contributors
- Ayush Dhungana (ad2431)
- Niraj Ghimire (ng733)
- Rohan Patel (rrp196)

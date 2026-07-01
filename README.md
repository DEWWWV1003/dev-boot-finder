# Dev Boot Finder (DBF)

An advanced e-commerce platform for football (soccer) boots and jerseys. Built with Python and Flask.

## Features
- **Storefront & Catalog**: Browse modern and retro football boots and jerseys.
- **AI 3D Sizing**: Uses Machine Learning (Random Forest) logic to recommend boot sizes based on uploaded foot scans.
- **PRO Design Studio**: A customizer that lets users design their own boots with custom colors, numbers, flags, and stud types using interactive SVG graphics.
- **AR Virtual Try-On**: A web-based Augmented Reality studio that accesses the device camera to overlay and size football boots over the user's foot.
- **Admin Dashboard**: Full banking ledger, order tracking, and inventory management.
- **Express Checkout**: Apple Pay, Google Pay, and PayPal mock integrations.

## Installation

1. Ensure you have Python installed.
2. Clone the repository.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the database initialization (if needed):
   ```bash
   python init_db.py
   ```

## Running the App

The platform is split into two portals:

**User Storefront:**
```bash
python app_user.py
```
*(Runs on http://localhost:5000)*

**Admin Dashboard:**
```bash
python app_admin.py
```
*(Runs on http://localhost:5001)*

## Admin Access
- **Username:** admin
- **Password:** admin123

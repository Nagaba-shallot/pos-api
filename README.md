# Point of Sale (POS) CRUD API

A production-ready, fully relational Point of Sale (POS) backend built with **FastAPI**, **SQLAlchemy ORM (v2.0+)**, and **PostgreSQL**. This system manages a complete retail workflow including users, categories, products, suppliers, customers, sales orders, automated inventory line items, payments, and receipts.

## Features & Architecture

- **Full Relational CRUD**: Comprehensive POST, GET, PUT, and DELETE operations implemented for all 9 core domain entities.
- **Strict Database Integrity**: Managed entirely via PostgreSQL Foreign Key constraints to prevent orphan rows (e.g., preventing a sale item from linking to a non-existent product).
- **FastAPI Dependency Injection**: Clean, thread-safe database session life-cycle handling via context-aware connection pooling.
- **Robust Schema Validation**: Powered by Pydantic v2 schemas using modern configuration dictionaries (`ConfigDict(from_attributes=True)`).
- **Graceful Error Handling**: Rest-compliant execution pathways returning strict semantic HTTP Status Codes (e.g., `201 Created` for insertions, `204 No Content` for clean deletions, and `404 Not Found` for missing resources).



## Entity Relationship Mapping

The API manages the following interconnected domain models:
1. **Users**: System operators (Cashiers, Managers, Admins) who manage transactions.
2. **Categories**: Product classification metrics.
3. **Suppliers**: Wholesale trade vendors supplying items.
4. **Products**: Retail items tracking pricing, quantities, and safety stock reorder triggers.
5. **Customers**: Consumer profiles tracking localized delivery coordinates.
6. **Sales**: Master ledger tracking transaction parameters (Totals, Tax, Discounts).
7. **Sale Items**: Nested transaction line items mapping products to sales quantities.
8. **Payments**: Processing ledger backing transactions (Cash, Card, Mobile).
9. **Receipts**: Customer checkout documents auto-generating tracking codes via transactional hooks.



## Installation & Setup

### 1. Clone & Initialize Environment

`git clone https://github.com/Nagaba-shallot/pos-api
cd pos
uv venv env
source env/bin/activate
uv pip install -r requirements.txt`


### 2. Configure Database Context
Ensure you have a live **PostgreSQL** instance running locally or remotely, and update your configuration string inside `app/database.py`:
`SQLALCHEMY_DATABASE_URL = "postgresql://username:password@localhost:5432/pos_db"`

### 3. Launch Development Reloader
`
cd app
uvicorn main:app --reload
`
The server will bind to `http://127.0.0.1:8000`.


## Testing the API
Open your browser and navigate to the integrated interactive Open-API dashboard, Swagga UI:
`http://127.0.0.1:8000/docs#/`

### Recommended Verification Flow:
1. **Seed Structural Entities**: Submit a `POST /users/` and `POST /categories/` record first.
2. **Setup Vendor Inventory**: Submit a `POST /suppliers/` profile, followed by a `POST /products/` payload mapping back to the created category and supplier primary keys.
3. **Register Transaction**: Populate a consumer via `POST /customers/`, then commit a master sales order via `POST /sales/`.
4. **Checkout Processing**: Append transaction item entries via `POST /sale-items/` and settle balances using `POST /payments/`.

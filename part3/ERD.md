```mermaid
erDiagram
    USERS {
        varchar(36) id PK "UUID"
        varchar(120) email UK "Unique email"
        varchar(255) password_hash "Hashed password"
        varchar(50) first_name "First name"
        varchar(50) last_name "Last name"
        boolean is_admin "Admin role flag"
        datetime created_at "Creation timestamp"
        datetime updated_at "Update timestamp"
    }
   
    PLACES {
        varchar(36) id PK "UUID"
        varchar(100) title "Place title"
        text description "Place description"
        decimal(10,2) price "Price per night"
        float latitude "GPS latitude"
        float longitude "GPS longitude"
        varchar(36) owner_id FK "Owner reference"
        datetime created_at "Creation timestamp"
        datetime updated_at "Update timestamp"
    }
   
    REVIEWS {
        varchar(36) id PK "UUID"
        text text "Review content"
        integer rating "Rating 1-5"
        varchar(36) user_id FK "User reference"
        varchar(36) place_id FK "Place reference"
        datetime created_at "Creation timestamp"
        datetime updated_at "Update timestamp"
    }
   
    AMENITIES {
        varchar(36) id PK "UUID"
        varchar(50) name UK "Amenity name"
        text description "Amenity description"
        datetime created_at "Creation timestamp"
        datetime updated_at "Update timestamp"
    }
   
    PLACE_AMENITIES {
        varchar(36) place_id PK,FK "Place reference"
        varchar(36) amenity_id PK,FK "Amenity reference"
    }
   
    %% Relations
    USERS ||--o{ PLACES : "owns (1:N)"
    USERS ||--o{ REVIEWS : "writes (1:N)"
    PLACES ||--o{ REVIEWS : "has (1:N)"
    PLACES ||--o{ PLACE_AMENITIES : "has (1:N)"
    AMENITIES ||--o{ PLACE_AMENITIES : "belongs_to (1:N)"
   
    %% Constraints
    USERS {
        constraint email_unique "UNIQUE(email)"
        constraint email_not_null "NOT NULL(email)"
        constraint password_not_null "NOT NULL(password_hash)"
        index idx_email "INDEX(email)"
    }
   
    PLACES {
        constraint owner_fk "FOREIGN KEY(owner_id) REFERENCES users(id)"
        constraint price_positive "CHECK(price > 0)"
        index idx_owner "INDEX(owner_id)"
        index idx_location "INDEX(latitude

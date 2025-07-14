```mermaid
erDiagram
    users ||--o{ places : "has"
    users ||--o{ reviews : "writes"
    places ||--o{ reviews : "has"
    places }o--o{ amenities : "has"

    users {
        VARCHAR(36) id PK
        DATETIME created_at
        DATETIME updated_at
        VARCHAR(50) first_name
        VARCHAR(50) last_name
        VARCHAR(120) email UNIQUE
        VARCHAR(128) _password
        BOOLEAN is_admin
    }

    places {
        VARCHAR(36) id PK
        DATETIME created_at
        DATETIME updated_at
        VARCHAR(100) title
        TEXT description
        INTEGER price_per_night
        FLOAT latitude
        FLOAT longitude
        VARCHAR(255) address
        VARCHAR(100) city
        INTEGER number_rooms
        INTEGER number_bathrooms
        INTEGER max_guests
        VARCHAR(36) user_id FK "owner"
    }

    reviews {
        VARCHAR(36) id PK
        DATETIME created_at
        DATETIME updated_at
        TEXT text
        INTEGER rating
        VARCHAR(36) user_id FK "reviewer"
        VARCHAR(36) place_id FK "on_place"
    }

    amenities {
        VARCHAR(36) id PK
        DATETIME created_at
        DATETIME updated_at
        VARCHAR(100) name UNIQUE
    }

    place_amenities {
        VARCHAR(36) place_id PK,FK
        VARCHAR(36) amenity_id PK,FK
    }

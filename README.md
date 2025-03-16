# API to serve notes in markdown

This will be a simple API to serve docs in markdown. 

## TODO list

- Deployment



### Wish list 

- Auto-categorization and auto-tag of uploaded markdowns.

## Data models

```mermaid
erDiagram
    NOTE {
        int id
        string name
        datetime last_updated
        string abstract
        bool is_public
        int category_id FK "to CATEGORY"
    }
    CATEGORY {
        int id
        string name UK
    }

    
    TAG {
        int id
        string name UK "UK with category_id"
        int category_id UK, FK "FK to CATEGORY, UK with name"
    }
    
    NOTETAGLINK {
        int id
        int tag_id FK "to TAG"
        int note_id FK "to NOTE"
    }
    CATEGORY ||--o{ NOTE : ""
    NOTETAGLINK }o--o| TAG: ""
    NOTETAGLINK }o--o| NOTE: ""
```

## Endpoints

Autodocumented. See swagger ui.

# Running all unit tests from CLI
Better to set the environment variable IN_MEMORY_DB="Yes":
```sh
env IN_MEMORY_DB="Yes" python -m unittest
```
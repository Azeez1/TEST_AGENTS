# Mermaid Diagram Syntax Reference

Complete reference for creating professional flow diagrams using Mermaid.

## Diagram Types

### 1. Flowchart / Graph Diagrams

**Orientations:**
- `graph TD` - Top to Down (vertical)
- `graph LR` - Left to Right (horizontal)
- `graph BT` - Bottom to Top
- `graph RL` - Right to Left

**Node Shapes:**
```mermaid
graph LR
    A[Rectangle] --> B(Rounded Rectangle)
    B --> C([Stadium/Pill Shape])
    C --> D[[Subroutine]]
    D --> E[(Database)]
    E --> F((Circle))
    F --> G>Asymmetric]
    G --> H{Diamond/Decision}
    H --> I{{Hexagon}}
    I --> J[/Parallelogram/]
    J --> K[\Parallelogram Alt\]
    K --> L[/Trapezoid\]
    L --> M[\Trapezoid Alt/]
```

**Arrow Types:**
```mermaid
graph LR
    A --> B  %% Solid arrow
    C --- D  %% Line without arrow
    E -.-> F  %% Dotted arrow
    G -.- H  %% Dotted line
    I ==> J  %% Thick arrow
    K === L  %% Thick line
    M -- Text --> N  %% Arrow with text
    O -->|Text| P  %% Alternative text syntax
```

**Example System Architecture:**
```mermaid
graph TB
    User[User] --> LB[Load Balancer]
    LB --> WS1[Web Server 1]
    LB --> WS2[Web Server 2]
    WS1 --> API[API Gateway]
    WS2 --> API
    API --> Auth[Auth Service]
    API --> Data[Data Service]
    Data --> DB[(PostgreSQL)]
    Data --> Cache[(Redis Cache)]
    Auth --> DB
```

### 2. Sequence Diagrams

Show interactions between actors/systems over time.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Database

    User->>Frontend: Click Login
    Frontend->>API: POST /auth/login
    API->>Database: Validate credentials
    Database-->>API: User data
    API-->>Frontend: JWT Token
    Frontend-->>User: Redirect to Dashboard
```

**Advanced Features:**
```mermaid
sequenceDiagram
    actor Alice
    actor Bob

    Alice->>+Bob: Hello Bob, how are you?
    Bob-->>-Alice: Great!

    Note over Alice,Bob: Secure Connection

    alt Successful case
        Alice->>Bob: Request data
        Bob->>Alice: Send data
    else Failure case
        Alice->>Bob: Request data
        Bob->>Alice: Error 404
    end

    loop Every minute
        Alice->>Bob: Heartbeat
    end
```

### 3. State Diagrams

Show state transitions and system behavior.

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing: Start
    Processing --> Success: Complete
    Processing --> Failed: Error
    Success --> [*]
    Failed --> Idle: Retry
    Failed --> [*]: Give Up

    Processing --> Paused: Pause
    Paused --> Processing: Resume
```

**With Nested States:**
```mermaid
stateDiagram-v2
    [*] --> Active

    state Active {
        [*] --> Running
        Running --> Paused
        Paused --> Running
        Running --> [*]
    }

    Active --> Inactive: Stop
    Inactive --> Active: Start
```

### 4. Entity Relationship Diagrams (ER Diagrams)

Database schema and relationships.

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER {
        int id PK
        string email
        string name
        datetime created_at
    }
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        int id PK
        int user_id FK
        datetime created_at
        string status
    }
    PRODUCT ||--o{ ORDER_ITEM : "ordered in"
    PRODUCT {
        int id PK
        string name
        decimal price
        int stock
    }
    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal price
    }
```

**Relationship Types:**
- `||--||` : One to one
- `||--o{` : One to zero or more
- `||--|{` : One to one or more
- `}o--o{` : Zero or more to zero or more
- `}|--|{` : One or more to one or more

### 5. Class Diagrams

Object-oriented design and class relationships.

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
        +move()
    }

    class Dog {
        +String breed
        +bark()
        +fetch()
    }

    class Cat {
        +Boolean indoor
        +meow()
        +scratch()
    }

    Animal <|-- Dog
    Animal <|-- Cat

    class Owner {
        +String name
        +feedPet()
    }

    Owner "1" --> "*" Animal : owns
```

**Relationship Types:**
- `<|--` : Inheritance
- `*--` : Composition
- `o--` : Aggregation
- `-->` : Association
- `..>` : Dependency
- `..|>` : Realization

### 6. Gantt Charts

Project timelines and task scheduling.

```mermaid
gantt
    title Project Development Timeline
    dateFormat YYYY-MM-DD
    section Planning
    Requirements Gathering    :done, req, 2024-01-01, 2024-01-15
    Design Phase              :active, design, 2024-01-16, 2024-02-01

    section Development
    Backend Development       :dev1, 2024-02-01, 30d
    Frontend Development      :dev2, 2024-02-15, 25d
    Integration              :after dev1 dev2, 10d

    section Testing
    QA Testing               :test, after dev1, 15d
    User Acceptance Testing  :uat, after test, 10d

    section Deployment
    Production Deployment    :milestone, after uat, 0d
```

### 7. User Journey Diagrams

Map user interactions and experiences.

```mermaid
journey
    title User Shopping Experience
    section Browse
      Visit Website: 5: User
      View Products: 4: User
      Search Items: 3: User
    section Purchase
      Add to Cart: 4: User
      Checkout: 3: User
      Payment: 2: User, System
    section Post-Purchase
      Confirmation: 5: User, System
      Shipping Update: 4: System
      Delivery: 5: User
```

### 8. Git Graph

Version control branching visualization.

```mermaid
gitGraph
    commit
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
    commit
    branch feature
    checkout feature
    commit
    checkout main
    merge feature
    commit
```

### 9. Pie Charts

Simple data visualization.

```mermaid
pie title Technology Stack Usage
    "React" : 35
    "Vue" : 25
    "Angular" : 20
    "Svelte" : 15
    "Other" : 5
```

### 10. Quadrant Charts

Strategic planning and analysis.

```mermaid
quadrantChart
    title Technical Debt vs Business Value
    x-axis Low Business Value --> High Business Value
    y-axis Low Technical Debt --> High Technical Debt
    quadrant-1 Quick Wins
    quadrant-2 Major Projects
    quadrant-3 Fill-ins
    quadrant-4 Thankless Tasks
    Feature A: [0.8, 0.3]
    Feature B: [0.3, 0.7]
    Feature C: [0.6, 0.6]
    Feature D: [0.2, 0.2]
```

## Styling and Theming

### Built-in Themes

Available themes: `default`, `forest`, `dark`, `neutral`, `base`

Specify in HTML initialization:
```javascript
mermaid.initialize({ theme: 'dark' });
```

### Custom Styling with CSS Classes

```mermaid
graph LR
    A[Normal]:::highlight --> B[Styled]:::warning
    B --> C[Node]:::success

    classDef highlight fill:#f9f,stroke:#333,stroke-width:4px
    classDef warning fill:#ff9,stroke:#f66,stroke-width:2px
    classDef success fill:#9f9,stroke:#393,stroke-width:2px
```

### Inline Styling

```mermaid
graph LR
    A[Start] --> B[Process]
    style A fill:#ff9,stroke:#333,stroke-width:4px
    style B fill:#bbf,stroke:#33f,stroke-width:2px
```

## Best Practices

### 1. Clarity and Readability
- Use descriptive node labels
- Keep diagrams focused on one concept
- Avoid overcrowding nodes
- Use consistent naming conventions

### 2. Visual Hierarchy
- Use different node shapes to indicate different types
- Apply color coding for categories
- Use thicker arrows for primary flows
- Use dotted lines for optional/conditional flows

### 3. Layout Optimization
- Choose appropriate orientation (TB vs LR)
- Group related nodes together
- Use subgraphs for complex sections
- Maintain consistent spacing

### 4. Professional Styling
- Use consistent color schemes
- Apply brand colors when appropriate
- Ensure sufficient contrast
- Use professional, clean themes

### 5. Complex Diagrams
- Break large diagrams into smaller, focused ones
- Use subgraphs to group related components
- Add notes and annotations for clarity
- Consider using multiple diagram types for different perspectives

## Example: Complete System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Web[Web Browser]
        Mobile[Mobile App]
        Desktop[Desktop App]
    end

    subgraph "API Gateway Layer"
        Gateway[API Gateway]
        Auth[Authentication]
        RateLimit[Rate Limiter]
    end

    subgraph "Service Layer"
        UserService[User Service]
        OrderService[Order Service]
        PaymentService[Payment Service]
        NotificationService[Notification Service]
    end

    subgraph "Data Layer"
        UserDB[(User DB)]
        OrderDB[(Order DB)]
        Cache[(Redis Cache)]
        Queue[Message Queue]
    end

    subgraph "External Services"
        PaymentGateway[Payment Gateway]
        EmailService[Email Service]
        SMS[SMS Gateway]
    end

    Web --> Gateway
    Mobile --> Gateway
    Desktop --> Gateway

    Gateway --> Auth
    Gateway --> RateLimit

    Auth --> UserService
    RateLimit --> UserService
    RateLimit --> OrderService
    RateLimit --> PaymentService

    UserService --> UserDB
    OrderService --> OrderDB
    UserService --> Cache
    OrderService --> Cache

    PaymentService --> PaymentGateway
    PaymentService --> Queue

    Queue --> NotificationService
    NotificationService --> EmailService
    NotificationService --> SMS

    classDef client fill:#e1f5ff,stroke:#01579b
    classDef gateway fill:#fff3e0,stroke:#e65100
    classDef service fill:#f3e5f5,stroke:#4a148c
    classDef data fill:#e8f5e9,stroke:#1b5e20
    classDef external fill:#fce4ec,stroke:#880e4f

    class Web,Mobile,Desktop client
    class Gateway,Auth,RateLimit gateway
    class UserService,OrderService,PaymentService,NotificationService service
    class UserDB,OrderDB,Cache,Queue data
    class PaymentGateway,EmailService,SMS external
```

## Advanced Techniques

### Subgraphs for Grouping

```mermaid
graph TB
    subgraph Frontend
        A[React App]
        B[Vue App]
    end

    subgraph Backend
        C[Node.js API]
        D[Python Service]
    end

    A --> C
    B --> C
    C --> D
```

### Comments in Mermaid

```mermaid
graph LR
    A[Start] --> B[Process]
    %% This is a comment
    B --> C[End]
```

### Links and Interactions

```mermaid
graph LR
    A[GitHub] --> B[Documentation]
    click A "https://github.com" "Visit GitHub"
    click B "https://docs.example.com" "Read Docs"
```

## Common Issues and Solutions

1. **Diagram not rendering**: Check syntax, ensure proper spacing
2. **Arrows pointing wrong way**: Verify arrow direction syntax
3. **Labels overlapping**: Adjust node spacing or orientation
4. **Special characters**: Escape or use quotes for node labels
5. **Complex layouts**: Use subgraphs and manual node positioning

## Resources

- Official Mermaid Docs: https://mermaid.js.org/
- Live Editor: https://mermaid.live/
- Syntax Testing: Use the live editor to validate complex diagrams

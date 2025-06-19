HBnB Evolution - UML Documentation

#Project Overview
The goal of this project is to create comprehensive technical documentation which will serve as the foundation of our HBnB Evolution application.

**Current Phase:** Part 1 - Technical Documentation & UML Design

*Holberton School - Software Engineering Program*

---

#Problem Statement

In this project we are tasked with documenting the architecture and design of a simplified version of **HBnB Evolution**.

The users will be allowed to perform the following operations:

1. **User Management** - Users can register, update their profiles, and be identified as either regular users or administrators
2. **Place Management** - Users can list properties (places) they own, specifying details such as name, description, price, and location (latitude and longitude). Each place can also have a list of amenities
3. **Review Management** - Users can leave reviews for places they have visited, including a rating and a comment
4. **Amenity Management** - The application will manage amenities that can be associated with places

---

#Project Requirements

This project is divided into **4 main steps**:

#Step 1: Architecture Layers
Represent the architecture layers allowing the different components of the application to interact together through a **3-layer architecture**:
- **Presentation Layer**: API endpoints and services
- **Business Logic Layer**: Core models and business rules
- **Persistence Layer**: Database access and data management

#Step 2: Detailed Class Diagram for Business Logic Layer
Create and represent with a diagram the following objects of the business logic:

**User Entity**
- Each user has a first name, last name, email, and password
- Users can be identified as administrators through a boolean attribute
- Users should be able to register, update their profile information, and be deleted

**Place Entity**
- Each place has a title, description, price, latitude, and longitude
- Places are associated with the user who created them (owner)
- Places can have a list of amenities
- Places can be created, updated, deleted, and listed

**Review Entity**
- Each review is associated with a specific place and user, and includes a rating and comment
- Reviews can be created, updated, deleted, and listed by place

**Amenity Entity**
- Each amenity has a name and description
- Amenities can be created, updated, deleted, and listed

**Note:** Each object should be uniquely identified by an ID. For audit reasons, the creation and update datetime should be registered for all entities.

#Step 3: Sequence Diagrams for API Calls
Creation of 4 sequence diagrams for the following API calls:
- User registration
- Place creation
- Review submission
- Fetching a list of places

#Step 4: Documentation
Compilation of technical documentation gathering all the diagrams and notes created.

---

#Project Structure


holbertonschool-hbnb part1 UML Documentation
README.md               # This file

--------------diagrams--------------


package-diagram.md      # High-level architecture diagram
class-diagram.md        # Business logic class diagram
sequence-diagrams.md    # API interaction diagrams
documentation           # Compiled technical documentation


- **Package Diagram**: 3-layer architecture with Facade pattern
- **Class Diagram**: Detailed Business Logic layer (User, Place, Review, Amenity)
- **Sequence Diagrams**: 4 API call flows
- **Technical Documentation**: Comprehensive document compilation

---

#Resources and Tools

#Primary Tools Used
- **[Mermaid.js](https://mermaid.js.org/)** - Diagram creation and visualization
  - Used for all UML diagrams (Package, Class, Sequence)
  - Code-based diagram generation
  - Integration with GitHub/GitLab

#UML Documentation and Learning Resources

**UML Basics:**
- [OOP - Introduction to UML](https://example.com) - Fundamental UML concepts

**Package Diagrams:**
- [UML Package Diagram Overview](https://example.com)
- [UML Package Diagrams Guide](https://example.com)

**Class Diagrams:**
- [UML Class Diagram Tutorial](https://example.com)
- [How to Draw UML Class Diagrams](https://example.com)

**Sequence Diagrams:**
- [UML Sequence Diagram Tutorial](https://example.com)
- [Understanding Sequence Diagrams](https://example.com)

#Alternative Tools
- **[draw.io](https://app.diagrams.net/)** - Visual diagram editor
- **[Mermaid Live Editor](https://mermaid.live/)** - Online Mermaid testing and visualization

---

#Team and Contribution

#Team Members
This project is developed collaboratively by:
- **Dirimo IRIARTE PEREZ**
- **Nomen RATSIMBA**
- **Patrice BOLIN**

#Work Distribution
- **Architecture Design**: Collaborative planning of 3-layer structure
- **UML Diagrams**: Shared creation using Mermaid.js
- **Documentation**: Collective technical writing and review
- **Quality Assurance**: Peer review and validation

---

#License

This project is part of the Holberton School Software Engineering curriculum.

**Repository:** [holbertonschool-hbnb](https://github.com/Dirimo/holbertonschool-hbnb)  
**Project:** HBnB Evolution - Part 1 (UML Documentation)  
**School:** Holberton School

---

